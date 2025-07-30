#!/usr/bin/env python3
"""
Control LiDAR services via Unitree SDK
"""

import sys
import time

sys.path.append('/workspace/development/unitree_sdk2_python')

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.robot_state.robot_state_client import RobotStateClient

def control_lidar_services(network_interface):
    print("🔧 LiDAR Service Control")
    
    try:
        # Initialize
        ChannelFactoryInitialize(0, network_interface)
        state_client = RobotStateClient()
        state_client.SetTimeout(10.0)
        state_client.Init()
        
        # List available services
        print("📋 Available services:")
        try:
            services = state_client.ServiceList()
            print(f"   Services: {services}")
        except Exception as e:
            print(f"   ServiceList error: {e}")
        
        # Try to enable LiDAR-related services
        lidar_services = ["lidar", "sensor", "perception", "slam", "l1_lidar"]
        
        for service in lidar_services:
            try:
                print(f"🔄 Trying to enable {service}...")
                result = state_client.ServiceSwitch(service, True)
                print(f"   Result: {result}")
            except Exception as e:
                print(f"   {service} not available: {e}")
        
        # Check API version
        try:
            api_version = state_client.GetApiVersion()
            print(f"📟 API Version: {api_version}")
        except Exception as e:
            print(f"   API version error: {e}")
            
    except Exception as e:
        print(f"❌ Service control failed: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 lidar_service_control.py eth0")
        sys.exit(1)
    
    control_lidar_services(sys.argv[1])
    
    print("\n💡 Next steps:")
    print("1. Check web interface: http://192.168.123.18")
    print("2. Look for LiDAR/sensor settings")
    print("3. Verify LiDAR is physically spinning")

if __name__ == "__main__":
    main()