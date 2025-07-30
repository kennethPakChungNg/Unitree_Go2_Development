#!/bin/bash
# Enhanced Go2-W Development Environment Setup
# This script handles dependency conflicts and ensures correct package versions

echo "🚀 Configuring Go2-W Development Environment"
echo "   This process includes dependency conflict resolution"

# Update system package manager
echo "📦 Updating system packages..."
apt-get update -qq

# Install essential development tools
echo "🔧 Installing development tools..."
apt-get install -y -qq \
    python3-dev \
    cmake \
    build-essential \
    libssl-dev \
    git \
    iproute2 \
    net-tools \
    iputils-ping

# Upgrade pip to latest version
echo "🐍 Upgrading Python package manager..."
pip3 install --upgrade pip --quiet

# Install core Python packages (excluding OpenCV temporarily)
echo "📚 Installing core robotics packages..."
pip3 install --quiet \
    cyclonedds \
    numpy

# Install Unitree SDK (which may install opencv-python)
echo "🤖 Setting up Unitree SDK..."
cd /workspace/development
if [ ! -d "unitree_sdk2_python" ]; then
    echo "   Cloning Unitree SDK repository..."
    git clone https://github.com/unitreerobotics/unitree_sdk2_python.git --quiet
fi
cd unitree_sdk2_python
pip3 install -e . --quiet

# Post-SDK installation: Fix OpenCV dependency conflict
echo "🔧 Resolving OpenCV dependency conflict..."
pip3 uninstall opencv-python -y --quiet 2>/dev/null || true
pip3 install opencv-python-headless --quiet

# Verify installation with comprehensive testing
echo "🔍 Verifying package installation..."
python3 -c "
try:
    import cyclonedx, numpy, cv2, unitree_sdk2py
    print('✅ All packages installed successfully')
    print('   CyclonDDS: Robot communication ready')
    print('   NumPy: Mathematical operations ready') 
    print('   OpenCV: Computer vision ready (headless mode)')
    print('   Unitree SDK: Go2-W control interface ready')
except ImportError as e:
    print(f'❌ Package verification failed: {e}')
    exit(1)
"

echo "🎉 Container environment setup complete!"
echo "   Your development environment is ready for Go2-W robotics work"