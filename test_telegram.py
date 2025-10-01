#!/usr/bin/env python3
"""Test script for Telegram notifications."""

from amazon_monitor import AmazonMonitor
import logging

def test_telegram_notification():
    """Test Telegram notification functionality."""
    logging.basicConfig(level=logging.INFO)
    
    monitor = AmazonMonitor()
    
    print("📱 Testing Telegram notification...")
    print(f"Bot Token configured: {'Yes' if monitor.config.TELEGRAM_BOT_TOKEN else 'No'}")
    print(f"Chat ID configured: {'Yes' if monitor.config.TELEGRAM_CHAT_ID else 'No'}")
    
    if not monitor.config.TELEGRAM_BOT_TOKEN or not monitor.config.TELEGRAM_CHAT_ID:
        print("\n❌ Telegram credentials not configured!")
        print("Please add to your .env file:")
        print("TELEGRAM_BOT_TOKEN=your_bot_token_here")
        print("TELEGRAM_CHAT_ID=your_chat_id_here")
        return
    
    # Test with mock available products
    test_products = [{
        'title': 'SUUNTO Race 2 GPS Sports Watch Test',
        'available': True,
        'status': 'Test Status',
        'price': '€299.99',
        'url': f'https://www.{monitor.config.AMAZON_DOMAIN}/s?k=suunto+race+2'
    }]
    
    print("\n📤 Sending test Telegram notification...")
    monitor.send_telegram_notification(test_products)
    print("✅ Telegram notification test complete!")
    print("Check your Telegram app for the message!")

if __name__ == "__main__":
    test_telegram_notification()
