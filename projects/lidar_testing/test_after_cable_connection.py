#!/usr/bin/env python3
"""
Test LiDAR functionality after cable connection
"""

import sys
import time
import socket
import threading
sys.path.append('/workspace/development/unitree_sdk2_python')

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.go2.robot_state.robot_state_client import RobotStateClient
from unitree_sdk2py.go2.sport.sport_client import SportClient
from unitree_sdk2py.idl.default import unitree_go_msg_dds__LowState_
from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowState_

def test_basic_connection():
    """Test basic robot connection"""
    print("🔌 Testing Basic Robot Connection...")
    
    try:
        ChannelFactoryInitialize(0, "eth0")
        
        sport_client = SportClient()
        sport_client.SetTimeout(5.0)
        sport_client.Init()
        
        print("  ✅ Robot connection confirmed")
        return True
        
    except Exception as e:
        print(f"  ❌ Robot connection failed: {e}")
        return False

def test_robot_services():
    """Test robot services - should work better now"""
    print("\n🤖 Testing Robot Services (After Cable Connection)...")
    
    try:
        state_client = RobotStateClient()
        state_client.Init()
        
        print("  🔍 Checking service list...")
        code, services = state_client.ServiceList()
        
        if code == 0 and services:
            print(f"  ✅ SUCCESS! Services accessible (code: {code})")
            print(f"  📋 Found {len(services)} services:")
            
            lidar_services = []
            for service in services:
                print(f"    - {service.name}: {'🟢 ACTIVE' if service.status else '🔴 INACTIVE'}")
                
                # Look for LiDAR-related services
                if any(keyword in service.name.lower() 
                      for keyword in ['lidar', 'utlidar', 'point', 'cloud', 'sensor', 'perception']):
                    lidar_services.append(service)
                    print(f"      🎯 LiDAR-RELATED SERVICE FOUND!")
            
            if lidar_services:
                print(f"\n  🎉 Found {len(lidar_services)} LiDAR-related services!")
                return True
            else:
                print(f"\n  ⚠️ No obvious LiDAR services found")
                return False
                
        else:
            print(f"  ❌ Service list failed with code: {code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Service test failed: {e}")
        return False

def test_udp_ports_improved():
    """Test UDP ports with longer timeout - hardware should respond now"""
    print("\n🌐 Testing UDP Ports (Extended)...")
    
    def listen_port(port, results):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(8)  # Longer timeout
            sock.bind(('', port))
            
            print(f"  👂 Listening on port {port} (8 second timeout)...")
            
            data, addr = sock.recvfrom(4096)
            results[port] = (True, len(data), addr)
            print(f"  🎉 PORT {port}: Received {len(data)} bytes from {addr}!")
            
            # Quick analysis
            if len(data) > 100:
                print(f"    📊 Looks like LiDAR data (large packet)")
            
            sock.close()
            
        except socket.timeout:
            results[port] = (False, 0, None)
            print(f"  ⏰ Port {port}: No data (timeout)")
        except Exception as e:
            results[port] = (False, 0, str(e))
            print(f"  ❌ Port {port}: Error - {e}")

    # Test key LiDAR ports with threading for parallel testing
    ports = [2368, 2369, 8308, 8080]
    results = {}
    threads = []
    
    for port in ports:
        thread = threading.Thread(target=listen_port, args=(port, results))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join(timeout=10)
    
    # Summary
    successful_ports = [port for port, (success, _, _) in results.items() if success]
    
    if successful_ports:
        print(f"\n  🎉 SUCCESS! LiDAR data found on ports: {successful_ports}")
        return True
    else:
        print(f"\n  ❌ No LiDAR data on any tested ports")
        return False

def test_dds_topics_enhanced():
    """Test DDS topics with callback tracking"""
    print("\n📡 Testing DDS Topics (Enhanced)...")
    
    data_received = {'count': 0, 'topics': []}
    
    def make_handler(topic_name):
        def handler(msg):
            data_received['count'] += 1
            if topic_name not in data_received['topics']:
                data_received['topics'].append(topic_name)
            print(f"  🎉 Data received on {topic_name}! (Total: {data_received['count']})")
            
            # Analyze message content
            if hasattr(msg, 'imu_state'):
                print(f"    📊 IMU data detected")
            if hasattr(msg, 'motor_state'):
                print(f"    🦿 Motor data detected")
            if hasattr(msg, 'foot_force'):
                print(f"    👣 Foot sensor data detected")
                
        return handler
    
    # Test expanded list of topics
    topics_to_test = [
        ("rt/lowstate", LowState_),
        ("rt/utlidar/cloud", LowState_),  # Using LowState as fallback
        ("rt/utlidar/state", LowState_),
        ("ut/utlidar/cloud", LowState_),
        ("rt/lidar/cloud", LowState_),
    ]
    
    subscribers = []
    
    for topic_name, msg_type in topics_to_test:
        try:
            print(f"  🎯 Subscribing to {topic_name}...")
            subscriber = ChannelSubscriber(topic_name, msg_type)
            subscriber.Init(make_handler(topic_name), 10)
            subscribers.append(subscriber)
            
        except Exception as e:
            print(f"    ❌ Failed to subscribe to {topic_name}: {e}")
    
    if subscribers:
        print(f"  ✅ Subscribed to {len(subscribers)} topics")
        print(f"  ⏰ Waiting 15 seconds for data...")
        time.sleep(15)
        
        if data_received['count'] > 0:
            print(f"\n  🎉 SUCCESS! Received data on topics: {data_received['topics']}")
            return True
        else:
            print(f"\n  ❌ No data received on any DDS topics")
            return False
    else:
        print(f"  ❌ Failed to subscribe to any topics")
        return False

def try_lidar_activation():
    """Try to activate LiDAR services now that hardware is connected"""
    print("\n🚀 Attempting LiDAR Service Activation...")
    
    try:
        state_client = RobotStateClient()
        state_client.Init()
        
        # Try to activate potential LiDAR services
        services_to_try = [
            "lidar_server",
            "utlidar_server", 
            "point_cloud_server",
            "sensor_server",
            "perception_server",
            "lidar_driver",
            "hesai_driver",
            "utlidar_driver"
        ]
        
        activated = []
        
        for service in services_to_try:
            try:
                print(f"  🔧 Trying to start {service}...")
                code = state_client.ServiceSwitch(service, True)
                
                if code == 0:
                    print(f"    ✅ {service} started successfully!")
                    activated.append(service)
                else:
                    print(f"    ⚠️ {service} returned code: {code}")
                    
            except Exception as e:
                print(f"    ❌ {service} failed: {e}")
        
        if activated:
            print(f"\n  🎉 Successfully activated: {activated}")
            return True
        else:
            print(f"\n  ⚠️ No services could be activated")
            return False
            
    except Exception as e:
        print(f"  ❌ Service activation failed: {e}")
        return False

def main():
    print("🚀 Go2-W LiDAR Test After Cable Connection")
    print("=" * 50)
    print("Testing to verify cable connection resolved the issue...")
    print()
    
    # Test sequence
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Basic connection
    if test_basic_connection():
        tests_passed += 1
    
    # Test 2: Robot services (should work better now)
    if test_robot_services():
        tests_passed += 1
    
    # Test 3: Try service activation
    if try_lidar_activation():
        tests_passed += 1
    
    # Wait a moment for services to start
    print("\n⏰ Waiting 5 seconds for services to initialize...")
    time.sleep(5)
    
    # Test 4: UDP ports (should have data now)
    if test_udp_ports_improved():
        tests_passed += 1
    
    # Test 5: DDS topics (should receive data now)
    if test_dds_topics_enhanced():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"🏁 Cable Connection Test Results")
    print(f"📊 Tests Passed: {tests_passed}/{total_tests}")
    
    if tests_passed >= 3:
        print("🎉 EXCELLENT! Cable connection fixed the issue!")
        print("✅ LiDAR system is now working")
        print("\n💡 Next steps:")
        print("- Use your existing scripts for LiDAR data")
        print("- Try the real_lidar_access.py script again")
        print("- Develop your patrol route system")
        
    elif tests_passed >= 1:
        print("🟡 PARTIAL SUCCESS - Some improvements detected")
        print("💡 Cable helped, but may need additional configuration")
        print("\n🔧 Try:")
        print("- Check Unitree Go app settings")
        print("- Restart robot completely")
        print("- Try unofficial SDK")
        
    else:
        print("❌ Cable connection didn't resolve all issues")
        print("💡 Additional troubleshooting needed:")
        print("- Verify cable is fully seated")
        print("- Check if LiDAR LED is now active")
        print("- Try robot restart")
        print("- Consider firmware issues")

if __name__ == "__main__":
    main() 