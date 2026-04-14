"""
amcl_debug_visualizer.py
========================
ROS 2 debug node that subscribes to the AMCL particle cloud and the static
occupancy map and republishes several RViz-friendly visualisation topics:

  /amcl_debug/particles          – all (or top-N) particles as coloured arrows
  /amcl_debug/top_particles      – top-N particles as slightly larger arrows
  /amcl_debug/mean_pose          – weighted mean pose of the particle cloud
  /amcl_debug/distance_field     – Euclidean obstacle distance field from /map
  /amcl_debug/likelihood_field   – AMCL-style Gaussian likelihood from the
                                   distance field

Distance field vs likelihood field
------------------------------------
* The **distance field** stores, for every cell, the Euclidean distance (metres)
  to the nearest occupied cell, capped at `max_occ_dist`.  Cells far from any
  obstacle have value ≈ max_occ_dist; cells at an obstacle boundary have
  value ≈ 0.  We visualise this as a 0-100 occupancy-style grid so that the
  obstacle silhouette is clearly visible in RViz.

* The **likelihood field** applies a Gaussian to that distance:
      L(d) = exp( -d² / (2·σ²) )
  where σ = sigma_hit.  This is the same sensor model AMCL uses internally
  (nav2_amcl/src/sensors/laser/likelihood_field_model.cpp) to score each scan
  beam: beams that hit near an obstacle get high likelihood.  We publish it as
  an occupancy-style grid so you can visually confirm that the "expensive"
  likelihood region matches your map.

Why AMCL-*like* rather than pulling Nav2 internals
-----------------------------------------------------
Nav2 AMCL computes the sensor model on-demand inside the particle filter and
does not export its internal likelihood field or particle weights at the field
level.  The published /particle_cloud gives us the weights after resampling; the
map lets us recompute the sensor model independently.  This node therefore
replicates the maths from the published paper / Nav2 source externally so we
can visualise it without modifying Nav2.
"""

import math

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy

from geometry_msgs.msg import PoseStamped, Point, Vector3
from nav_msgs.msg import OccupancyGrid
from rcl_interfaces.srv import GetParameters
from std_msgs.msg import Header, ColorRGBA
from visualization_msgs.msg import Marker, MarkerArray

try:
    from nav2_msgs.msg import ParticleCloud
    _HAS_NAV2_MSGS = True
except ImportError:
    _HAS_NAV2_MSGS = False

# --------------------------------------------------------------------------- #
#  Optional SciPy – used for fast distance transform                          #
# --------------------------------------------------------------------------- #
try:
    from scipy.ndimage import distance_transform_edt as _scipy_edt
    _HAS_SCIPY = True
except ImportError:
    _scipy_edt = None
    _HAS_SCIPY = False


# --------------------------------------------------------------------------- #
#  Helpers                                                                     #
# --------------------------------------------------------------------------- #

def _weight_color(norm_w: float, alpha: float) -> ColorRGBA:
    """
    Map a normalized weight in [0,1] to an RGBA colour.

    Colour ramp:
        0.0  → blue   (0, 0, 1)
        0.5  → yellow (1, 1, 0)
        1.0  → red    (1, 0, 0)
    """
    c = ColorRGBA()
    c.a = float(alpha)
    if norm_w <= 0.5:
        t = norm_w * 2.0          # 0 → 1 across the blue-to-yellow half
        c.r = t
        c.g = t
        c.b = 1.0 - t
    else:
        t = (norm_w - 0.5) * 2.0  # 0 → 1 across the yellow-to-red half
        c.r = 1.0
        c.g = 1.0 - t
        c.b = 0.0
    return c


def _normalize_weights(weights: np.ndarray) -> np.ndarray:
    """
    Robustly normalize an array of particle weights to [0, 1].

    Handles:
      * all-equal weights  → uniform 0.5 (mid-scale so nothing is invisible)
      * all-zero weights   → uniform 0.5
      * single particle    → 1.0
    """
    if len(weights) == 0:
        return weights
    w_min = weights.min()
    w_max = weights.max()
    span = w_max - w_min
    if span < 1e-12:
        # All weights effectively equal – show uniform mid-colour
        return np.full_like(weights, 0.5)
    return (weights - w_min) / span


def _weighted_mean_pose(poses_xy: np.ndarray,
                        poses_yaw: np.ndarray,
                        weights: np.ndarray):
    """
    Compute the weighted mean of (x, y, yaw) given raw (un-normalized) weights.

    Yaw averaging uses the circular mean via sin/cos to avoid wrap-around
    artefacts.  Returns (x, y, yaw) as floats.
    """
    w_sum = weights.sum()
    if w_sum < 1e-12:
        # Degenerate – fall back to simple mean
        weights = np.ones_like(weights)
        w_sum = float(len(weights))

    mean_x = float((weights * poses_xy[:, 0]).sum() / w_sum)
    mean_y = float((weights * poses_xy[:, 1]).sum() / w_sum)
    # Circular mean for yaw
    mean_sin = float((weights * np.sin(poses_yaw)).sum() / w_sum)
    mean_cos = float((weights * np.cos(poses_yaw)).sum() / w_sum)
    mean_yaw = math.atan2(mean_sin, mean_cos)
    return mean_x, mean_y, mean_yaw


def _yaw_to_quaternion(yaw: float):
    """Return (qx, qy, qz, qw) for a rotation about Z by `yaw` radians."""
    half = yaw * 0.5
    return 0.0, 0.0, math.sin(half), math.cos(half)


def _parse_particle_cloud(msg):
    """
    Extract (poses_xy, poses_yaw, weights) from a nav2_msgs/ParticleCloud.

    Returns three numpy arrays, or (None, None, None) on failure.

    Defensive parsing notes
    -----------------------
    nav2_msgs/msg/ParticleCloud.particles is a list of
    nav2_msgs/msg/Particle which each have:
      - pose  : geometry_msgs/Pose
      - weight: float64

    We access fields by name and catch AttributeError so that if the message
    definition ever changes the node degrades gracefully rather than crashing.
    """
    particles = getattr(msg, 'particles', None)
    if not particles:
        return None, None, None

    xs, ys, yaws, ws = [], [], [], []
    for p in particles:
        try:
            pose = p.pose
            pos = pose.position
            ori = pose.orientation
            xs.append(pos.x)
            ys.append(pos.y)
            # Extract yaw from quaternion
            siny_cosp = 2.0 * (ori.w * ori.z + ori.x * ori.y)
            cosy_cosp = 1.0 - 2.0 * (ori.y * ori.y + ori.z * ori.z)
            yaws.append(math.atan2(siny_cosp, cosy_cosp))
            ws.append(float(p.weight))
        except AttributeError:
            continue

    if not xs:
        return None, None, None

    poses_xy = np.column_stack([xs, ys])
    poses_yaw = np.array(yaws, dtype=np.float64)
    weights = np.array(ws, dtype=np.float64)
    return poses_xy, poses_yaw, weights


def _compute_distance_field(occupancy_data: np.ndarray,
                             width: int,
                             height: int,
                             resolution: float,
                             occupied_threshold: int,
                             treat_unknown_as_occupied: bool,
                             max_occ_dist: float) -> np.ndarray:
    """
    Compute a Euclidean obstacle distance field in metres.

    Returns a float32 array of shape (height, width) where each element is the
    distance to the nearest occupied cell, capped at max_occ_dist.

    The occupancy grid is stored row-major with row 0 at minimum y (ROS
    convention).  The reshape preserves that ordering.

    SciPy path (preferred)
    ----------------------
    distance_transform_edt computes the exact Euclidean distance transform of
    a binary image.  Obstacles → 0 in the binary mask so their distance is 0;
    free cells → distance to nearest obstacle in pixels, scaled by resolution.

    NumPy fallback
    --------------
    A brute-force approach that works for small maps but degrades to O(N²)
    for large ones.  It iterates over BFS-style expanding distance shells using
    np.minimum and shifted arrays.  Correct, readable, slow for large maps.
    """
    # ---------- Build binary obstacle mask -------------------------------- #
    grid = occupancy_data.reshape((height, width)).astype(np.int16)

    obstacle = np.zeros((height, width), dtype=bool)
    # Occupied: value >= occupied_threshold (and not -1)
    obstacle |= (grid >= occupied_threshold)
    if treat_unknown_as_occupied:
        obstacle |= (grid < 0)

    # ------------------------------------------------------------------ #
    if _HAS_SCIPY:
        # distance_transform_edt: distance in pixels of each non-obstacle cell
        # from the nearest obstacle cell – we want distance OF free cells FROM
        # obstacles, so we pass ~obstacle (True = background pixel).
        dist_pixels = _scipy_edt(~obstacle)           # float64, shape (H,W)
        dist_m = dist_pixels.astype(np.float32) * resolution
    else:
        # --- NumPy fallback: propagate distances using repeated dilation --- #
        # This is a simplified multi-pass distance fill, not a true EDT.
        # Each iteration propagates "1 pixel" outwards from obstacles,
        # so it computes the taxicab / L-inf distance rather than Euclidean.
        # For short max_occ_dist values this is adequate.
        dist_m = np.full((height, width), np.inf, dtype=np.float32)
        dist_m[obstacle] = 0.0
        step = resolution
        for _ in range(int(math.ceil(max_occ_dist / resolution)) + 1):
            # Propagate to 4-connected neighbours
            updated = dist_m.copy()
            updated[1:, :] = np.minimum(updated[1:, :],  dist_m[:-1, :] + step)
            updated[:-1, :] = np.minimum(updated[:-1, :], dist_m[1:, :] + step)
            updated[:, 1:] = np.minimum(updated[:, 1:],  dist_m[:, :-1] + step)
            updated[:, :-1] = np.minimum(updated[:, :-1], dist_m[:, 1:] + step)
            if np.allclose(dist_m, updated, atol=1e-6):
                break
            dist_m = updated

    # Cap at max_occ_dist
    dist_m = np.minimum(dist_m, max_occ_dist)
    return dist_m


def _distance_field_to_occupancy(dist_m: np.ndarray,
                                  max_occ_dist: float) -> np.ndarray:
    """
    Convert a float distance field (metres) to a 0-100 occupancy-style grid
    suitable for nav_msgs/OccupancyGrid data.

    Encoding (intuitive in RViz with default costmap colour scheme):
      0   = nearest to obstacle  → darkest / most "dangerous"
      100 = furthest from obstacle → lightest / "safest"

    This is inverted (high value = far) so that in RViz the map looks
    "bright" in free space and "dark" near obstacles, which matches how
    people think about distance fields for localization.

    If you prefer the opposite, swap the subtraction below.
    """
    if max_occ_dist < 1e-6:
        return np.zeros_like(dist_m, dtype=np.int8)
    norm = np.clip(dist_m / max_occ_dist, 0.0, 1.0)   # 0 (obstacle) → 1 (far)
    # Invert so 0 = near obstacle = high value in RViz
    vis = ((1.0 - norm) * 100.0).astype(np.int8)
    return vis


def _likelihood_field_to_occupancy(dist_m: np.ndarray,
                                    sigma_hit: float) -> np.ndarray:
    """
    L(d) = exp( -d² / (2·σ²) )   then scaled to 0-100.

    High value (bright in RViz) = high likelihood = near obstacle.
    """
    likelihood = np.exp(-0.5 * (dist_m / sigma_hit) ** 2)
    vis = (likelihood * 100.0).clip(0, 100).astype(np.int8)
    return vis


def _make_grid_msg(header: Header,
                   map_msg: OccupancyGrid,
                   data: np.ndarray) -> OccupancyGrid:
    """
    Pack a 2-D int8 array into an OccupancyGrid message, preserving the
    metadata from the original /map message exactly.
    """
    out = OccupancyGrid()
    out.header = header
    out.info = map_msg.info          # width, height, resolution, origin
    out.data = data.flatten().tolist()
    return out


# --------------------------------------------------------------------------- #
#  Node                                                                        #
# --------------------------------------------------------------------------- #

class AmclDebugVisualizer(Node):
    """
    Publishes AMCL debug visualisations for RViz.

    Topics published
    ----------------
    /amcl_debug/particles        MarkerArray   – arrows per particle, heat-map colour
    /amcl_debug/top_particles    MarkerArray   – top-N particles, slightly larger
    /amcl_debug/mean_pose        PoseStamped   – weighted mean of particles
    /amcl_debug/distance_field   OccupancyGrid – obstacle distance field from /map
    /amcl_debug/likelihood_field OccupancyGrid – AMCL-style Gaussian likelihood
    """

    def __init__(self):
        super().__init__('amcl_debug_visualizer')

        # ------------------------------------------------------------------ #
        #  Parameters                                                         #
        # ------------------------------------------------------------------ #
        # map_topic: leave empty ('') to auto-read from the AMCL node's
        # own parameter service at startup.  Set a non-empty string to
        # hard-code the topic and skip the auto-detect step.
        self.declare_parameter('map_topic',                   '')
        self.declare_parameter('amcl_node_name',              'amcl')
        self.declare_parameter('particle_topic',              '/particle_cloud')
        self.declare_parameter('particles_marker_topic',      '/amcl_debug/particles')
        self.declare_parameter('top_particles_marker_topic',  '/amcl_debug/top_particles')
        self.declare_parameter('mean_pose_topic',             '/amcl_debug/mean_pose')
        self.declare_parameter('distance_field_topic',        '/amcl_debug/distance_field')
        self.declare_parameter('likelihood_field_topic',      '/amcl_debug/likelihood_field')

        self.declare_parameter('occupied_threshold',          65)
        self.declare_parameter('treat_unknown_as_occupied',   False)
        self.declare_parameter('max_occ_dist',                2.0)
        self.declare_parameter('sigma_hit',                   0.2)

        self.declare_parameter('show_all_particles',          True)
        self.declare_parameter('top_n_particles',             50)
        self.declare_parameter('use_weight_scaled_size',      True)
        self.declare_parameter('particle_scale_min',          0.03)
        self.declare_parameter('particle_scale_max',          0.15)
        self.declare_parameter('particle_arrow_length',       0.18)
        self.declare_parameter('particle_arrow_width',        0.008)  # shaft diameter in metres
        self.declare_parameter('marker_alpha',                0.85)
        self.declare_parameter('publish_on_particle_update_only', True)

        p = self.get_parameters_by_prefix('')  # read-back convenience below

        def _p(name):
            return self.get_parameter(name).value

        # ------------------------------------------------------------------ #
        #  State                                                               #
        # ------------------------------------------------------------------ #
        self._map_msg: OccupancyGrid | None = None
        self._dist_field: np.ndarray | None = None   # cached distance field
        self._last_particle_count: int = 0            # for DELETE marker sweep
        self._warned_uniform_weights: bool = False
        self._warned_no_map: bool = False
        self._map_sub = None          # created after map topic is resolved
        self._param_client = None     # AsyncParametersClient to AMCL node
        self._resolved_map_topic: str = ''

        if not _HAS_SCIPY:
            self.get_logger().warning(
                'SciPy not found – distance field will use slower NumPy fallback '
                '(taxicab approximation). Install scipy for exact Euclidean EDT.')

        if not _HAS_NAV2_MSGS:
            self.get_logger().error(
                'nav2_msgs not importable – particle cloud subscription disabled. '
                'Install ros-<distro>-nav2-msgs.')

        # ------------------------------------------------------------------ #
        #  QoS – map is latched (transient_local)                             #
        # ------------------------------------------------------------------ #
        self._map_qos = QoSProfile(
            depth=1,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
        )
        best_effort_qos = QoSProfile(
            depth=10,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE,
        )

        # ------------------------------------------------------------------ #
        #  Map topic resolution                                                #
        # ------------------------------------------------------------------ #
        # If map_topic is explicitly set, subscribe immediately.
        # Otherwise poll AMCL's parameter service every 0.5 s until it
        # responds, then subscribe to whatever it says.
        override = _p('map_topic').strip()
        if override:
            self._start_map_subscription(override)
        else:
            self._setup_timer = self.create_timer(0.5, self._try_resolve_map_topic)

        if _HAS_NAV2_MSGS:
            self._particle_sub = self.create_subscription(
                ParticleCloud,
                _p('particle_topic'),
                self._particle_callback,
                best_effort_qos,
            )

        # Placeholder for future /scan subscription
        # self._scan_sub = self.create_subscription(LaserScan, '/scan', ...)

        # ------------------------------------------------------------------ #
        #  Publishers                                                          #
        # ------------------------------------------------------------------ #
        self._particle_pub = self.create_publisher(
            MarkerArray, _p('particles_marker_topic'), 10)
        self._top_particle_pub = self.create_publisher(
            MarkerArray, _p('top_particles_marker_topic'), 10)
        self._mean_pose_pub = self.create_publisher(
            PoseStamped, _p('mean_pose_topic'), 10)
        # TRANSIENT_LOCAL so RViz gets the last field immediately on connect,
        # matching the behaviour of the map_server's /map publisher.
        latched_qos = QoSProfile(
            depth=1,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
        )
        self._dist_field_pub = self.create_publisher(
            OccupancyGrid, _p('distance_field_topic'), latched_qos)
        self._likelihood_pub = self.create_publisher(
            OccupancyGrid, _p('likelihood_field_topic'), latched_qos)

        # ------------------------------------------------------------------ #
        #  Optional timer-based republish                                      #
        # ------------------------------------------------------------------ #
        if not _p('publish_on_particle_update_only'):
            self._timer = self.create_timer(0.5, self._timer_callback)
        else:
            self._timer = None

        self.get_logger().info(
            f'amcl_debug_visualizer started. '
            f'Particle topic: "{_p("particle_topic")}"')

    # ---------------------------------------------------------------------- #
    #  Map topic resolution – reads map_topic from AMCL parameter service    #
    # ---------------------------------------------------------------------- #
    def _try_resolve_map_topic(self) -> None:
        """
        Timer callback (0.5 s interval) that polls AMCL's GetParameters service
        until it is ready, then requests the 'map_topic' parameter value and
        cancels itself.  Called only when map_topic was not explicitly set.

        Uses rcl_interfaces/srv/GetParameters directly – compatible with
        ROS 2 Humble (rclpy.parameter_client does not exist until Iron).
        """
        amcl_name = self.get_parameter('amcl_node_name').value

        if self._param_client is None:
            self._param_client = self.create_client(
                GetParameters, f'/{amcl_name}/get_parameters')

        if not self._param_client.service_is_ready():
            self.get_logger().info(
                f'Waiting for AMCL node "{amcl_name}" parameter service…',
                throttle_duration_sec=5.0)
            return

        # Service is up – fire the request and stop the timer so we don't
        # send duplicate requests while waiting for the response.
        self._setup_timer.cancel()
        req = GetParameters.Request()
        req.names = ['map_topic']
        future = self._param_client.call_async(req)
        future.add_done_callback(self._on_amcl_map_topic)

    def _on_amcl_map_topic(self, future) -> None:
        """Called when the GetParameters response arrives."""
        try:
            response = future.result()
            # response.values is a list of rcl_interfaces/msg/ParameterValue
            # .string_value holds the value when type == ParameterType.PARAMETER_STRING
            map_topic = response.values[0].string_value if response.values else ''
        except Exception as exc:
            self.get_logger().warning(
                f'Failed to read map_topic from AMCL parameter service: {exc}. '
                f'Falling back to "/map".')
            map_topic = ''

        if not map_topic:
            map_topic = '/map'
            self.get_logger().warning(
                f'AMCL returned an empty map_topic; falling back to "{map_topic}".')

        self._start_map_subscription(map_topic)

    def _start_map_subscription(self, map_topic: str) -> None:
        """Create the /map subscription once the topic name is known."""
        if self._map_sub is not None:
            return  # already subscribed (e.g. explicit override)
        self._resolved_map_topic = map_topic
        self.get_logger().info(
            f'Subscribing to map on "{map_topic}" (RELIABLE + TRANSIENT_LOCAL).')
        self._map_sub = self.create_subscription(
            OccupancyGrid,
            map_topic,
            self._map_callback,
            self._map_qos,
        )

    # ---------------------------------------------------------------------- #
    #  Map callback                                                            #
    # ---------------------------------------------------------------------- #
    def _map_callback(self, msg: OccupancyGrid) -> None:
        if msg.info.width == 0 or msg.info.height == 0:
            self.get_logger().warning('Received empty map (width or height is 0) – ignoring.')
            return

        self._map_msg = msg
        self.get_logger().info(
            f'Map received: {msg.info.width}×{msg.info.height}, '
            f'res={msg.info.resolution:.4f} m/cell, frame={msg.header.frame_id}')

        self._recompute_map_fields()

    def _recompute_map_fields(self) -> None:
        """Compute distance field and likelihood field from the stored map."""
        msg = self._map_msg
        if msg is None:
            return

        occupied_threshold      = self.get_parameter('occupied_threshold').value
        treat_unknown_as_occupied = self.get_parameter('treat_unknown_as_occupied').value
        max_occ_dist            = self.get_parameter('max_occ_dist').value
        sigma_hit               = self.get_parameter('sigma_hit').value

        data = np.array(msg.data, dtype=np.int16)
        dist_m = _compute_distance_field(
            data,
            msg.info.width,
            msg.info.height,
            msg.info.resolution,
            occupied_threshold,
            treat_unknown_as_occupied,
            max_occ_dist,
        )
        self._dist_field = dist_m

        now = self.get_clock().now().to_msg()
        header = Header()
        header.stamp = now
        header.frame_id = msg.header.frame_id

        # ---- Distance field publication ---------------------------------- #
        df_data = _distance_field_to_occupancy(dist_m, max_occ_dist)
        df_msg = _make_grid_msg(header, msg, df_data)
        self._dist_field_pub.publish(df_msg)

        # ---- Likelihood field publication --------------------------------- #
        if sigma_hit <= 0.0:
            self.get_logger().warning(
                f'sigma_hit={sigma_hit} is not positive – skipping likelihood field.')
        else:
            lf_data = _likelihood_field_to_occupancy(dist_m, sigma_hit)
            lf_msg = _make_grid_msg(header, msg, lf_data)
            self._likelihood_pub.publish(lf_msg)

    # ---------------------------------------------------------------------- #
    #  Particle callback                                                       #
    # ---------------------------------------------------------------------- #
    def _particle_callback(self, msg) -> None:
        poses_xy, poses_yaw, weights = _parse_particle_cloud(msg)

        if poses_xy is None:
            self.get_logger().warning(
                'Received particle cloud with no parseable particles – ignoring.')
            return

        # One-shot warning if the map hasn't arrived yet.
        if self._map_msg is None and not self._warned_no_map:
            if self._resolved_map_topic:
                self.get_logger().warning(
                    f'Particle cloud received but no map yet on "{self._resolved_map_topic}". '
                    f'Distance/likelihood fields will publish once the map arrives.')
            else:
                self.get_logger().warning(
                    'Particle cloud received but map topic not resolved yet. '
                    'Still waiting for AMCL parameter service response.')
            self._warned_no_map = True

        n = len(weights)
        frame_id = getattr(msg, 'header', None)
        frame_id = frame_id.frame_id if frame_id else 'map'
        stamp = getattr(getattr(msg, 'header', None), 'stamp', self.get_clock().now().to_msg())

        norm_w = _normalize_weights(weights)

        # ---- Uniform-weight detection ------------------------------------ #
        # Nav2 AMCL publishes the particle cloud POST-resampling.  After
        # resampling the weights are reset to 1/N (all equal), so the raw
        # weight field gives no colour variation.
        # Fallback: colour by distance from the spatial mean.
        #   near mean = 1.0 → red  (tight, confident cluster)
        #   far from mean = 0.0 → blue  (spread / outlier)
        w_span = float(weights.max() - weights.min())
        if w_span < 1e-12 and len(weights) > 1:
            if not self._warned_uniform_weights:
                self.get_logger().warning(
                    'All particle weights are equal (AMCL resets weights to 1/N '
                    'after resampling). Falling back to colouring by distance '
                    'from the mean pose.')
                self._warned_uniform_weights = True
            mean_x = float(poses_xy[:, 0].mean())
            mean_y = float(poses_xy[:, 1].mean())
            dists = np.hypot(poses_xy[:, 0] - mean_x, poses_xy[:, 1] - mean_y)
            max_d = float(dists.max())
            if max_d > 1e-6:
                norm_w = 1.0 - np.clip(dists / max_d, 0.0, 1.0)
            # else: all particles at the same point – uniform red is fine
        else:
            self._warned_uniform_weights = False  # weights vary again, reset flag

        # ---- Publish all (or top-N) particles ----------------------------- #
        show_all     = self.get_parameter('show_all_particles').value
        top_n        = self.get_parameter('top_n_particles').value

        if show_all:
            indices_all = np.arange(n)
        else:
            # Sort descending by weight, take top_n
            indices_all = np.argsort(weights)[::-1][:top_n]

        top_indices = np.argsort(weights)[::-1][:top_n]

        all_markers  = self._make_particle_markers(
            indices_all, poses_xy, poses_yaw, norm_w, stamp, frame_id,
            ns='particles', scale_multiplier=1.0)
        top_markers  = self._make_particle_markers(
            top_indices, poses_xy, poses_yaw, norm_w, stamp, frame_id,
            ns='top_particles', scale_multiplier=1.4)

        # Delete stale markers from the previous update to avoid ghost arrows
        # when particle count decreases.  RViz respects DELETE + ADD in the
        # same MarkerArray message.
        prev_count = self._last_particle_count
        all_array  = self._wrap_with_deletes(all_markers,  prev_count, 'particles')
        top_array  = self._wrap_with_deletes(top_markers,  prev_count, 'top_particles')
        self._last_particle_count = n

        self._particle_pub.publish(all_array)
        self._top_particle_pub.publish(top_array)

        # ---- Publish weighted mean pose ----------------------------------- #
        mx, my, myaw = _weighted_mean_pose(poses_xy, poses_yaw, weights)
        qx, qy, qz, qw = _yaw_to_quaternion(myaw)

        ps = PoseStamped()
        ps.header.stamp = stamp
        ps.header.frame_id = frame_id
        ps.pose.position.x = mx
        ps.pose.position.y = my
        ps.pose.position.z = 0.0
        ps.pose.orientation.x = qx
        ps.pose.orientation.y = qy
        ps.pose.orientation.z = qz
        ps.pose.orientation.w = qw
        self._mean_pose_pub.publish(ps)

    # ---------------------------------------------------------------------- #
    #  Marker construction helpers                                             #
    # ---------------------------------------------------------------------- #
    def _make_particle_markers(self,
                                indices: np.ndarray,
                                poses_xy: np.ndarray,
                                poses_yaw: np.ndarray,
                                norm_w: np.ndarray,
                                stamp,
                                frame_id: str,
                                ns: str,
                                scale_multiplier: float) -> list:
        """Build a list of ARROW Marker objects for the given particle indices."""
        use_weight_scale = self.get_parameter('use_weight_scaled_size').value
        scale_min        = self.get_parameter('particle_scale_min').value
        scale_max        = self.get_parameter('particle_scale_max').value
        arrow_length     = self.get_parameter('particle_arrow_length').value
        arrow_width      = self.get_parameter('particle_arrow_width').value
        alpha            = self.get_parameter('marker_alpha').value

        # Two-point ARROW marker scale convention in RViz:
        #   scale.x = shaft diameter   ← keep this thin (arrow_width)
        #   scale.y = arrowhead diam   ← ~2.5x shaft looks natural
        #   scale.z = arrowhead length (0 = auto, ~30% of total arrow)
        # Weight scaling affects arrow LENGTH, not thickness, so heading
        # is always readable regardless of weight.
        shaft = arrow_width * scale_multiplier
        head_diam = shaft * 2.5

        markers = []
        for marker_id, idx in enumerate(indices):
            nw = float(norm_w[idx])

            # Weight-scaled arrow LENGTH in metres.
            # scale_min/max are absolute lengths so short = low weight.
            if use_weight_scale:
                length = (scale_min + nw * (scale_max - scale_min)) * scale_multiplier
            else:
                length = arrow_length * scale_multiplier

            m = Marker()
            m.header.stamp    = stamp
            m.header.frame_id = frame_id
            m.ns              = ns
            m.id              = marker_id   # deterministic ID based on position in array
            m.type            = Marker.ARROW
            m.action          = Marker.ADD  # ADD replaces any existing marker with same ns+id

            # Arrow defined by two points: tail → head
            x, y   = float(poses_xy[idx, 0]), float(poses_xy[idx, 1])
            yaw    = float(poses_yaw[idx])
            tail   = Point(x=x, y=y, z=0.0)
            head   = Point(
                x=x + length * math.cos(yaw),
                y=y + length * math.sin(yaw),
                z=0.0,
            )
            m.points = [tail, head]

            m.scale = Vector3(x=shaft, y=head_diam, z=0.0)
            m.color = _weight_color(nw, alpha)
            m.lifetime.sec = 0  # 0 = persistent (until explicitly deleted)

            markers.append(m)

        return markers

    def _wrap_with_deletes(self,
                            new_markers: list,
                            prev_count: int,
                            ns: str) -> MarkerArray:
        """
        Return a MarkerArray that:
          1. Deletes any markers with IDs in [len(new_markers), prev_count)
             so that shrinking clouds don't leave ghost arrows.
          2. Appends all ADD markers from new_markers.

        RViz processes the message sequentially, so DELETEs before ADDs is safe.
        """
        array = MarkerArray()
        new_count = len(new_markers)

        # Emit DELETE markers for any IDs that no longer exist
        if prev_count > new_count:
            dummy_stamp = self.get_clock().now().to_msg()
            for stale_id in range(new_count, prev_count):
                dm = Marker()
                dm.ns     = ns
                dm.id     = stale_id
                dm.action = Marker.DELETE
                dm.header.stamp    = dummy_stamp
                dm.header.frame_id = 'map'
                array.markers.append(dm)

        array.markers.extend(new_markers)
        return array

    # ---------------------------------------------------------------------- #
    #  Timer callback – republish last known data at fixed rate               #
    # ---------------------------------------------------------------------- #
    def _timer_callback(self) -> None:
        """Republish cached map fields at a fixed rate (non-particle-driven mode)."""
        if self._dist_field is not None and self._map_msg is not None:
            self._recompute_map_fields()


# --------------------------------------------------------------------------- #
#  Entry point                                                                 #
# --------------------------------------------------------------------------- #

def main(args=None):
    rclpy.init(args=args)
    node = AmclDebugVisualizer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
