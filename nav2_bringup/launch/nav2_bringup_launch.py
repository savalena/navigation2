import os
from launch import LaunchDescription
import launch.actions
import launch_ros.actions

def generate_launch_description():
    map_file = launch.substitutions.LaunchConfiguration('map')
    map_type = launch.substitutions.LaunchConfiguration('map_type', default='occupancy')
    use_sim_time = launch.substitutions.LaunchConfiguration('use_sim_time', default='false')
    params_file = launch.substitutions.LaunchConfiguration('params', default='nav2_params.yaml')

    return LaunchDescription([
        launch.actions.DeclareLaunchArgument(
            'map', description='Full path to map file to load'),
        launch.actions.DeclareLaunchArgument(
            'map_type', default_value='occupancy', description='Type of map to load'),
        launch.actions.DeclareLaunchArgument(
            'use_sim_time', default_value='false', description='Use simulation (Gazebo) clock if true'),

        launch_ros.actions.Node(
            package='tf2_ros',
            node_executable='static_transform_publisher',
            output='screen',
            arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'base_footprint']),

        launch_ros.actions.Node(
            package='tf2_ros',
            node_executable='static_transform_publisher',
            output='screen',
            arguments=['0', '0', '0', '0', '0', '0', 'base_footprint', 'base_scan']),

        launch_ros.actions.Node(
            package='nav2_map_server',
            node_executable='map_server',
            output='screen',
            arguments=[map_file, map_type]),

        launch_ros.actions.Node(
            package='nav2_world_model',
            node_executable='world_model',
            node_name='world_model',
            output='screen',
            parameters=[{ 'use_sim_time': use_sim_time}]),

        launch_ros.actions.Node(
            package='nav2_amcl',
            node_executable='amcl',
            node_name='amcl',
            output='screen',
            remappings=[('scan', 'tb3/scan')],
            parameters=[{ 'use_sim_time': use_sim_time}]),

        launch_ros.actions.Node(
            package='dwb_controller',
            node_executable='dwb_controller',
            node_name='FollowPathNode',
            output='screen',
            remappings=[('/cmd_vel', 'tb3/cmd_vel')],
            parameters=[{ 'prune_plan': False }, {'debug_trajectory_details': True }, { 'use_sim_time': use_sim_time }]),

        launch_ros.actions.Node(
            package='nav2_dijkstra_planner',
            node_executable='dijkstra_planner',
            node_name='dijkstra_planner',
            output='screen',
            parameters=[{ 'use_sim_time': use_sim_time}]),

        launch_ros.actions.Node(
            package='nav2_simple_navigator',
            node_executable='simple_navigator',
            node_name='simple_navigator',
            output='screen',
            parameters=[{ 'use_sim_time': use_sim_time}]),

        launch_ros.actions.Node(
            package='nav2_mission_executor',
            node_executable='mission_executor',
            node_name='mission_executor',
            output='screen',
            parameters=[{ 'use_sim_time': use_sim_time}]),

    ])
