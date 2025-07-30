#!/bin/bash
# Install and test unofficial Go2 SDK for Go2-W compatibility

echo "🚀 Installing Unofficial Unitree Go2 SDK"
echo "This SDK specifically supports Go2-W models"
echo "================================================"

# Navigate to projects directory
cd /workspace/development/projects

# Clone the unofficial SDK
echo "📥 Downloading unofficial SDK..."
if [ -d "go2_python_sdk" ]; then
    echo "  ⚠️ go2_python_sdk already exists, updating..."
    cd go2_python_sdk
    git pull
    cd ..
else
    git clone https://github.com/legion1581/go2_python_sdk.git
fi

cd go2_python_sdk

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Installation complete!"
echo ""
echo "🧪 Testing LiDAR client..."

# Create a test script for the unofficial SDK
cat > test_unofficial_lidar.py << 'EOF'
#!/usr/bin/env python3
"""
Test LiDAR access using unofficial SDK
"""

import sys
import time

# Add the unofficial SDK to path
sys.path.insert(0, '/workspace/development/projects/go2_python_sdk')

try:
    # Import from unofficial SDK
    from clients.lidar_client import LidarClient
    from communicator.dds_communicator import DDSCommunicator
    
    print("✅ Unofficial SDK imported successfully")
    
    # Test LiDAR client
    print("🎯 Testing LiDAR client...")
    
    # Initialize communicator
    communicator = DDSCommunicator()
    communicator.initialize()
    
    # Create LiDAR client
    lidar_client = LidarClient(communicator)
    
    # Test data retrieval
    print("📡 Attempting to get LiDAR data...")
    
    for i in range(10):
        try:
            # Try to get point cloud data
            point_cloud = lidar_client.get_point_cloud()
            if point_cloud is not None:
                print(f"  ✅ Point cloud received: {len(point_cloud)} points")
                break
            else:
                print(f"  ⏰ Attempt {i+1}/10: No data yet...")
                time.sleep(1)
                
        except Exception as e:
            print(f"  ⚠️ Attempt {i+1}/10 failed: {e}")
            time.sleep(1)
    
    # Test LiDAR state
    try:
        state = lidar_client.get_lidar_state()
        if state:
            print(f"✅ LiDAR state: {state}")
        else:
            print("⚠️ No LiDAR state data")
    except Exception as e:
        print(f"❌ LiDAR state error: {e}")

except ImportError as e:
    print(f"❌ Failed to import unofficial SDK: {e}")
    print("💡 The SDK structure might be different, checking available modules...")
    
    # List available modules
    import os
    print("📁 Available directories:")
    for item in os.listdir('/workspace/development/projects/go2_python_sdk'):
        if os.path.isdir(os.path.join('/workspace/development/projects/go2_python_sdk', item)):
            print(f"  - {item}/")
    
    # Try alternative imports
    try:
        import clients
        print("✅ Found clients module")
        print(f"  Available clients: {[item for item in dir(clients) if not item.startswith('_')]}")
    except:
        print("❌ No clients module found")
    
    try:
        import communicator  
        print("✅ Found communicator module")
    except:
        print("❌ No communicator module found")

except Exception as e:
    print(f"❌ Unexpected error: {e}")

print("\n🏁 Unofficial SDK test complete")
EOF

# Make the test script executable
chmod +x test_unofficial_lidar.py

echo "📝 Running unofficial SDK test..."
python3 test_unofficial_lidar.py

echo ""
echo "================================================"
echo "🏁 Unofficial SDK Installation Complete"
echo ""
echo "💡 Next steps:"
echo "1. Check the test results above"
echo "2. If successful, LiDAR data should be available"
echo "3. If not, try the hardware diagnostic script"
echo "4. Consider firmware upgrade if all else fails" 