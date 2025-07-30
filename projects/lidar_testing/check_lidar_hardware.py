#!/usr/bin/env python3
"""
Check Go2-W LiDAR Hardware Status and Activation
"""

import sys
import time
import subprocess
sys.path.append('/workspace/development/unitree_sdk2_python')

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient
from unitree_sdk2py.go2.robot_state.robot_state_client import RobotStateClient

def check_robot_connection():
    """Verify basic robot connectivity"""
    print("🔌 Checking Robot Connection...")
    
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

def check_lidar_hardware_visually():
    """Guide user to check LiDAR hardware status"""
    print("\n👁️ Visual LiDAR Hardware Check")
    print("=" * 40)
    print("Please visually inspect your Go2-W and answer:")
    print()
    
    print("1. 🔄 Is the LiDAR unit spinning?")
    print("   - Look at the top of the robot")
    print("   - You should see a black cylindrical unit rotating")
    print()
    
    print("2. 💡 Is the LiDAR LED active?")
    print("   - Look for a green LED on the LiDAR unit")
    print("   - It should be solid or blinking green")
    print()
    
    print("3. 🔊 Can you hear the LiDAR motor?")
    print("   - There should be a quiet humming/whirring sound")
    print("   - This indicates the motor is running")
    print()
    
    # Interactive check
    try:
        spinning = input("Is the LiDAR spinning? (y/n): ").lower().strip()
        led_active = input("Is the green LED on? (y/n): ").lower().strip()
        motor_sound = input("Can you hear motor sound? (y/n): ").lower().strip()
        
        print(f"\n📊 Hardware Status:")
        print(f"  - Spinning: {'✅' if spinning == 'y' else '❌'}")
        print(f"  - LED: {'✅' if led_active == 'y' else '❌'}")
        print(f"  - Motor: {'✅' if motor_sound == 'y' else '❌'}")
        
        if spinning == 'y' and led_active == 'y':
            print("\n✅ LiDAR hardware appears active!")
            return True
        else:
            print("\n❌ LiDAR hardware appears inactive!")
            return False
            
    except KeyboardInterrupt:
        print("\n⚠️ Manual check skipped")
        return False

def try_lidar_activation():
    """Try to activate LiDAR through available methods"""
    print("\n🚀 Attempting LiDAR Activation...")
    print("=" * 40)
    
    # Method 1: Try through SportClient
    print("1️⃣ Trying SportClient activation...")
    try:
        sport_client = SportClient()
        sport_client.SetTimeout(10.0)
        sport_client.Init()
        
        # Try basic robot activation which might start sensors
        print("  - Standing up robot...")
        sport_client.StandUp()
        time.sleep(3)
        
        print("  - Setting to sport mode...")
        sport_client.Move(0, 0, 0)  # Enable movement mode
        time.sleep(2)
        
        print("  ✅ Robot activation commands sent")
        
    except Exception as e:
        print(f"  ❌ SportClient activation failed: {e}")
    
    # Method 2: Try RobotStateClient service management
    print("\n2️⃣ Trying service activation...")
    try:
        state_client = RobotStateClient()
        state_client.Init()
        
        # Try to get and potentially restart services
        print("  - Checking available services...")
        
        # Even if ServiceList fails, try to enable potential LiDAR services
        lidar_services = [
            "lidar_server",
            "utlidar_server", 
            "point_cloud_server",
            "sensor_server",
            "perception_server"
        ]
        
        for service in lidar_services:
            try:
                print(f"  - Attempting to start {service}...")
                code = state_client.ServiceSwitch(service, True)
                if code == 0:
                    print(f"    ✅ {service} started successfully")
                else:
                    print(f"    ⚠️ {service} start returned code: {code}")
            except Exception as e:
                print(f"    ❌ {service} start failed: {e}")
        
    except Exception as e:
        print(f"  ❌ Service activation failed: {e}")

def test_after_activation():
    """Test LiDAR data access after activation attempts"""
    print("\n🔍 Testing LiDAR Access After Activation...")
    print("=" * 40)
    
    # Wait for services to potentially start
    print("⏰ Waiting 10 seconds for services to initialize...")
    time.sleep(10)
    
    # Test UDP ports again
    import socket
    
    lidar_ports = [2368, 2369, 8308]
    for port in lidar_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)
            sock.bind(('', port))
            
            print(f"🔌 Testing port {port}...")
            data, addr = sock.recvfrom(1024)
            print(f"  ✅ Data received on port {port}! ({len(data)} bytes)")
            sock.close()
            return True
            
        except socket.timeout:
            print(f"  ⏰ No data on port {port}")
            sock.close()
        except Exception as e:
            print(f"  ❌ Port {port} error: {e}")
    
    return False

def check_robot_app_settings():
    """Guide user to check robot app settings"""
    print("\n📱 Unitree Go App Settings Check")
    print("=" * 40)
    print("Check these settings in the Unitree Go mobile app:")
    print()
    
    print("1. 🔧 Device Settings:")
    print("   - Open Unitree Go app")
    print("   - Go to Device → Data → Unitree Perception LiDAR")
    print("   - Check if LiDAR is enabled")
    print("   - Look for 'Packet Loss Rate' - should be low (<10%)")
    print()
    
    print("2. 🎯 LiDAR Mode:")
    print("   - Ensure LiDAR is not in sleep/standby mode")
    print("   - Try toggling LiDAR on/off in app")
    print("   - Restart robot if needed")
    print()
    
    print("3. 📊 Data Status:")
    print("   - Look for 'PointCloud Data Status'")
    print("   - Check packet loss rate")
    print("   - Verify data is flowing")

def main():
    print("🚀 Go2-W LiDAR Hardware Diagnostic & Activation")
    print("=" * 50)
    
    # Step 1: Basic connection check
    if not check_robot_connection():
        print("❌ Cannot proceed without robot connection")
        return
    
    # Step 2: Visual hardware check
    hardware_ok = check_lidar_hardware_visually()
    
    if not hardware_ok:
        print("\n⚠️ LiDAR hardware appears inactive. Trying activation...")
        
        # Step 3: Try activation
        try_lidar_activation()
        
        # Step 4: Test after activation
        if test_after_activation():
            print("\n🎉 SUCCESS! LiDAR data detected after activation!")
        else:
            print("\n❌ Still no LiDAR data after activation attempts")
            
        # Step 5: App settings guidance
        check_robot_app_settings()
    
    else:
        print("\n✅ Hardware appears active but no data detected")
        print("💡 This suggests a software/configuration issue")
        
        # Test data access
        if test_after_activation():
            print("🎉 SUCCESS! LiDAR data is now available!")
        else:
            check_robot_app_settings()
    
    print("\n" + "=" * 50)
    print("🏁 Hardware Diagnostic Complete")
    
    print("\n📋 Summary & Next Steps:")
    print("1. If LiDAR hardware is not spinning → Check power/connections")
    print("2. If hardware spins but no data → Try app settings")
    print("3. If app shows high packet loss → Network/firmware issue")
    print("4. If all fails → Try unofficial SDK or contact support")

if __name__ == "__main__":
    main() 