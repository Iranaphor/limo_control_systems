import os

from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    bringup_src = os.path.join('/home/ros/ros2_ws', 'src', 'local/my_limo')
    rviz_file = os.path.join(bringup_src, 'config', 'topomap_marker.rviz')
    rosbag2_dir = os.path.join(bringup_src, 'tmule', 'rosbags', 'rosbag2_2026_04_09-08_11_32')
    localisation_launch_file = os.path.join(bringup_src, 'launch', 'localisation.launch.py')

    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_file],
        output='screen'
    )

    tf_tree = Node(
        package='rqt_tf_tree',
        executable='rqt_tf_tree',
        output='screen'
    )

    reconfigure = Node(
        package='rqt_reconfigure',
        executable='rqt_reconfigure',
        arguments=['--force-discover'],
        output='screen'
    )

    rosbag_play = ExecuteProcess(
        cmd=['ros2', 'bag', 'play', rosbag2_dir],
        output='screen'
    )

    localisation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(localisation_launch_file)
    )

    return LaunchDescription([
        rviz2,
        tf_tree,
        reconfigure,
        rosbag_play,
        localisation,
    ])

