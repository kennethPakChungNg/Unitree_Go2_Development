#!/usr/bin/env python3
"""
Hesai XT16 LiDAR Launch Configuration
Direct connection to Go2-W LiDAR for SLAM mapping
"""

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Hesai XT16 LiDAR node
        Node(
            package='velodyne_driver',
            executable='velodyne_driver_node',
            name='hesai_xt16',
            parameters=[{
                'device_ip': '192.168.123.20',  # Your LiDAR IP
                'port': 2368,                   # LiDAR data port
                'model': 'XT16',               # Hesai XT16 model
                'frame_id': 'velodyne',        # ROS frame name
                'rpm': 600.0,                  # 600 RPM (from web interface)
            }],
            output='screen'
        ),
        
        # Convert point cloud to laser scan for SLAM
        Node(
            package='pointcloud_to_laserscan',
            executable='pointcloud_to_laserscan_node',
            name='pc_to_scan',
            parameters=[{
                'target_frame': 'velodyne',
                'transform_tolerance': 0.01,
                'min_height': -1.0,
                'max_height': 1.0,
                'angle_min': -3.14159,  # -180 degrees
                'angle_max': 3.14159,   # +180 degrees
                'angle_increment': 0.0087,  # ~0.5 degrees
                'scan_time': 0.1,
                'range_min': 0.05,      # 5cm minimum (XT16 spec)
                'range_max': 120.0,     # 120m maximum (XT16 spec)
            }],
            remappings=[
                ('cloud_in', '/velodyne_points'),
                ('scan', '/scan')
            ],
            output='screen'
        )
    ])