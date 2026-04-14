import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():

    # bringup_dir = get_package_share_directory('my_limo')
    bringup_src = os.path.join('/home/ros/ros2_ws', 'src', 'local/my_limo')
    default_params_file = os.path.join(bringup_src, 'config', 'amcl_experiments', 'amcl_params_baseline.yml')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    declare_params_file_arg = DeclareLaunchArgument(
        'params_file',
        default_value=default_params_file,
        description='Absolute path to the AMCL params YAML file'
    )
    declare_use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation/rosbag clock when true'
    )

    remappings = [('/tf', 'tf'),
                  ('/tf_static', 'tf_static')]

    amcl_node = Node(
        package="nav2_amcl",
        executable="amcl",
        name="amcl",
        output="screen",
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        remappings=remappings
    )

    lifecycle_mgr = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_amcl",
        output="screen",
        parameters=[{
            "use_sim_time": use_sim_time,
            "autostart": True,
            "node_names": ["amcl"]
        }],
    )

    amcl_debug_node = Node(
        package='my_limo',
        executable='amcl_debug_visualizer',
        name='amcl_debug_visualizer',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )

    return LaunchDescription([
        declare_params_file_arg,
        declare_use_sim_time_arg,
        amcl_node,
        lifecycle_mgr,
        # amcl_debug_node,
    ])
