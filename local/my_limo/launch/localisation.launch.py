import os

from launch import LaunchDescription
from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    bringup_dir = get_package_share_directory('my_limo')
    params_file = os.path.join(bringup_dir, 'config', 'amcl_params.yml'),

    remappings = [('/tf', 'tf'),
                  ('/tf_static', 'tf_static')]

    amcl_node = Node(
        package="nav2_amcl",
        executable="amcl",
        name="amcl",
        output="screen",
        parameters=[params_file],
        remappings=remappings
    )

    lifecycle_mgr = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_amcl",
        output="screen",
        parameters=[{
            "autostart": True,
            "node_names": ["amcl"]
        }],
    )

    return LaunchDescription([
        amcl_node,
        lifecycle_mgr
    ])
