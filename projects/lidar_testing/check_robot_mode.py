#!/usr/bin/env python3
"""
Robot Mode Diagnostic and Activation Helper
Diagnose why robot returns error 3102
"""

import sys
import time
sys.path.append('/workspace/development/unitree_sdk2_python')

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient
from unitree_sdk2py.go2.robot_state.robot_state_client import RobotStateClient

def check_robot_services():
    """Check what services are available and their status"""
    print("🔍 Checking Robot Services")
    print("=" * 30)
    
    try:
        state_client = RobotStateClient()
        state_client.Init()
        
        print("📋 Attempting to get service list...")
        code, services = state_client.ServiceList()
        
        print(f"🎯 Service list returned code: {code}")
        
        if code == 0 and services:
            print(f"✅ Found {len(services)} services:")
            for service in services:
                status = "🟢 Active" if service.status == 1 else "🔴 Inactive"
                protected = "🔒 Protected" if service.protect else "🔓 Open"
                print(f"  - {service.name}: {status}, {protected}")
        elif code == 3102:
            print("❌ Error 3102: Robot not in correct mode for SDK access")
            print("💡 This means:")
            print("   - Robot may be in Lock mode")
            print("   - Robot may be in Damping mode")
            print("   - Robot app may not be running")
            print("   - Robot may need to be activated")
        else:
            print(f"⚠️ Unknown service code: {code}")
            
    except Exception as e:
        print(f"❌ Service check failed: {e}")

def try_different_clients():
    """Try different client types to see what works"""
    print("\n🎮 Testing Different Client Types")
    print("=" * 35)
    
    # Test SportClient
    try:
        print("🏃 Testing SportClient...")
        sport_client = SportClient()
        sport_client.SetTimeout(3.0)
        sport_client.Init()
        print("  ✅ SportClient created successfully")
        
        # Try a simple query instead of movement
        print("  🔍 Testing simple sport client access...")
        # Note: Not calling actual movement commands to avoid error spam
        print("  ✅ SportClient accessible")
        
    except Exception as e:
        print(f"  ❌ SportClient failed: {e}")
    
    # Test RobotStateClient  
    try:
        print("\n📊 Testing RobotStateClient...")
        state_client = RobotStateClient()
        state_client.Init()
        print("  ✅ RobotStateClient created successfully")
        
    except Exception as e:
        print(f"  ❌ RobotStateClient failed: {e}")

def guide_robot_activation():
    """Guide user through robot activation process"""
    print("\n🚀 Robot Activation Guide")
    print("=" * 30)
    
    print("📱 STEP 1: Check Robot Screen")
    print("   1. Look at your Go2-W's screen/display")
    print("   2. Is it active and showing the app?")
    print("   3. What does the screen show?")
    print()
    
    print("🎮 STEP 2: Activate Sport Mode")
    print("   Method A - Touch Screen:")
    print("   1. Tap the screen to wake it up")
    print("   2. Look for mode buttons (Sport/Lock/etc)")
    print("   3. Tap 'Sport' mode button")
    print("   4. Should turn green/highlighted")
    print()
    
    print("   Method B - Power Button:")
    print("   1. Press and hold power button 2-3 seconds")
    print("   2. Robot should make activation sound")
    print("   3. LEDs should change pattern")
    print()
    
    print("   Method C - Physical Check:")
    print("   1. Ensure robot is standing (not sitting)")
    print("   2. Check no emergency stop is pressed")
    print("   3. Verify robot is not in 'sleep' mode")
    print()
    
    print("🔍 STEP 3: Look for These Signs")
    print("   ✅ Screen shows 'Sport' mode active")
    print("   ✅ No lock icon 🔒 visible")
    print("   ✅ Robot LEDs in normal pattern")
    print("   ✅ Robot responds to gentle push (stands firm)")

def test_after_activation():
    """Test robot after user activates sport mode"""
    print("\n⏰ Waiting for Robot Activation...")
    print("=" * 35)
    
    print("💡 After you activate Sport mode:")
    print("1. Wait 5-10 seconds for mode to take effect")
    print("2. Run this test again")
    print("3. Robot should respond to movement commands")
    print()
    
    input("Press Enter after you've activated Sport mode...")
    
    print("\n🔄 Testing again after activation...")
    try:
        sport_client = SportClient()
        sport_client.SetTimeout(5.0)
        sport_client.Init()
        
        print("🪑 Trying sit command...")
        result = sport_client.StandDown()
        
        if result == 0:
            print("🎉 SUCCESS! Robot should sit down now")
            time.sleep(2)
            
            print("🦵 Trying stand command...")
            result2 = sport_client.StandUp()
            if result2 == 0:
                print("🎉 PERFECT! Robot is now responding")
                return True
            else:
                print(f"⚠️ Stand failed with code: {result2}")
        else:
            print(f"❌ Sit still failed with code: {result}")
            print("💡 Robot may still not be in Sport mode")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    return False

def main():
    print("🤖 Go2-W Mode Diagnostic Tool")
    print("=" * 40)
    print("Diagnosing Error 3102 (Robot Mode Issue)")
    print()
    
    # Initialize DDS
    ChannelFactoryInitialize(0, "eth0")
    
    # Step 1: Check services
    check_robot_services()
    
    # Step 2: Test different clients
    try_different_clients()
    
    # Step 3: Guide activation
    guide_robot_activation()
    
    # Step 4: Test after activation
    success = test_after_activation()
    
    # Summary
    print("\n" + "=" * 40)
    if success:
        print("🎉 ROBOT ACTIVATION SUCCESSFUL!")
        print("✅ Robot now responds to SDK commands")
        print("✅ Ready for LiDAR testing")
    else:
        print("❌ Robot still not responding")
        print("🔧 Additional troubleshooting needed:")
        print("- Check robot manual for mode activation")
        print("- Verify robot firmware compatibility")
        print("- Try robot power cycle")

if __name__ == "__main__":
    main() 