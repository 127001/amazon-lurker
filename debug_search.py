#!/usr/bin/env python3
"""Debug script to test Amazon search functionality."""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import time

def test_amazon_search(search_term, domain="amazon.de"):
    """Test Amazon search and debug the response."""
    print(f"🔍 Testing Amazon search for: '{search_term}'")
    print(f"🌐 Domain: {domain}")
    
    # Create session with proper headers
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    })
    
    # Build search URL
    search_url = f"https://www.{domain}/s?k={quote_plus(search_term)}"
    print(f"🔗 Search URL: {search_url}")
    
    try:
        print("📡 Making request to Amazon...")
        response = session.get(search_url, timeout=10)
        print(f"📊 Response status: {response.status_code}")
        print(f"📏 Response size: {len(response.content)} bytes")
        
        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            return
            
        # Parse the response
        soup = BeautifulSoup(response.content, 'html5lib')
        
        # Look for different possible product containers
        print("\n🔍 Looking for product containers...")
        
        # Try different selectors
        selectors_to_try = [
            ('data-component-type=s-search-result', 'div[data-component-type="s-search-result"]'),
            ('class=s-result-item', 'div.s-result-item'),
            ('class=s-widget-container', 'div.s-widget-container'),
            ('class=s-main-slot', 'div.s-main-slot'),
            ('class=s-result-list', 'div.s-result-list'),
            ('class=s-search-results', 'div.s-search-results'),
        ]
        
        for name, selector in selectors_to_try:
            elements = soup.select(selector)
            print(f"  {name}: {len(elements)} found")
            
        # Look for any divs that might contain products
        all_divs = soup.find_all('div')
        print(f"\n📦 Total divs found: {len(all_divs)}")
        
        # Look for common Amazon product indicators
        print("\n🔍 Looking for Amazon-specific elements...")
        
        # Check for "Add to Cart" buttons
        add_to_cart = soup.find_all('input', {'name': 'submit.add-to-cart'})
        print(f"  Add to Cart buttons: {len(add_to_cart)}")
        
        # Check for product titles
        titles = soup.find_all(['h2', 'span'], class_=lambda x: x and 'title' in x.lower() if x else False)
        print(f"  Potential titles: {len(titles)}")
        
        # Check for price elements
        prices = soup.find_all('span', class_=lambda x: x and 'price' in x.lower() if x else False)
        print(f"  Potential prices: {len(prices)}")
        
        # Look for "No results" or similar messages
        no_results = soup.find_all(text=lambda text: text and 'no results' in text.lower())
        if no_results:
            print(f"\n❌ Found 'no results' messages: {len(no_results)}")
            for msg in no_results[:3]:  # Show first 3
                print(f"  - {msg.strip()}")
        
        # Save a sample of the HTML for inspection
        with open('amazon_response_sample.html', 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()[:5000]))  # First 5000 chars
        print(f"\n💾 Saved sample HTML to 'amazon_response_sample.html'")
        
        # Look for any text that might indicate what we're searching for
        search_lower = search_term.lower()
        found_terms = []
        for term in search_lower.split():
            if term in soup.get_text().lower():
                found_terms.append(term)
        
        print(f"\n🔍 Search terms found in page: {found_terms}")
        
        # Check if we got redirected or blocked
        final_url = response.url
        if final_url != search_url:
            print(f"\n🔄 Redirected to: {final_url}")
            
        # Check for captcha or blocking
        if 'captcha' in soup.get_text().lower():
            print("\n🤖 CAPTCHA detected!")
        if 'robot' in soup.get_text().lower():
            print("\n🤖 Robot detection message found!")
            
    except Exception as e:
        print(f"❌ Error during search: {e}")

def test_different_search_terms():
    """Test with different search terms to see what works."""
    test_terms = [
        "suunto race 2 titanium trail",
        "suunto race",
        "suunto",
        "apple watch",  # Common product that should be found
        "iphone",       # Very common product
    ]
    
    for term in test_terms:
        print(f"\n{'='*60}")
        test_amazon_search(term)
        print(f"{'='*60}")
        time.sleep(2)  # Be nice to Amazon

if __name__ == "__main__":
    print("🐛 Amazon Search Debug Tool")
    print("This will help us understand why the search isn't working\n")
    
    # Test with a simple term first
    test_amazon_search("apple watch")
    
    print("\n" + "="*60)
    print("If you want to test more terms, uncomment the line below:")
    print("# test_different_search_terms()")


