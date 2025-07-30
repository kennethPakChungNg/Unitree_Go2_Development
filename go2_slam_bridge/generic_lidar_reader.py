#!/usr/bin/env python3
"""
Generic UDP LiDAR Reader for ROS2
Direct connection to Hesai XT16 without vendor-specific drivers
"""

import rclpy
from rclpy.node import Node
import socket
import struct
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header

class GenericLidarReader(Node):
    def __init__(self):
        super().__init__('generic_lidar_reader')
        
        # Create publisher for point cloud data
        self.publisher = self.create_publisher(PointCloud2, '/velodyne_points', 10)
        
        # LiDAR network settings
        self.lidar_ip = '192.168.123.20'
        self.lidar_port = 2368
        
        # Start UDP listener
        self.start_udp_listener()
    
    def start_udp_listener(self):
        self.get_logger().info(f'🔍 Connecting to LiDAR at {self.lidar_ip}:{self.lidar_port}')
        
        try:
            # Create UDP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.settimeout(5.0)
            
            # Try to connect to LiDAR
            self.sock.connect((self.lidar_ip, self.lidar_port))
            self.get_logger().info('✅ Connected to LiDAR!')
            
            # Start receiving data
            self.receive_data()
            
        except Exception as e:
            self.get_logger().error(f'❌ Connection failed: {e}')
    
    def receive_data(self):
        packet_count = 0
        while rclpy.ok():
            try:
                # Receive LiDAR packet
                data = self.sock.recv(2048)
                packet_count += 1
                
                if packet_count % 100 == 0:  # Log every 100 packets
                    self.get_logger().info(f'📦 Received packet #{packet_count}: {len(data)} bytes')
                
                # TODO: Parse Hesai XT16 packet format and publish to ROS2
                # For now, just log that we're receiving data
                
            except socket.timeout:
                self.get_logger().warn('⏰ No data received in 5 seconds')
            except Exception as e:
                self.get_logger().error(f'❌ Error receiving data: {e}')
                break

def main():
    rclpy.init()
    node = GenericLidarReader()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()