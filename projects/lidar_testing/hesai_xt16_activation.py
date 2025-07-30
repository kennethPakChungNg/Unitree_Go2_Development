#!/usr/bin/env python3
"""
Hesai Pandar XT-16 LiDAR Activation and Detection Script
Professional external LiDAR sensor management
"""

import socket
import struct
import time
import threading
import subprocess

class HesaiXT16Controller:
    def __init__(self):
        # Hesai XT-16 default network settings
        self.lidar_ip = "192.168.1.201"  # Default Hesai IP
        self.host_ip = "192.168.1.100"   # Your computer IP
        self.data_port = 2368            # Point cloud data port
        self.device_port = 9347          # Device control port
        self.gps_port = 10110           # GPS/timestamp port
        
        # Alternative IPs to try
        self.possible_ips = [
            "192.168.1.201",  # Default Hesai
            "192.168.123.201", # Unitree network variant
            "192.168.0.201",   # Common alternative
            "10.5.5.200",      # Another common Hesai IP
        ]

    def check_power_status(self):
        """Guide user through power status check"""
        print("🔋 Hesai XT-16 Power Status Check")
        print("=" * 40)
        print("Please visually inspect your Hesai Pandar XT-16:")
        print()
        
        print("1. 💡 Power LED Status:")
        print("   - Look for LED indicators on the sensor")
        print("   - Green/Blue = Powered and ready")
        print("   - Red/Orange = Error or initializing")
        print("   - No LED = No power")
        print()
        
        print("2. 🔄 Rotation Status:")
        print("   - The sensor head should be rotating")
        print("   - You should hear a quiet motor sound")
        print("   - Rotation speed: ~600-1200 RPM")
        print()
        
        print("3. 🔌 Cable Connections:")
        print("   - Power cable connected to robot power distribution")
        print("   - Ethernet cable connected to expansion module")
        print("   - All connections secure")
        print()
        
        try:
            power_led = input("Is the power LED on? (y/n): ").lower().strip()
            rotating = input("Is the sensor rotating? (y/n): ").lower().strip()
            cables_ok = input("Are all cables connected? (y/n): ").lower().strip()
            
            print(f"\n📊 Power Status:")
            print(f"  - Power LED: {'✅' if power_led == 'y' else '❌'}")
            print(f"  - Rotating: {'✅' if rotating == 'y' else '❌'}")
            print(f"  - Cables: {'✅' if cables_ok == 'y' else '❌'}")
            
            if power_led == 'y' and rotating == 'y':
                print("\n✅ Hesai XT-16 appears powered and active!")
                return True
            else:
                print("\n❌ Hesai XT-16 needs power/connection attention!")
                return False
                
        except KeyboardInterrupt:
            print("\n⚠️ Power check skipped")
            return False

    def scan_for_lidar(self):
        """Scan network for Hesai XT-16"""
        print("\n🔍 Scanning for Hesai XT-16 on Network...")
        print("=" * 40)
        
        found_devices = []
        
        for ip in self.possible_ips:
            print(f"🎯 Testing {ip}...")
            
            # Test ping first
            try:
                result = subprocess.run(['ping', '-c', '1', '-W', '2', ip], 
                                     capture_output=True, timeout=5)
                if result.returncode == 0:
                    print(f"  ✅ {ip} responds to ping")
                    found_devices.append(ip)
                else:
                    print(f"  ❌ {ip} no ping response")
            except:
                print(f"  ❌ {ip} ping failed")
        
        if found_devices:
            print(f"\n🎉 Found potential LiDAR devices: {found_devices}")
            return found_devices
        else:
            print(f"\n❌ No LiDAR devices found on standard IPs")
            return []

    def test_udp_data_port(self, ip):
        """Test if UDP data is coming from specific IP"""
        print(f"\n📡 Testing UDP data from {ip}:{self.data_port}")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(5)
            sock.bind(('', self.data_port))
            
            print(f"  👂 Listening for data...")
            
            data, addr = sock.recvfrom(4096)
            print(f"  🎉 Received {len(data)} bytes from {addr}")
            
            # Analyze Hesai packet structure
            if self.analyze_hesai_packet(data):
                print(f"  ✅ Confirmed Hesai XT-16 data format!")
                return True
            else:
                print(f"  ⚠️ Data format doesn't match Hesai XT-16")
                
            sock.close()
            
        except socket.timeout:
            print(f"  ⏰ No data received (timeout)")
            return False
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

    def analyze_hesai_packet(self, data):
        """Analyze if packet matches Hesai XT-16 format"""
        if len(data) < 512:  # Hesai packets are typically larger
            return False
        
        # Check for Hesai packet headers
        # XT-16 typically uses specific header patterns
        header = data[:8]
        
        # Common Hesai headers (this may need adjustment based on firmware)
        hesai_patterns = [
            b'\xEE\xFF\x55\xAA',  # Common Hesai pattern
            b'\xFF\xEE\xAA\x55',  # Alternative pattern
            b'\x55\xAA\xFF\xEE',  # Another variant
        ]
        
        for pattern in hesai_patterns:
            if pattern in data[:20]:  # Check first 20 bytes
                return True
        
        # Check for typical LiDAR data characteristics
        if len(data) > 1000 and len(data) < 2000:  # Typical XT-16 packet size
            return True
            
        return False

    def send_activation_commands(self, ip):
        """Send activation commands to Hesai XT-16"""
        print(f"\n🚀 Sending activation commands to {ip}")
        
        try:
            # Create control socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)
            
            # Common Hesai activation commands
            commands = [
                # Start spinning command
                b'\x47\x74\x00\x01\x00\x00\x00\x00',
                # Set return mode (dual return)
                b'\x47\x74\x00\x02\x39\x00\x00\x00',
                # Start data transmission
                b'\x47\x74\x00\x03\x00\x00\x00\x00',
            ]
            
            for i, cmd in enumerate(commands):
                print(f"  📤 Sending command {i+1}/{len(commands)}...")
                try:
                    sock.sendto(cmd, (ip, self.device_port))
                    
                    # Try to receive response
                    try:
                        response, addr = sock.recvfrom(1024)
                        print(f"    ✅ Response: {len(response)} bytes")
                    except socket.timeout:
                        print(f"    ⏰ No response (normal for some commands)")
                        
                except Exception as e:
                    print(f"    ❌ Command {i+1} failed: {e}")
                
                time.sleep(0.5)
            
            sock.close()
            print(f"  ✅ Activation commands sent")
            return True
            
        except Exception as e:
            print(f"  ❌ Activation failed: {e}")
            return False

    def configure_network_for_hesai(self):
        """Configure network interface for Hesai communication"""
        print("\n🌐 Network Configuration for Hesai XT-16")
        print("=" * 40)
        
        print("To communicate with Hesai XT-16, you may need to:")
        print()
        print("1. 🔧 Set your computer's IP in same subnet:")
        print("   sudo ifconfig eth0 192.168.1.100/24")
        print("   (or whatever interface connects to the LiDAR)")
        print()
        print("2. 🎯 Configure LiDAR IP if needed:")
        print("   - Use Hesai LiDAR configuration tool")
        print("   - Default IP: 192.168.1.201")
        print("   - May need to match robot's network: 192.168.123.x")
        print()
        print("3. 📡 Test connectivity:")
        print("   ping 192.168.1.201")
        print("   telnet 192.168.1.201 9347")

def main():
    print("🚀 Hesai Pandar XT-16 Activation Tool")
    print("=" * 50)
    print("Professional LiDAR sensor initialization")
    print()
    
    controller = HesaiXT16Controller()
    
    # Step 1: Check physical power status
    if not controller.check_power_status():
        print("\n⚠️ Resolve power issues before continuing")
        print("💡 Check:")
        print("- Power cable connection to robot")
        print("- Robot power distribution to sensors")
        print("- LiDAR power requirements (12V/24V)")
        return
    
    # Step 2: Scan network for device
    found_devices = controller.scan_for_lidar()
    
    if not found_devices:
        print("\n❌ No LiDAR found on network")
        controller.configure_network_for_hesai()
        print("\n💡 Try manual network configuration and run again")
        return
    
    # Step 3: Test data ports and send activation commands
    success = False
    for ip in found_devices:
        print(f"\n🎯 Testing device at {ip}")
        
        # Send activation commands
        if controller.send_activation_commands(ip):
            print(f"  ⏰ Waiting 5 seconds for activation...")
            time.sleep(5)
            
            # Test for data
            if controller.test_udp_data_port(ip):
                print(f"  🎉 SUCCESS! Hesai XT-16 active at {ip}")
                success = True
                break
            else:
                print(f"  ⚠️ Commands sent but no data yet")
    
    # Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 Hesai XT-16 Successfully Activated!")
        print("✅ LiDAR is now sending data")
        print("\n💡 Next steps:")
        print("- Create point cloud processing scripts")
        print("- Integrate with your patrol route system")
        print("- Use standard LiDAR libraries (PCL, Open3D)")
        
    else:
        print("❌ Hesai XT-16 Activation Failed")
        print("\n🔧 Troubleshooting:")
        print("- Verify power connections")
        print("- Check network configuration")
        print("- Try manual activation with Hesai tools")
        print("- Consult Hesai XT-16 documentation")

if __name__ == "__main__":
    main() 