#!/usr/bin/env python3
"""
Go2-W LiDAR to ROS2 Bridge
Connects to Hesai XT16 LiDAR and publishes point cloud data to ROS2
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header
import socket
import struct
import numpy as np
import time
from threading import Thread

class LidarBridge(Node):
    def __init__(self):
        super().__init__('lidar_bridge')
        
        # Configuration
        self.lidar_ip = '192.168.123.20'
        self.lidar_port = 2368
        self.frame_id = 'lidar_frame'
        
        # ROS2 Publisher
        self.point_cloud_pub = self.create_publisher(
            PointCloud2, 
            '/scan', 
            10
        )
        
        # Status logging
        self.get_logger().info(f'🚀 Starting LiDAR Bridge...')
        self.get_logger().info(f'📡 Target: {self.lidar_ip}:{self.lidar_port}')
        
        # Start LiDAR reader thread
        self.running = True
        self.lidar_thread = Thread(target=self.read_lidar_data)
        self.lidar_thread.daemon = True
        self.lidar_thread.start()
        
        # Statistics
        self.packet_count = 0
        self.last_stats_time = time.time()
        
        # Timer for status updates
        self.create_timer(5.0, self.print_status)
    
    def read_lidar_data(self):
        """Main LiDAR data reading loop"""
        self.get_logger().info('🔗 Starting LiDAR reader thread...')
        
        while self.running:
            try:
                # Create UDP socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(1.0)  # 1 second timeout
                
                # Try different approaches to get data
                self.get_logger().info('📡 Attempting to connect to LiDAR...')
                
                # Method 1: Try to bind and listen
                try:
                    sock.bind(('0.0.0.0', self.lidar_port))
                    self.get_logger().info('✅ Bound to LiDAR port, waiting for data...')
                    
                    while self.running:
                        try:
                            # Receive data
                            data, addr = sock.recvfrom(65535)  # Max UDP packet size
                            
                            if len(data) > 0:
                                self.packet_count += 1
                                self.get_logger().info(f'📦 Received packet #{self.packet_count}: {len(data)} bytes from {addr}')
                                
                                # Process the packet
                                self.process_lidar_packet(data)
                                
                        except socket.timeout:
                            # No data received, continue waiting
                            pass
                        except Exception as e:
                            self.get_logger().error(f'❌ Data receive error: {e}')
                            break
                            
                except OSError as e:
                    self.get_logger().warn(f'⚠️ Could not bind to port {self.lidar_port}: {e}')
                    self.get_logger().info('🔄 Trying alternative connection method...')
                    
                    # Method 2: Try to connect directly
                    try:
                        sock.connect((self.lidar_ip, self.lidar_port))
                        self.get_logger().info('✅ Connected to LiDAR directly')
                        
                        # Send a simple request (if LiDAR expects one)
                        sock.send(b'SCAN_REQUEST')
                        
                        # Listen for response
                        data = sock.recv(65535)
                        if len(data) > 0:
                            self.packet_count += 1
                            self.process_lidar_packet(data)
                            
                    except Exception as e:
                        self.get_logger().error(f'❌ Direct connection failed: {e}')
                
                sock.close()
                
            except Exception as e:
                self.get_logger().error(f'❌ Socket creation failed: {e}')
            
            # Wait before retrying
            if self.running:
                self.get_logger().info('🔄 Retrying connection in 5 seconds...')
                time.sleep(5)
    
    def process_lidar_packet(self, data):
        """Process raw LiDAR packet and convert to ROS2 PointCloud2"""
        try:
            # Log packet info
            self.get_logger().info(f'🔍 Processing packet: {len(data)} bytes')
            
            # For now, create a simple test point cloud
            # Later: Parse actual Hesai XT16 data format
            points = self.create_test_pointcloud()
            
            # Convert to ROS2 PointCloud2 message
            cloud_msg = self.create_pointcloud2_msg(points)
            
            # Publish to ROS2
            self.point_cloud_pub.publish(cloud_msg)
            self.get_logger().info(f'📤 Published point cloud with {len(points)} points')
            
        except Exception as e:
            self.get_logger().error(f'❌ Packet processing error: {e}')
    
    def create_test_pointcloud(self):
        """Create test point cloud data"""
        # Generate simple test points in a circle
        angles = np.linspace(0, 2*np.pi, 360)
        distances = np.ones_like(angles) * 5.0  # 5 meter radius
        
        points = []
        for angle, dist in zip(angles, distances):
            x = dist * np.cos(angle)
            y = dist * np.sin(angle)
            z = 0.0
            points.append([x, y, z])
        
        return np.array(points, dtype=np.float32)
    
    def create_pointcloud2_msg(self, points):
        """Convert point array to ROS2 PointCloud2 message"""
        # Create header
        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        header.frame_id = self.frame_id
        
        # Define point fields (x, y, z coordinates)
        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
        ]
        
        # Create PointCloud2 message
        cloud_msg = PointCloud2()
        cloud_msg.header = header
        cloud_msg.height = 1
        cloud_msg.width = len(points)
        cloud_msg.fields = fields
        cloud_msg.is_bigendian = False
        cloud_msg.point_step = 12  # 3 floats * 4 bytes each
        cloud_msg.row_step = cloud_msg.point_step * cloud_msg.width
        cloud_msg.data = points.tobytes()
        cloud_msg.is_dense = True
        
        return cloud_msg
    
    def print_status(self):
        """Print periodic status updates"""
        current_time = time.time()
        elapsed = current_time - self.last_stats_time
        rate = self.packet_count / elapsed if elapsed > 0 else 0
        
        self.get_logger().info(f'📊 Status: {self.packet_count} packets, {rate:.1f} packets/sec')
        
        # Reset counters
        self.packet_count = 0
        self.last_stats_time = current_time
    
    def destroy_node(self):
        """Clean shutdown"""
        self.running = False
        if hasattr(self, 'lidar_thread'):
            self.lidar_thread.join(timeout=1.0)
        super().destroy_node()

def main(args=None):
    """Main function"""
    # Initialize ROS2
    rclpy.init(args=args)
    
    # Create and run the bridge node
    try:
        bridge = LidarBridge()
        
        print("🚀 Go2-W LiDAR Bridge Started!")
        print("📡 Connecting to LiDAR at 192.168.123.20:2368")
        print("📤 Publishing point clouds to /scan topic")
        print("Press Ctrl+C to stop...")
        
        # Keep running until interrupted
        rclpy.spin(bridge)
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping LiDAR bridge...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'bridge' in locals():
            bridge.destroy_node()
        rclpy.shutdown()
        print("✅ LiDAR bridge stopped")

if __name__ == '__main__':
    main()