#!/usr/bin/env python3
"""
Access LiDAR data through Unitree SDK
"""

import sys
import time
import numpy as np

sys.path.append('/workspace/development/unitree_sdk2_python')

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.robot_state.robot_state_client import RobotStateClient

def access_lidar_via_sdk(network_interface):
    print("🚀 Accessing LiDAR via Unitree SDK")
    
    try:
        # Initialize
        ChannelFactoryInitialize(0, network_interface)
        state_client = RobotStateClient()
        state_client.SetTimeout(10.0)
        state_client.Init()
        
        print("✅ SDK initialized")
        
        # Try to read robot state data
        for i in range(10):
            print(f"📡 Reading robot state {i+1}/10...")
            
            # Get robot state (may contain sensor data)
            try:
                # Check what's available in the state client
                print(f"   State client methods: {[m for m in dir(state_client) if not m.startswith('_')]}")
                
                # Try different ways to access sensor data
                if hasattr(state_client, 'GetRobotState'):
                    state = state_client.GetRobotState()
                    print(f"   Robot state type: {type(state)}")
                    if state:
                        print(f"   State attributes: {[attr for attr in dir(state) if not attr.startswith('_')]}")
                
            except Exception as e:
                print(f"   ⚠️ State read error: {e}")
            
            time.sleep(1)
            
    except Exception as e:
        print(f"❌ SDK access failed: {e}")

def check_lidar_activation():
    print("\n🔍 LiDAR Activation Check")
    print("The LiDAR might need activation through:")
    print("1. Robot web interface (192.168.123.18)")
    print("2. Specific SDK commands")
    print("3. App-based LiDAR enabling")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 sdk_lidar_access.py eth0")
        sys.exit(1)
    
    access_lidar_via_sdk(sys.argv[1])
    check_lidar_activation()

if __name__ == "__main__":
    main()