#!/usr/bin/env python3
"""
Hesai XT-16 UDP to ROS2 Bridge
Receives UDP data from LiDAR and publishes to ROS2 topics
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, PointCloud2
import socket
import threading
import time
import numpy as np
from builtin_interfaces.msg import Time

class HesaiXT16Bridge(Node):
    def __init__(self):
        super().__init__('hesai_xt16_bridge')
        
        # ROS2 publishers
        self.scan_publisher = self.create_publisher(LaserScan, '/scan', 10)
        self.cloud_publisher = self.create_publisher(PointCloud2, '/velodyne_points', 10)
        
        # LiDAR parameters  
        self.lidar_ip = '0.0.0.0'  # Listen on all interfaces
        self.lidar_port = 2368     # Standard LiDAR port
        
        # Initialize UDP socket
        self.setup_udp_socket()
        
        # Start receiving thread
        self.receiving = True
        self.receive_thread = threading.Thread(target=self.receive_lidar_data)
        self.receive_thread.start()
        
        self.get_logger().info(f'🚀 Hesai XT-16 Bridge started - listening on port {self.lidar_port}')
        
    def setup_udp_socket(self):
        """Setup UDP socket for receiving LiDAR data"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.lidar_ip, self.lidar_port))
            self.sock.settimeout(1.0)  # 1 second timeout
            self.get_logger().info(f'✅ UDP socket bound to {self.lidar_ip}:{self.lidar_port}')
        except Exception as e:
            self.get_logger().error(f'❌ Failed to setup UDP socket: {e}')
            
    def receive_lidar_data(self):
        """Receive and process LiDAR UDP packets"""
        packet_count = 0
        
        while self.receiving:
            try:
                # Receive UDP packet
                data, addr = self.sock.recvfrom(4096)
                packet_count += 1
                
                if packet_count % 100 == 0:  # Log every 100 packets
                    self.get_logger().info(f'📦 Received packet #{packet_count}: {len(data)} bytes from {addr}')
                
                # Convert to ROS2 LaserScan message
                self.publish_laser_scan(data, addr)
                
            except socket.timeout:
                # Normal timeout - continue listening
                continue
            except Exception as e:
                self.get_logger().error(f'❌ Error receiving data: {e}')
                time.sleep(1)
                
    def publish_laser_scan(self, data, addr):
        """Convert UDP data to LaserScan message"""
        try:
            # Create LaserScan message
            scan = LaserScan()
            
            # Header
            scan.header.stamp = self.get_clock().now().to_msg()
            scan.header.frame_id = 'laser'
            
            # LiDAR specifications for Hesai XT-16
            scan.angle_min = -3.14159  # -180 degrees
            scan.angle_max = 3.14159   # +180 degrees  
            scan.angle_increment = 0.0174533  # ~1 degree
            scan.time_increment = 0.0001
            scan.scan_time = 0.1  # 10 Hz
            scan.range_min = 0.05  # 5cm minimum
            scan.range_max = 120.0  # 120m maximum
            
            # Simple range data (placeholder - real implementation would parse UDP data)
            num_readings = int((scan.angle_max - scan.angle_min) / scan.angle_increment)
            scan.ranges = [10.0] * num_readings  # Placeholder ranges
            scan.intensities = [100.0] * num_readings  # Placeholder intensities
            
            # Publish scan
            self.scan_publisher.publish(scan)
            
        except Exception as e:
            self.get_logger().error(f'❌ Error publishing scan: {e}')
            
    def destroy_node(self):
        """Cleanup when shutting down"""
        self.receiving = False
        if hasattr(self, 'sock'):
            self.sock.close()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    
    try:
        node = HesaiXT16Bridge()
        rclpy.spin(node)
    except KeyboardInterrupt:
        print('\n🛑 Shutting down Hesai XT-16 Bridge...')
    finally:
        if 'node' in locals():
            node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()