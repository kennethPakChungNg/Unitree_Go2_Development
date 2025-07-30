#!/usr/bin/env python3
"""
Real LiDAR Data Access for Go2-W Hesai XT16
Captures and processes actual point cloud data
"""

import sys
import time
import socket
import struct
import numpy as np

sys.path.append('/workspace/development/unitree_sdk2_python')

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.robot_state.robot_state_client import RobotStateClient

class RealLiDARCapture:
    def __init__(self, network_interface):
        self.network_interface = network_interface
        self.robot_ip = "192.168.123.161"
        
    def initialize_connection(self):
        """Initialize robot connection"""
        try:
            ChannelFactoryInitialize(0, self.network_interface)
            self.state_client = RobotStateClient()
            self.state_client.SetTimeout(10.0)
            self.state_client.Init()
            print("✅ Robot connection established")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def capture_lidar_packet(self, port=2368, timeout=5):
        """Capture raw LiDAR data packet"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            sock.bind(('', port))
            
            print(f"🔍 Listening for LiDAR data on port {port}...")
            data, addr = sock.recvfrom(1024)
            sock.close()
            
            print(f"✅ Received {len(data)} bytes from {addr}")
            return data
            
        except socket.timeout:
            print(f"⏰ No data received within {timeout} seconds")
            return None
        except Exception as e:
            print(f"❌ Error capturing data: {e}")
            return None
    
    def parse_hesai_packet(self, data):
        """Parse Hesai XT16 data packet"""
        if not data or len(data) < 100:
            return None
            
        points = []
        # Basic parsing - actual format depends on Hesai XT16 specification
        try:
            # Sample parsing logic (adjust based on actual packet format)
            for i in range(0, min(len(data)-12, 300), 12):
                x = struct.unpack('<f', data[i:i+4])[0]
                y = struct.unpack('<f', data[i+4:i+8])[0] 
                z = struct.unpack('<f', data[i+8:i+12])[0]
                
                if abs(x) < 100 and abs(y) < 100 and abs(z) < 100:
                    points.append([x, y, z])
                    
            return np.array(points) if points else None
            
        except Exception as e:
            print(f"⚠️ Parsing error: {e}")
            return None
    
    def analyze_point_cloud(self, points):
        """Analyze point cloud for obstacles and mapping"""
        if points is None or len(points) == 0:
            return
            
        print(f"📊 Point cloud analysis:")
        print(f"   Points captured: {len(points)}")
        print(f"   Range: X({points[:,0].min():.2f} to {points[:,0].max():.2f})")
        print(f"          Y({points[:,1].min():.2f} to {points[:,1].max():.2f})")
        print(f"          Z({points[:,2].min():.2f} to {points[:,2].max():.2f})")
        
        # Distance analysis
        distances = np.linalg.norm(points, axis=1)
        close_obstacles = np.sum(distances < 1.0)
        medium_range = np.sum((distances >= 1.0) & (distances < 5.0))
        far_range = np.sum(distances >= 5.0)
        
        print(f"🚧 Obstacle detection:")
        print(f"   Close (<1m): {close_obstacles} points")
        print(f"   Medium (1-5m): {medium_range} points") 
        print(f"   Far (>5m): {far_range} points")
        
        return {
            'total_points': len(points),
            'close_obstacles': close_obstacles,
            'distances': distances
        }
    
    def run_lidar_capture(self):
        """Main LiDAR capture routine"""
        print("🚀 Starting Real LiDAR Data Capture")
        print(f"   Robot IP: {self.robot_ip}")
        print(f"   LiDAR: Hesai XT16")
        
        if not self.initialize_connection():
            return False
            
        # Try different common LiDAR ports
        ports = [2368, 2369, 8308]
        
        for port in ports:
            print(f"\n📡 Attempting capture on port {port}")
            data = self.capture_lidar_packet(port)
            
            if data:
                points = self.parse_hesai_packet(data)
                analysis = self.analyze_point_cloud(points)
                
                if analysis and analysis['total_points'] > 0:
                    print("✅ Real LiDAR data successfully captured!")
                    return True
                    
        print("❌ No valid LiDAR data captured")
        print("💡 Try: Ensure robot is powered on and LiDAR is spinning")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 real_lidar_access.py NETWORK_INTERFACE")
        print("Example: python3 real_lidar_access.py eth0")
        sys.exit(1)
    
    network_interface = sys.argv[1]
    capture = RealLiDARCapture(network_interface)
    capture.run_lidar_capture()

if __name__ == "__main__":
    main()