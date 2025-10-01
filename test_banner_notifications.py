#!/usr/bin/env python3
"""Test script to verify banner notifications are working."""

import subprocess
import time

def test_banner_notifications():
    """Test banner notifications to see if they work."""
    print("🔔 Testing banner notifications...")
    
    # Test 1: Simple banner
    print("\n1. Testing simple banner notification...")
    try:
        subprocess.run(['osascript', '-e', 'display notification "Simple banner test" with title "Test 1"'], check=True)
        print("✅ Simple banner sent")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Simple banner failed: {e}")
    
    # Test 2: Banner with sound
    print("\n2. Testing banner with sound...")
    try:
        subprocess.run(['osascript', '-e', 'display notification "Banner with sound test" with title "Test 2" sound name "Glass"'], check=True)
        print("✅ Banner with sound sent")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Banner with sound failed: {e}")
    
    # Test 3: Banner with subtitle
    print("\n3. Testing banner with subtitle...")
    try:
        subprocess.run(['osascript', '-e', 'display notification "Banner with subtitle test" with title "Test 3" subtitle "Subtitle"'], check=True)
        print("✅ Banner with subtitle sent")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Banner with subtitle failed: {e}")
    
    print("\n📱 Check your Mac's top-right corner for banner notifications!")
    print("If you see them, banner notifications are working!")
    print("If you don't see them, follow the permission steps in the previous output.")

if __name__ == "__main__":
    test_banner_notifications()




