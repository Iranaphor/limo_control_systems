FROM ros:humble

ARG DEBIAN_FRONTEND=noninteractive
ARG USERNAME=ros
ARG UID=1000
ARG GID=1000

ENV WS=/home/${USERNAME}/ros2_ws
ENV ROS_WS=${WS}
ENV ROS_DISTRO=humble
ENV PIP_BREAK_SYSTEM_PACKAGES=1

SHELL ["/bin/bash", "-c"]

# Base OS tools + ROS testing repo
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    sudo \
    git \
    nano \
    bash-completion \
    build-essential \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-rosdep-modules \
    tmux \
    && curl -fsSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
      | gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2-testing/ubuntu $(lsb_release -cs) main" \
      > /etc/apt/sources.list.d/ros2-testing.list \
    && apt-get update \
    && rm -rf /var/lib/apt/lists/*

# Create user
RUN (getent group ${GID} >/dev/null || groupadd -g ${GID} ${USERNAME}) \
    && (id -u ${USERNAME} >/dev/null 2>&1 || useradd -m -u ${UID} -g ${GID} -s /bin/bash ${USERNAME}) \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
    && groupadd -f dialout \
    && usermod -aG dialout ${USERNAME}

# Workspace layout
RUN mkdir -p ${ROS_WS}/src/external ${ROS_WS}/src/local \
    && mkdir -p /home/${USERNAME}/.colcon \
    && chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}

# Copy workspace sources so rosdep/package discovery works at build time
COPY external/ ${ROS_WS}/src/external/
COPY local/ ${ROS_WS}/src/local/

# Copy helper scripts
COPY start.sh /home/${USERNAME}/start.sh
COPY bash_aliases.sh /home/${USERNAME}/.bash_aliases.sh

RUN chmod +x /home/${USERNAME}/start.sh \
    && chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}

# Python packages installed once at build time
RUN python3 -m pip install --no-cache-dir --upgrade pip wheel "setuptools<75" \
    && python3 -m pip install --no-cache-dir tmule

# Initialize rosdep and install workspace dependencies, skipping gazebo rosdeps
RUN rosdep init 2>/dev/null || true \
    && rosdep fix-permissions \
    && rosdep update \
    && apt-get update \
    && source /opt/ros/${ROS_DISTRO}/setup.bash \
    && rosdep install \
         --from-paths ${ROS_WS}/src \
         --ignore-src \
         -r -y \
         --rosdistro ${ROS_DISTRO} \
         --skip-keys="gazebo_ros gazebo_plugins" \
    && rm -rf /var/lib/apt/lists/*

USER ${USERNAME}
WORKDIR ${ROS_WS}

# Build workspace once during image build
RUN source /opt/ros/${ROS_DISTRO}/setup.bash \
    && colcon build \
         --symlink-install \
         --packages-skip \
           ydlidar_ros2_driver \
           limo_gazebosim \
           limo_speaker \
           voice_control \
           astra_camera

# Shell niceties
RUN sed -i 's/^#\(force_color_prompt\)/\1/' /home/${USERNAME}/.bashrc \
    && grep -qxF 'source ~/.bash_aliases.sh' /home/${USERNAME}/.bashrc || echo 'source ~/.bash_aliases.sh' >> /home/${USERNAME}/.bashrc \
    && grep -qxF "source /opt/ros/${ROS_DISTRO}/setup.bash" /home/${USERNAME}/.bashrc || echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> /home/${USERNAME}/.bashrc \
    && grep -qxF "source ${ROS_WS}/install/setup.bash" /home/${USERNAME}/.bashrc || echo "source ${ROS_WS}/install/setup.bash" >> /home/${USERNAME}/.bashrc


CMD ["/bin/bash"]
