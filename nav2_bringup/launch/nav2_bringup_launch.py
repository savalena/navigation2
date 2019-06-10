# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from ament_index_python.packages import get_package_prefix
from ament_index_python.packages import get_package_share_directory
from launch.conditions import IfCondition

import launch.actions


def generate_launch_description():
    use_simulation = launch.substitutions.LaunchConfiguration('use_simulation')
    simulator = launch.substitutions.LaunchConfiguration('simulator')
    world = launch.substitutions.LaunchConfiguration('world')
    params_file = launch.substitutions.LaunchConfiguration(
        'params', default=[launch.substitutions.ThisLaunchFileDir(), '/nav2_params.yaml'])

    declare_use_simulation_cmd = launch.actions.DeclareLaunchArgument(
        'use_simulation', condition=IfCondition('True'),
        default_value='True', description='Whether to run in simulation')

    declare_simulator_cmd = launch.actions.DeclareLaunchArgument(
        'simulator',
        default_value='gzserver', description='The simulator to use (gazebo or gzserver)')

    declare_world_cmd = launch.actions.DeclareLaunchArgument(
        'world',
        default_value=os.path.join(
            get_package_share_directory('turtlebot3_gazebo'),
            'worlds/turtlebot3_worlds/burger.model'),
        description='Full path to world file to load')

    declare_params_file_cmd = launch.actions.DeclareLaunchArgument(
        'params_file',
        description='Full path to the ROS2 parameters file to use for all launched nodes')

    launch_dir = os.path.join(get_package_share_directory('nav2_bringup'), 'launch')
    gz = launch.substitutions.LaunchConfiguration('gz', default=['gzserver'])

    # Specify the actions

    start_gazebo_cmd = launch.actions.ExecuteProcess(
        condition=IfCondition(use_simulation),
        cmd=[simulator, '-s', 'libgazebo_ros_init.so', world, ['__params:=', params_file]],
        cwd=[launch_dir], output='screen')

    start_robot_state_publisher_cmd = launch.actions.ExecuteProcess(
        condition=IfCondition(use_simulation),
        cmd=[
            os.path.join(
                get_package_prefix('robot_state_publisher'),
                'lib/robot_state_publisher/robot_state_publisher'),
            os.path.join(
                get_package_share_directory('turtlebot3_description'),
                'urdf', 'turtlebot3_burger.urdf'),
            ['__params:=', params_file]],
        cwd=[launch_dir], output='screen')

    start_rviz_cmd = launch.actions.ExecuteProcess(
        cmd=[os.path.join(get_package_prefix('rviz2'), 'lib/rviz2/rviz2'), ],
        cwd=[launch_dir], output='screen')

    exit_event_handler = launch.actions.RegisterEventHandler(
        event_handler=launch.event_handlers.OnProcessExit(
            target_action=start_rviz_cmd,
            on_exit=launch.actions.EmitEvent(event=launch.events.Shutdown(reason='rviz exited'))))

    start_map_server_cmd = launch.actions.ExecuteProcess(
        cmd=[
            os.path.join(
                get_package_prefix('nav2_map_server'),
                'lib/nav2_map_server/map_server'),
            ['__params:=', params_file]],
        cwd=[launch_dir], output='screen')

    start_localizer_cmd = launch.actions.ExecuteProcess(
        cmd=[
            os.path.join(
                get_package_prefix('nav2_amcl'),
                'lib/nav2_amcl/amcl'),
            ['__params:=', params_file]],
        cwd=[launch_dir], output='screen')

    start_world_model_cmd = launch.actions.ExecuteProcess(
        cmd=[
            os.path.join(
                get_package_prefix('nav2_world_model'),
                'lib/nav2_world_model/world_model'),
            ['__params:=', params_file]],
        cwd=[launch_dir], output='screen')

    start_dwb_cmd = launch.actions.ExecuteProcess(
        cmd=[
            os.path.join(
                get_package_prefix('dwb_controller'),
                'lib/dwb_controller/dwb_controller'),
            ['__params:=', params_file]],
        cwd=[launch_dir], output='screen')

    start_planner_cmd = launch.actions.ExecuteProcess(
        cmd=[
            os.path.join(
                get_package_prefix('nav2_navfn_planner'),
                'lib/nav2_navfn_planner/navfn_planner'),
            ['__params:=', params_file]],
        cwd=[launch_dir], output='screen')

    start_navigator_cmd = launch.actions.ExecuteProcess(
        cmd=[
            os.path.join(
                get_package_prefix('nav2_bt_navigator'),
                'lib/nav2_bt_navigator/bt_navigator'),
            ['__params:=', params_file]],
        cwd=[launch_dir], output='screen')

    start_controller_cmd = launch.actions.ExecuteProcess(
        cmd=[
            os.path.join(
                get_package_prefix('nav2_controller'),
                'lib/nav2_controller/nav2_controller'),
            ['__params:=', params_file]],
        cwd=[launch_dir], output='screen')

    # Create the launch description and populate
    ld = launch.LaunchDescription()

    # First, declare the launch options
    ld.add_action(declare_use_simulation_cmd)
    ld.add_action(declare_simulator_cmd)
    ld.add_action(declare_world_cmd)

    # Then, add the actions to launch the simulator-related nodes (conditioned on 'use_simulation')
    ld.add_action(start_gazebo_cmd)
    ld.add_action(start_robot_state_publisher_cmd)
    ld.add_action(start_rviz_cmd)
    ld.add_action(exit_event_handler)

    # Next, add the actions to launch all of the navigation nodes
    ld.add_action(start_controller_cmd)
    ld.add_action(start_map_server_cmd)
    ld.add_action(start_localizer_cmd)
    ld.add_action(start_world_model_cmd)
    ld.add_action(start_dwb_cmd)
    ld.add_action(start_planner_cmd)
    ld.add_action(start_navigator_cmd)

    return ld
