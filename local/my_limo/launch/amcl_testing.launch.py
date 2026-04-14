import os

from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    bringup_src = os.path.join('/home/ros/ros2_ws', 'src', 'local/my_limo')
       

    rviz_file = os.path.join(bringup_src, 'config', 'topomap_marker.rviz')
    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_file],
        output='screen'
    )
    # tf_tree = Node(
    #     package='rqt_tf_tree',
    #     executable='rqt_tf_tree',
    #     output='screen'
    # )
    reconfigure = Node(
        package='rqt_reconfigure',
        executable='rqt_reconfigure',
        arguments=['--force-discover'],
        output='screen'
    )


    amcl_params = os.path.join(bringup_src, 'config', 'amcl_experiments')
    ## params_file = os.path.join(amcl_params, 'amcl_params_baseline.yml')
    ## params_file = os.path.join(amcl_params, 'amcl_params_v1_update_particles.yml')
    ## params_file = os.path.join(amcl_params, 'amcl_params_v2_skid_motion.yml')
    ## params_file = os.path.join(amcl_params, 'amcl_params_v3_sensor_robust.yml')
    ## params_file = os.path.join(amcl_params, 'amcl_params_v4_sensor_sharp.yml')
    ## params_file = os.path.join(amcl_params, 'amcl_params_v5_recovery_enabled.yml') #wtf???
    ## params_file = os.path.join(amcl_params, 'amcl_params_v6_high_search.yml') #wtf???
    ## params_file = os.path.join(amcl_params, 'amcl_params_v6_high_search.yml') #wtf???
    ## params_file = os.path.join(amcl_params, 'amcl_params_v7_anchor_low_drift.yml')
    ## params_file = os.path.join(amcl_params, 'amcl_params_v8_rotation_balance.yml')
    ## params_file = os.path.join(amcl_params, 'amcl_params_v9_clutter_beamskip.yml')
    ## params_file = os.path.join(amcl_params, 'amcl_params_v10_yaw_trim_minus8deg.yml') #nope
    ## params_file = os.path.join(amcl_params, 'amcl_params_v11_yaw_trim_plus8deg.yml')
    ## params_file = os.path.join(amcl_params, 'amcl_params_v12_dynamic_robust.yml')
    #params_file = os.path.join(amcl_params, 'amcl_params_v13_translation_hold.yml')
    ## params_file = os.path.join(amcl_params, 'amcl_params_v14_slow_phase_stable.yml')
    ## params_file = os.path.join(amcl_params, 'amcl_params_v15_rotlock.yml')
    ## params_file = os.path.join(amcl_params, 'amcl_params_v16_mild_recovery.yml')
    # params_file = os.path.join(amcl_params, 'amcl_params_v17_low_jitter.yml')
    #params_file = os.path.join(amcl_params, 'amcl_params_v18_many_particles.yml')
    params_file = os.path.join(amcl_params, 'amcl_params_v19_sharp_map_match.yml')
    # params_file = os.path.join(amcl_params, 'amcl_params_v20_dense_scan_evidence.yml')
    localisation_launch_file = os.path.join(bringup_src, 'launch', 'localisation.launch.py')
    localisation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(localisation_launch_file),
        launch_arguments={
            'params_file': params_file,
            'use_sim_time': 'true'
        }.items()
    )



    common_src = os.path.join('/home/ros/ros2_ws', 'src', 'external/environment_common')
    environment_params_file = os.path.join(common_src, 'config', 'params_map_server.yaml')
    environment_launch_file = os.path.join(common_src, 'launch', 'environment.launch.py')

    # -----------------------------------------------------------------------
    # CHANGE THIS to switch which map AMCL localises against.
    # The keepout_mask_server will publish this file as /keepout_mask.
    # Must be an absolute path to a valid map.yaml inside the container.
    # Default points to the SLAM-built occupancy grid used for localisation.
    # -----------------------------------------------------------------------
    env_template_src = os.path.join('/home/ros/ros2_ws', 'src', 'external/environment_template')
    nogomap_yaml = os.path.join(env_template_src, 'config', 'metric', 'nogo', 'map.yaml')

    environment = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(environment_launch_file),
        launch_arguments={
            'params_file': environment_params_file,
            'nogomap': nogomap_yaml,
            'use_rviz': 'false',
            'use_sim_time': 'true'
        }.items()
    )



    rosbag2_dir = os.path.join(bringup_src, 'tmule', 'rosbags', 'rosbag2_2026_04_09-08_11_32')
    topic_list = [
        "/scan", "/imu", "/odom", "/tf", "/tf_static"
    ]
    rosbag_play = ExecuteProcess(
        cmd=["ros2", "bag", "play", rosbag2_dir, "--clock", "--topics", *topic_list],
        output="screen"
    )



    output_bag_name = os.path.splitext(os.path.basename(params_file))[0]
    output_bag_path = os.path.join(bringup_src, 'tmule', 'rosbags', output_bag_name)
    rosbag_record = ExecuteProcess(
        cmd=['ros2', 'bag', 'record', '/amcl_pose', '/particle_cloud', '-o', output_bag_path],
        output='screen'
    )


    # Delay AMCL startup so keepout_mask_server is fully active and has
    # published /keepout_mask before AMCL subscribes. Without this, the two
    # lifecycle managers race and AMCL may miss the TRANSIENT_LOCAL map message.
    delayed_localisation = TimerAction(period=5.0, actions=[localisation])

    return LaunchDescription([
        rviz2,
        # tf_tree,
        reconfigure,
        environment,
        rosbag_play,
        rosbag_record,
        delayed_localisation,
    ])

