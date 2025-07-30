#!/usr/bin/env python3
"""
Go2-W Specific LiDAR Data Access Script
Addresses known compatibility issues between Go2 and Go2-W models
"""

import sys
import time
import struct
import socket
import threading
sys.path.append('/workspace/development/unitree_sdk2_python')

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.idl.default import unitree_go_msg_dds__LowState_
from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowState_

class Go2WLidarAccess:
    def __init__(self, robot_ip="192.168.123.161", interface="eth0"):
        self.robot_ip = robot_ip
        self.interface = interface
        self.data_received = False
        self.stop_listening = False
        
    def test_dds_topics(self):
        """Test various DDS topics that might contain LiDAR data"""
        print("🔍 Testing DDS Topics for LiDAR Data")
        print("-" * 40)
        
        # List of potential LiDAR topics for Go2-W
        potential_topics = [
            "rt/utlidar/cloud",     # Standard LiDAR point cloud
            "rt/utlidar/state",     # LiDAR state information
            "rt/lidar/cloud",       # Alternative topic name
            "rt/lidar/state",       # Alternative state topic
            "ut/lidar/cloud",       # Unitree-specific naming
            "ut/utlidar/cloud",     # Extended naming
            "/utlidar/cloud",       # ROS-style naming
            "/lidar/point_cloud",   # Standard ROS naming
        ]
        
        for topic in potential_topics:
            print(f"🎯 Testing topic: {topic}")
            try:
                # Try to subscribe with generic handler
                def generic_handler(msg):
                    print(f"  ✅ Data received on {topic}")
                    print(f"  📊 Message type: {type(msg)}")
                    if hasattr(msg, '__dict__'):
                        attrs = [attr for attr in dir(msg) if not attr.startswith('_')]
                        print(f"  📋 Attributes: {attrs[:5]}...")  # Show first 5 attributes
                    self.data_received = True
                
                # Try subscription
                subscriber = ChannelSubscriber(topic, LowState_)  # Using LowState as fallback
                subscriber.Init(generic_handler, 10)
                
                # Wait briefly for data
                time.sleep(2)
                
                if not self.data_received:
                    print(f"  ❌ No data on {topic}")
                    
            except Exception as e:
                print(f"  ❌ Failed to subscribe to {topic}: {e}")
        
    def test_udp_ports(self):
        """Test UDP ports commonly used by LiDAR systems"""
        print("\n🌐 Testing UDP Ports for LiDAR Data")
        print("-" * 40)
        
        # Known LiDAR ports for Hesai XT16 and similar
        lidar_ports = [2368, 2369, 8308, 8080, 6789, 2366, 2367]
        
        for port in lidar_ports:
            print(f"🔌 Testing port {port}")
            try:
                thread = threading.Thread(target=self.listen_udp_port, args=(port, 3))
                thread.daemon = True
                thread.start()
                thread.join(timeout=4)
                
            except Exception as e:
                print(f"  ❌ Error on port {port}: {e}")
    
    def listen_udp_port(self, port, timeout=5):
        """Listen on a specific UDP port for LiDAR data"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(timeout)
            sock.bind(('', port))
            
            print(f"  👂 Listening on port {port}...")
            
            data, addr = sock.recvfrom(4096)
            print(f"  ✅ Received {len(data)} bytes from {addr}")
            print(f"  📊 Data preview: {data[:50].hex()}")
            
            # Try to identify LiDAR data pattern
            if self.analyze_lidar_packet(data):
                print(f"  🎯 Detected LiDAR data pattern!")
            
            sock.close()
            
        except socket.timeout:
            print(f"  ⏰ Timeout on port {port}")
        except Exception as e:
            print(f"  ❌ Error listening on port {port}: {e}")
    
    def analyze_lidar_packet(self, data):
        """Analyze if received data looks like LiDAR packets"""
        try:
            # Check for common LiDAR packet patterns
            if len(data) < 16:
                return False
            
            # Check for Hesai XT16 header patterns
            header = data[:8]
            
            # Look for typical LiDAR headers (magic numbers)
            hesai_headers = [
                b'\xEE\xFF',  # Common Hesai header
                b'\xFF\xEE',  # Alternative header
                b'\xAA\x55', # Another common pattern
            ]
            
            for pattern in hesai_headers:
                if pattern in header:
                    return True
            
            # Check for repeating patterns typical of point cloud data
            if len(data) >= 1200:  # Typical LiDAR packet size
                return True
                
            return False
            
        except:
            return False
    
    def test_robot_services(self):
        """Test robot services that might provide LiDAR access"""
        print("\n🤖 Testing Robot Services")
        print("-" * 40)
        
        try:
            from unitree_sdk2py.go2.robot_state.robot_state_client import RobotStateClient
            
            client = RobotStateClient()
            client.Init()
            
            # Get available services
            code, services = client.ServiceList()
            if code == 0 and services:
                print("📋 Available robot services:")
                for service in services:
                    print(f"  - {service.name}: {'🟢' if service.status else '🔴'}")
                    
                    # Look for LiDAR-related services
                    if any(keyword in service.name.lower() 
                          for keyword in ['lidar', 'scan', 'point', 'cloud', 'sensor']):
                        print(f"    🎯 Potential LiDAR service: {service.name}")
            else:
                print(f"❌ Failed to get services list, code: {code}")
                
        except Exception as e:
            print(f"❌ Robot services test failed: {e}")
    
    def test_alternative_sdk(self):
        """Test using alternative unofficial SDK approaches"""
        print("\n🔧 Testing Alternative SDK Approaches")
        print("-" * 40)
        
        # This would integrate with the unofficial Go2 SDK mentioned in research
        print("💡 Consider trying unofficial Go2 SDK:")
        print("   - GitHub: legion1581/go2_python_sdk")
        print("   - Supports Go2-W with different communication patterns")
        print("   - May have better WebRTC support for consumer models")
        
        # Check if we can detect what model we're working with
        print("\n🔍 Robot Model Detection:")
        try:
            # Try to determine if this is AIR/PRO vs EDU
            # EDU models typically have full DDS access
            # AIR/PRO models may need firmware upgrade or WebRTC
            
            from unitree_sdk2py.go2.sport.sport_client import SportClient
            sport_client = SportClient()
            sport_client.SetTimeout(5.0)
            sport_client.Init()
            
            print("  ✅ SportClient initialized successfully")
            print("  💡 This suggests EDU model or proper SDK setup")
            
        except Exception as e:
            print(f"  ❌ SportClient failed: {e}")
            print("  💡 This might indicate AIR/PRO model needing firmware upgrade")

def main():
    print("🚀 Go2-W LiDAR Access Diagnostic Tool")
    print("=" * 50)
    
    # Initialize communication
    try:
        ChannelFactoryInitialize(0, "eth0")
        print("✅ DDS communication initialized")
    except Exception as e:
        print(f"❌ DDS initialization failed: {e}")
        return
    
    # Create access tester
    tester = Go2WLidarAccess()
    
    # Run all tests
    tester.test_robot_services()
    tester.test_dds_topics() 
    tester.test_udp_ports()
    tester.test_alternative_sdk()
    
    print("\n" + "=" * 50)
    print("🏁 Go2-W LiDAR Diagnostic Complete")
    print("\n💡 Next Steps:")
    print("1. If no data found, try the unofficial SDK")
    print("2. Check if firmware upgrade is needed for your model")
    print("3. Verify LiDAR hardware is spinning and LED is active")
    print("4. Consider using ROS bridge if available")

if __name__ == "__main__":
    main() 