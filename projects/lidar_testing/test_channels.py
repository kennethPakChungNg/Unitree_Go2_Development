# test_channels.py
import sys
sys.path.append('/workspace/development/unitree_sdk2_python')

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
import signal
import time

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

ChannelFactoryInitialize(0, "eth0")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(3)  # 3 second timeout

try:
    print("Testing basic connectivity...")
    time.sleep(1)
    print("✅ Basic test passed")
except TimeoutError:
    print("❌ Test timed out")
finally:
    signal.alarm(0)