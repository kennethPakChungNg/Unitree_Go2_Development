#!/usr/bin/env python3
"""
Robust Go2-W Development Environment Verification Test

This test verifies that all essential components for Go2-W robotics development
are properly installed and functional. It uses defensive programming techniques
to handle variations in how different packages expose their metadata.
"""

import sys

def get_package_version(module, package_name):
    """
    Attempts to retrieve version information from a Python module using
    multiple common approaches. This defensive technique handles the fact
    that different packages store version information in different ways.
    """
    version_attributes = ['__version__', 'VERSION', 'version']
    
    for attr in version_attributes:
        try:
            version = getattr(module, attr, None)
            if version:
                return str(version)
        except:
            continue
    
    # Try to get version from package metadata if direct attributes fail
    try:
        import pkg_resources
        return pkg_resources.get_distribution(package_name).version
    except:
        pass
    
    # If all else fails, return a descriptive message
    return "installed (version not accessible)"

def test_import_and_functionality():
    """
    Tests that all required packages can be imported and perform basic operations.
    This approach focuses on functionality rather than just version reporting.
    """
    print("🚀 Testing Go2-W Development Environment")
    print("=" * 50)
    
    # Test CyclonDDS for robot communication
    try:
        import cyclonedds
        version = get_package_version(cyclonedds, 'cyclonedds')
        print(f"✅ CyclonDDS {version}: Robot communication middleware ready")
    except ImportError as e:
        print(f"❌ CyclonDDS import failed: {e}")
        return False
    
    # Test NumPy for mathematical operations
    try:
        import numpy as np
        version = get_package_version(np, 'numpy')
        print(f"✅ NumPy {version}: Mathematical operations ready")
        
        # Test actual NumPy functionality with robot-relevant operations
        test_sensor_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        mean_reading = test_sensor_data.mean()
        print(f"   └─ Sensor data processing test: mean = {mean_reading}")
        
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    # Test OpenCV for computer vision operations
    try:
        import cv2
        version = get_package_version(cv2, 'opencv-python-headless')
        print(f"✅ OpenCV {version}: Computer vision ready (headless mode)")
        
        # Test actual OpenCV functionality with robot-relevant operations
        # Create a simulated camera frame
        test_camera_frame = np.zeros((240, 320, 3), dtype=np.uint8)
        # Convert to grayscale (common preprocessing for robot vision)
        processed_frame = cv2.cvtColor(test_camera_frame, cv2.COLOR_BGR2GRAY)
        print(f"   └─ Image processing test: {test_camera_frame.shape} → {processed_frame.shape}")
        
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    # Test Unitree SDK for robot control
    try:
        import unitree_sdk2py
        print("✅ Unitree SDK: Go2-W robot control interface ready")
        
        # Test that we can access key SDK components
        from unitree_sdk2py.core.channel import ChannelFactoryInitialize
        from unitree_sdk2py.go2.sport.sport_client import SportClient
        print("   └─ Core robot control modules accessible")
        
    except ImportError as e:
        print(f"❌ Unitree SDK import failed: {e}")
        return False
    
    print("\n🎉 Environment Verification Successful!")
    print("Your development environment is fully configured and ready for Go2-W robotics development.")
    print("You can now proceed with confidence to robot communication testing and development work.")
    
    return True

if __name__ == "__main__":
    success = test_import_and_functionality()
    sys.exit(0 if success else 1)