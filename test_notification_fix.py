#!/usr/bin/env python3
"""Test different notification methods to find one that works."""

import subprocess
import time
import os

def test_notification_methods():
    """Test various notification methods."""
    print("🔔 Testing different notification methods...")
    
    # Method 1: Basic osascript
    print("\n1. Testing basic osascript notification...")
    try:
        subprocess.run(['osascript', '-e', 'display notification "Basic test notification" with title "Method 1"'], check=True)
        print("✅ Method 1 sent")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    # Method 2: Using terminal-notifier if available
    print("\n2. Testing terminal-notifier...")
    try:
        result = subprocess.run(['which', 'terminal-notifier'], capture_output=True, text=True)
        if result.returncode == 0:
            subprocess.run(['terminal-notifier', '-title', 'Method 2', '-message', 'Terminal-notifier test'], check=True)
            print("✅ Method 2 sent")
        else:
            print("❌ terminal-notifier not installed")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
    
    # Method 3: Using say command (audio notification)
    print("\n3. Testing audio notification...")
    try:
        subprocess.run(['say', 'Amazon monitor test notification'], check=True)
        print("✅ Method 3 sent (audio)")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
    
    # Method 4: Using system dialog
    print("\n4. Testing system dialog...")
    try:
        subprocess.run(['osascript', '-e', 'display dialog "Amazon Monitor Test" with title "Method 4" buttons {"OK"} default button "OK"'], check=True)
        print("✅ Method 4 sent (dialog)")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Method 4 failed: {e}")
    
    # Method 5: Using growlnotify if available
    print("\n5. Testing growlnotify...")
    try:
        result = subprocess.run(['which', 'growlnotify'], capture_output=True, text=True)
        if result.returncode == 0:
            subprocess.run(['growlnotify', '-t', 'Method 5', '-m', 'Growl test notification'], check=True)
            print("✅ Method 5 sent")
        else:
            print("❌ growlnotify not installed")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Method 5 failed: {e}")
    
    print("\n📱 Please check which methods you can see/hear:")
    print("- Method 1: Basic notification (top-right corner)")
    print("- Method 2: terminal-notifier notification")
    print("- Method 3: Audio notification (you should hear speech)")
    print("- Method 4: System dialog (popup window)")
    print("- Method 5: Growl notification")

if __name__ == "__main__":
    test_notification_methods()





