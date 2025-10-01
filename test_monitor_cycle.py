#!/usr/bin/env python3
"""Test script to run one monitoring cycle and trigger notifications."""

from amazon_monitor import AmazonMonitor
import logging

def test_monitor_cycle():
    """Run one monitoring cycle to test notifications."""
    logging.basicConfig(level=logging.INFO)
    
    monitor = AmazonMonitor()
    
    print("🔍 Running one monitoring cycle...")
    print(f"EAN: {monitor.config.PRODUCT_EAN}")
    print(f"Domain: {monitor.config.AMAZON_DOMAIN}")
    print(f"Notification type: {monitor.config.NOTIFICATION_TYPE}")
    
    # Search for the product
    if monitor.config.PRODUCT_EAN:
        products = monitor.search_amazon(ean=monitor.config.PRODUCT_EAN)
    else:
        products = monitor.search_amazon(monitor.config.PRODUCT_SEARCH_TERM)
    
    if products:
        available_products = [p for p in products if p['available']]
        
        print(f"\n📊 Results:")
        print(f"  Total products found: {len(products)}")
        print(f"  Available products: {len(available_products)}")
        
        if available_products:
            print(f"\n🎉 Found {len(available_products)} available products!")
            print("📱 Sending notification...")
            monitor.send_notification(available_products)
            print("✅ Notification sent! Check your Mac for the notification.")
            
            print(f"\n📋 Available products:")
            for i, product in enumerate(available_products):
                print(f"{i+1}. {product['title'][:70]}...")
                print(f"   Status: {product['status']}")
                if product.get('price'):
                    print(f"   Price: {product['price']}")
                print(f"   URL: {product['url'][:60]}...")
                print()
        else:
            print("\n📦 Products found but not available yet")
            print("No notification sent.")
    else:
        print("\n❌ No products found in search results")
        print("No notification sent.")
    
    print("\n✅ Monitoring cycle test complete!")

if __name__ == "__main__":
    test_monitor_cycle()





