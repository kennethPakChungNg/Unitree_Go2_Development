"""
Enhanced Go2-W Robot Connectivity Test

This test verifies that your development environment can establish reliable
communication with your Go2-W robot's control systems. It builds upon basic
connectivity testing to provide comprehensive validation of your robotics
development setup.

The test systematically verifies each layer of the communication stack,
from low-level network connectivity through high-level robot control APIs.
This approach helps identify exactly where any connectivity issues might
be occurring, which is essential for reliable robotics development.
"""

import sys
import time
import socket
from pathlib import Path

# Add the SDK to Python path for clean imports
# This allows us to import Unitree SDK modules regardless of installation location
sys.path.append('/workspace/development/unitree_sdk2_python')

try:
    from unitree_sdk2py.core.channel import ChannelFactoryInitialize
    from unitree_sdk2py.go2.sport.sport_client import SportClient
    from unitree_sdk2py.go2.robot_state.robot_state_client import RobotStateClient
except ImportError as e:
    print(f"❌ SDK Import Error: {e}")
    print("Ensure the Unitree SDK is properly installed in your container")
    sys.exit(1)

class RobotConnectivityTester:
    """
    Comprehensive connectivity testing class that validates each layer
    of communication with your Go2-W robot.
    
    This systematic approach helps build confidence in your development
    environment and identifies potential issues before they affect your
    robotics development work.
    """
    
    def __init__(self, network_interface):
        self.network_interface = network_interface
        self.test_results = {}
        
    def test_network_layer(self):
        """Test basic network connectivity to robot control systems"""
        print("\n🔍 Testing Network Layer Connectivity...")
        
        robot_ips = {
            'control_interface': '192.168.123.161',
            'extension_dock': '192.168.123.18'
        }
        
        for name, ip in robot_ips.items():
            try:
                # Test basic ICMP connectivity
                result = socket.getaddrinfo(ip, None)
                
                # Test UDP connectivity on control port
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(2)
                
                # Attempt to connect to robot control port
                sock.connect((ip, 8082))
                sock.close()
                
                print(f"  ✅ {name} ({ip}): Network connectivity confirmed")
                self.test_results[f'network_{name}'] = True
                
            except Exception as e:
                print(f"  ❌ {name} ({ip}): Network connectivity failed - {e}")
                self.test_results[f'network_{name}'] = False
    
    def test_dds_communication(self):
        """Test DDS communication layer initialization"""
        print("\n🔍 Testing DDS Communication Layer...")
        
        try:
            # Initialize the DDS communication foundation
            ChannelFactoryInitialize(0, self.network_interface)
            print(f"  ✅ DDS initialized successfully on {self.network_interface}")
            self.test_results['dds_init'] = True
            
        except Exception as e:
            print(f"  ❌ DDS initialization failed: {e}")
            self.test_results['dds_init'] = False
            return False
        
        return True
    
    def test_sport_client(self):
        """Test high-level movement control client"""
        print("\n🔍 Testing Sport Control Client...")
        
        try:
            sport_client = SportClient()
            sport_client.SetTimeout(10.0)
            sport_client.Init()
            
            print("  ✅ Sport client initialized and responsive")
            self.test_results['sport_client'] = True
            return sport_client
            
        except Exception as e:
            print(f"  ❌ Sport client initialization failed: {e}")
            self.test_results['sport_client'] = False
            return None
    
    def test_robot_state_client(self):
        """Test robot state monitoring capabilities"""
        print("\n🔍 Testing Robot State Monitoring...")
        
        try:
            state_client = RobotStateClient()
            state_client.SetTimeout(10.0)
            state_client.Init()
            
            print("  ✅ Robot state monitoring active")
            self.test_results['state_client'] = True
            return state_client
            
        except Exception as e:
            print(f"  ❌ Robot state client initialization failed: {e}")
            self.test_results['state_client'] = False
            return None
    
    def run_comprehensive_test(self):
        """Execute the complete connectivity test suite"""
        print("🚀 Starting Enhanced Go2-W Connectivity Test")
        print(f"   Network Interface: {self.network_interface}")
        print(f"   Test Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test each layer systematically
        self.test_network_layer()
        
        if not self.test_dds_communication():
            return False
            
        sport_client = self.test_sport_client()
        state_client = self.test_robot_state_client()
        
        # Generate comprehensive test report
        self.generate_test_report()
        
        # Return overall success status
        return all(self.test_results.values())
    
    def generate_test_report(self):
        """Generate detailed test results report"""
        print("\n" + "="*60)
        print("📊 CONNECTIVITY TEST RESULTS SUMMARY")
        print("="*60)
        
        passed_tests = sum(1 for result in self.test_results.values() if result)
        total_tests = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name:<25}: {status}")
        
        print(f"\nOverall Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED - Your robotics development environment is ready!")
            print("   You can proceed with confidence to movement testing and advanced development.")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} TESTS FAILED - Please address issues before proceeding")
            print("   Check network connectivity and robot power status.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 enhanced_connection_test.py NETWORK_INTERFACE")
        print("Example: python3 enhanced_connection_test.py eth0")
        print("\nThis test verifies comprehensive connectivity to your Go2-W robot")
        sys.exit(1)
    
    network_interface = sys.argv[1]
    
    # Create and run the connectivity tester
    tester = RobotConnectivityTester(network_interface)
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate status code for script automation
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()