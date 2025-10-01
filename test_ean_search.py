#!/usr/bin/env python3
"""Test script for EAN-based Amazon search."""

from amazon_monitor import AmazonMonitor
import logging

def test_ean_search():
    """Test EAN search functionality."""
    logging.basicConfig(level=logging.INFO)
    
    monitor = AmazonMonitor()
    
    # Test EAN search on amazon.de (where we know it's available)
    print("🔍 Testing EAN search on amazon.de...")
    products = monitor.search_amazon(ean="SS051203000", domain="amazon.de")
    
    if products:
        print(f"✅ Found {len(products)} products on amazon.de:")
        for i, product in enumerate(products):
            print(f"{i+1}. {product['title'][:80]}...")
            print(f"   Available: {product['available']} - Status: {product['status']}")
            if product.get('price'):
                print(f"   Price: {product['price']}")
            print(f"   URL: {product['url'][:60]}...")
            print()
    else:
        print("❌ No products found on amazon.de")
    
    print("\n" + "="*60)
    
    # Test EAN search on the configured domain (where we want to monitor)
    target_domain = monitor.config.AMAZON_DOMAIN
    print(f"🔍 Testing EAN search on {target_domain}...")
    products = monitor.search_amazon(ean="SS051203000", domain=target_domain)
    
    if products:
        print(f"✅ Found {len(products)} products on {target_domain}:")
        for i, product in enumerate(products):
            print(f"{i+1}. {product['title'][:80]}...")
            print(f"   Available: {product['available']} - Status: {product['status']}")
            if product.get('price'):
                print(f"   Price: {product['price']}")
            print(f"   URL: {product['url'][:60]}...")
            print()
    else:
        print(f"❌ No products found on {target_domain} (this is expected if not available yet)")
    
    print("\n" + "="*60)
    print("🎯 EAN search test complete!")
    print(f"If amazon.de shows results but {target_domain} doesn't, the EAN search is working correctly.")
    print("You can now configure your .env file with PRODUCT_EAN=SS051203000")

if __name__ == "__main__":
    test_ean_search()


