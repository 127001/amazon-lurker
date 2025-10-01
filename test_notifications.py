#!/usr/bin/env python3
"""Test script to verify native notifications work on your Mac."""

import subprocess
import platform

def test_notification():
    """Test native macOS notification."""
    print("🔔 Testing native macOS notification...")
    
    try:
        if platform.system() == "Darwin":  # macOS
            applescript = '''
            display notification "If you can see this notification, your setup is working correctly!" with title "🚨 Amazon Monitor Test" sound name "Glass"
            '''
            
            subprocess.run(['osascript', '-e', applescript], check=True)
            print("✅ Notification sent successfully!")
            print("📱 Check your Mac's notification center or top-right corner")
        else:
            print("❌ This test only works on macOS")
            
    except Exception as e:
        print(f"❌ Error sending notification: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're running this on macOS")
        print("2. Check System Preferences > Notifications > Terminal")
        print("3. Ensure notifications are enabled for Terminal/Python")

if __name__ == "__main__":
    test_notification()

