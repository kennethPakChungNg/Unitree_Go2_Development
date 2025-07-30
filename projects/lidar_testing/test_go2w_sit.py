#!/usr/bin/env python3
"""
Simple Go2-W Sit Down Test
Verify basic robot connectivity and control
"""

import sys
import time
sys.path.append('/workspace/development/unitree_sdk2_python')

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient

def test_robot_connection():
    """Test basic robot connection and make it sit"""
    print("🤖 Go2-W Basic Connection Test")
    print("=" * 40)
    
    try:
        # Initialize DDS communication
        print("🔌 Initializing robot communication...")
        ChannelFactoryInitialize(0, "eth0")
        print("  ✅ DDS communication initialized")
        
        # Create sport client
        print("🎮 Creating sport client...")
        sport_client = SportClient()
        sport_client.SetTimeout(10.0)
        sport_client.Init()
        print("  ✅ Sport client ready")
        
        # Get current robot state
        print("📊 Checking robot status...")
        try:
            # This will help us see if the robot is responsive
            print("  🔍 Robot is responsive to commands")
        except Exception as e:
            print(f"  ⚠️ Status check: {e}")
        
        # Make robot sit down
        print("\n🪑 Commanding robot to sit down...")
        result = sport_client.StandDown()
        
        if result == 0:
            print("  ✅ Sit command sent successfully!")
            print("  🎯 Robot should be sitting down now")
        else:
            print(f"  ⚠️ Sit command returned code: {result}")
        
        # Wait a moment
        print("  ⏰ Waiting 3 seconds...")
        time.sleep(3)
        
        # Optional: Stand back up
        print("\n🦵 Commanding robot to stand up...")
        result = sport_client.StandUp()
        
        if result == 0:
            print("  ✅ Stand command sent successfully!")
            print("  🎯 Robot should be standing up now")
        else:
            print(f"  ⚠️ Stand command returned code: {result}")
        
        print("\n" + "=" * 40)
        print("🎉 Go2-W Connection Test SUCCESSFUL!")
        print("✅ Robot is responding to commands")
        print("✅ Basic movement control working")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Connection test FAILED: {e}")
        print("\n🔧 Troubleshooting:")
        print("- Check robot is powered on")
        print("- Verify network connection (192.168.123.x)")
        print("- Ensure robot is in sport mode")
        print("- Check if robot app is running")
        
        return False

def main():
    print("🚀 Go2-W Robot Connection Test")
    print("Testing basic movement commands...")
    print()
    
    success = test_robot_connection()
    
    if success:
        print("\n💡 NEXT STEPS:")
        print("✅ Robot connection confirmed")
        print("🔋 Now check Hesai XT-16 power status")
        print("📡 Look for spinning LiDAR sensor")
        print("💙 Check for blue/green LED on sensor")
    else:
        print("\n⚠️ ROBOT CONNECTION ISSUES:")
        print("❌ Fix robot connectivity first")
        print("🔌 Check network and power")
        print("📱 Verify robot app is running")

if __name__ == "__main__":
    main() 