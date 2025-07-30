#!/usr/bin/env python3
"""
Go2-W Basic Connection Test
Step-by-step connectivity verification
"""

import sys
import subprocess
import socket
import time
sys.path.append('/workspace/development/unitree_sdk2_python')

def test_network_connectivity():
    """Test basic network connectivity to robot"""
    print("🌐 Testing Network Connectivity")
    print("=" * 35)
    
    # Common Go2-W IP addresses
    robot_ips = [
        "192.168.123.161",  # Common Go2-W IP
        "192.168.123.162",  # Alternative
        "192.168.123.1",    # Gateway
        "192.168.123.12",   # Another common IP
    ]
    
    reachable_ips = []
    
    for ip in robot_ips:
        print(f"🎯 Testing {ip}...")
        try:
            # Use Linux ping syntax (-c for count, -W for timeout in seconds)
            result = subprocess.run(['ping', '-c', '1', '-W', '2', ip], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and "ttl=" in result.stdout.lower():
                print(f"  ✅ {ip} responds to ping")
                reachable_ips.append(ip)
            else:
                print(f"  ❌ {ip} no response")
        except Exception as e:
            print(f"  ❌ {ip} ping failed: {e}")
    
    if reachable_ips:
        print(f"\n✅ Robot network reachable: {reachable_ips}")
        return reachable_ips[0]  # Return first working IP
    else:
        print(f"\n❌ No robot found on network")
        return None

def test_robot_ports(robot_ip):
    """Test if robot services are running"""
    print(f"\n🔌 Testing Robot Service Ports on {robot_ip}")
    print("=" * 45)
    
    # Common robot service ports
    test_ports = [
        (8080, "Web interface"),
        (8081, "API service"),
        (9090, "Control service"),
        (22, "SSH service"),
    ]
    
    open_ports = []
    
    for port, description in test_ports:
        print(f"🎯 Testing {robot_ip}:{port} ({description})...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((robot_ip, port))
            
            if result == 0:
                print(f"  ✅ Port {port} open")
                open_ports.append(port)
            else:
                print(f"  ❌ Port {port} closed")
            
            sock.close()
            
        except Exception as e:
            print(f"  ❌ Port {port} test failed: {e}")
    
    return open_ports

def test_sdk_initialization():
    """Test SDK initialization without commands"""
    print("\n🔧 Testing SDK Initialization")
    print("=" * 35)
    
    try:
        print("📡 Initializing DDS communication...")
        from unitree_sdk2py.core.channel import ChannelFactoryInitialize
        
        ChannelFactoryInitialize(0, "eth0")
        print("  ✅ DDS factory initialized")
        
        # Wait a moment for initialization
        time.sleep(2)
        
        print("🎮 Testing SportClient creation...")
        from unitree_sdk2py.go2.sport.sport_client import SportClient
        
        sport_client = SportClient()
        print("  ✅ SportClient created")
        
        print("⏱️ Setting timeout...")
        sport_client.SetTimeout(5.0)
        print("  ✅ Timeout set")
        
        print("🚀 Initializing client...")
        sport_client.Init()
        print("  ✅ SportClient initialized")
        
        print("\n🎉 SDK initialization SUCCESSFUL!")
        return True
        
    except Exception as e:
        print(f"\n❌ SDK initialization FAILED: {e}")
        return False

def test_robot_state():
    """Test basic robot state access"""
    print("\n📊 Testing Robot State Access")
    print("=" * 35)
    
    try:
        from unitree_sdk2py.go2.robot_state.robot_state_client import RobotStateClient
        
        print("🤖 Creating robot state client...")
        state_client = RobotStateClient()
        state_client.Init()
        print("  ✅ State client created")
        
        # Try to get basic info (this may fail but gives us info)
        try:
            print("📋 Checking service list...")
            code, services = state_client.ServiceList()
            if code == 0:
                print(f"  ✅ Services available: {len(services) if services else 0}")
                if services:
                    for service in services[:3]:  # Show first 3
                        print(f"    - {service.name}")
            else:
                print(f"  ⚠️ Service list code: {code}")
        except Exception as e:
            print(f"  ⚠️ Service list failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Robot state test failed: {e}")
        return False

def check_robot_mode():
    """Check what mode the robot is in"""
    print("\n🎯 Robot Mode Check")
    print("=" * 25)
    
    print("💡 IMPORTANT: Check robot's current state:")
    print("1. 🔋 Is robot powered on? (LEDs active)")
    print("2. 📱 Is robot app running? (screen active)")
    print("3. 🎮 What mode is active? (Sport/Lock/Damping)")
    print("4. 🔒 Is robot locked? (app shows lock icon)")
    print("5. 🔴 Emergency stop pressed?")
    print()
    print("💡 For SDK control, robot should be in:")
    print("   - 🟢 Sport mode (not locked)")
    print("   - 📱 App running and responsive")
    print("   - 🔓 Not in emergency stop")

def main():
    print("🚀 Go2-W Connection Diagnostic")
    print("=" * 50)
    print("Step-by-step connectivity testing")
    print()
    
    # Step 1: Network connectivity
    robot_ip = test_network_connectivity()
    
    if not robot_ip:
        print("\n❌ NETWORK CONNECTIVITY FAILED")
        print("\n🔧 Troubleshooting:")
        print("- Check robot is powered on")
        print("- Verify network cable connection")
        print("- Check computer IP is 192.168.123.x")
        print("- Try: ifconfig (check your IP)")
        return
    
    # Step 2: Robot services
    open_ports = test_robot_ports(robot_ip)
    
    # Step 3: SDK initialization
    sdk_ok = test_sdk_initialization()
    
    if not sdk_ok:
        print("\n❌ SDK INITIALIZATION FAILED")
        print("\n🔧 Troubleshooting:")
        print("- Robot may not be in sport mode")
        print("- Check robot app is running")
        print("- Verify robot is not locked")
        return
    
    # Step 4: Robot state
    test_robot_state()
    
    # Step 5: Mode check
    check_robot_mode()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 CONNECTION TEST SUMMARY")
    print("=" * 50)
    
    if robot_ip and sdk_ok:
        print("🎉 BASIC CONNECTION WORKING!")
        print(f"✅ Robot reachable at {robot_ip}")
        print("✅ SDK can initialize")
        print(f"🔌 Open ports: {open_ports}")
        print("\n💡 Next steps:")
        print("1. Check robot is in Sport mode (not locked)")
        print("2. Try movement commands")
        print("3. Test LiDAR power status")
    else:
        print("❌ CONNECTION ISSUES DETECTED")
        print("\n🔧 Fix these issues first:")
        print("- Network connectivity")
        print("- Robot power/app state")
        print("- SDK compatibility")

if __name__ == "__main__":
    main() 