#!/usr/bin/env python3
"""Simple script to run the Amazon monitor with better error handling."""

import sys
import signal
import time
from amazon_monitor import AmazonMonitor

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print('\n🛑 Monitoring stopped by user.')
    sys.exit(0)

def main():
    """Main entry point."""
    print("🚀 Starting Amazon Product Monitor")
    print("📱 Monitoring: Suunto Race 2 Titanium Trail on Amazon.nl")
    print("📧 Notifications will be sent to your configured email")
    print("⏹️  Press Ctrl+C to stop monitoring\n")
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        monitor = AmazonMonitor()
        monitor.monitor()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()




