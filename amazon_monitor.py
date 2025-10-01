"""Amazon product availability monitor."""

import requests
import time
import logging
import smtplib
import subprocess
import platform
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from config import Config

class AmazonMonitor:
    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.config.LOG_LEVEL),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('amazon_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def search_amazon(self, search_term=None, ean=None, domain=None):
        """Search Amazon for the specified product."""
        if ean:
            search_term = ean
            self.logger.info(f"Searching Amazon by EAN: {ean}")
        else:
            search_term = search_term or self.config.PRODUCT_SEARCH_TERM
            self.logger.info(f"Searching Amazon for: {search_term}")
        
        target_domain = domain or self.config.AMAZON_DOMAIN
        search_url = f"https://www.{target_domain}/s?k={quote_plus(search_term)}"
        
        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html5lib')
            return self.parse_search_results(soup, is_ean_search=bool(ean))
            
        except requests.RequestException as e:
            self.logger.error(f"Error searching Amazon: {e}")
            return None
            
    def parse_search_results(self, soup, is_ean_search=False):
        """Parse Amazon search results to find product availability."""
        products = []
        
        # Look for product containers in search results - try multiple selectors
        product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        if not product_containers:
            # Alternative selectors for different Amazon layouts
            product_containers = soup.find_all('div', class_='s-result-item')
        
        self.logger.info(f"Found {len(product_containers)} product containers")
        
        for i, container in enumerate(product_containers[:10]):  # Check first 10 results
            try:
                # Extract product title - try multiple selectors
                title_elem = (
                    container.find('h2', class_='a-size-mini') or 
                    container.find('span', class_='a-size-medium') or
                    container.find('h2') or
                    container.find('span', {'data-component-type': 's-product-title'}) or
                    container.find('a', {'data-component-type': 's-product-title'})
                )
                
                if not title_elem:
                    self.logger.debug(f"Container {i}: No title found")
                    continue
                    
                title = title_elem.get_text(strip=True)
                self.logger.debug(f"Container {i}: Found title: {title[:50]}...")
                
                # For EAN searches, we're more lenient but filter out irrelevant results
                # For text searches, we use the keyword matching
                if is_ean_search:
                    # Filter out irrelevant results for EAN searches
                    irrelevant_terms = ['do you need help', 'no results for', 'help', 'customer service']
                    if any(term in title.lower() for term in irrelevant_terms):
                        self.logger.debug(f"Container {i}: Skipping irrelevant EAN result: {title[:30]}...")
                        continue
                    
                    # Verify this is actually a Suunto product for EAN searches
                    if not self.is_suunto_product(title):
                        self.logger.debug(f"Container {i}: EAN result is not a Suunto product: {title[:50]}...")
                        continue
                    
                    self.logger.info(f"Found Suunto EAN product: {title[:50]}...")
                elif self.is_target_product(title):
                    self.logger.info(f"Found matching product: {title[:50]}...")
                else:
                    self.logger.debug(f"Container {i}: Title doesn't match target product")
                    continue
                
                # Extract product URL
                link_elem = (
                    container.find('a', class_='a-link-normal') or
                    container.find('a', {'data-component-type': 's-product-title'}) or
                    container.find('a', href=True)
                )
                
                if link_elem:
                    href = link_elem.get('href')
                    if href.startswith('/'):
                        product_url = f"https://www.{self.config.AMAZON_DOMAIN}{href}"
                    else:
                        product_url = href
                    
                    # Check availability
                    availability = self.check_availability(container)
                    
                    products.append({
                        'title': title,
                        'url': product_url,
                        'available': availability['available'],
                        'status': availability['status'],
                        'price': availability.get('price', 'N/A')
                    })
                    
                    self.logger.info(f"Added product: {title[:30]}... - Available: {availability['available']}")
                        
            except Exception as e:
                self.logger.warning(f"Error parsing product container {i}: {e}")
                continue
                
        self.logger.info(f"Parsed {len(products)} matching products")
        return products
        
    def is_suunto_product(self, title):
        """Check if the product is a Suunto watch (for EAN search verification)."""
        title_lower = title.lower()
        
        # Must contain "suunto" brand name
        if 'suunto' not in title_lower:
            return False
        
        # Should be a watch/sports device (not accessories, bands, etc.)
        watch_indicators = [
            'watch', 'gps', 'sports', 'fitness', 'tracker', 'monitor',
            'race', 'core', 'traverse', 'spartan', 'ambit', 'quest',
            'baro', '9', '5', '3', 'peak', 'vertical'
        ]
        
        # Check if it contains watch-related terms
        has_watch_indicators = any(indicator in title_lower for indicator in watch_indicators)
        
        # Exclude accessories and non-watch items
        exclude_terms = [
            'band', 'strap', 'charger', 'cable', 'case', 'cover',
            'screen protector', 'mount', 'bracket', 'adapter',
            'manual', 'guide', 'book', 'software', 'app'
        ]
        
        has_exclude_terms = any(term in title_lower for term in exclude_terms)
        
        is_suunto_watch = has_watch_indicators and not has_exclude_terms
        
        self.logger.debug(f"Suunto verification - Title: '{title[:50]}...' - Watch indicators: {has_watch_indicators} - Exclude terms: {has_exclude_terms} - Is Suunto watch: {is_suunto_watch}")
        
        return is_suunto_watch

    def is_target_product(self, title):
        """Check if the product title matches our target product."""
        title_lower = title.lower()
        search_term_lower = self.config.PRODUCT_SEARCH_TERM.lower()
        
        # Split the search term into keywords
        search_keywords = search_term_lower.split()
        
        # Check if most keywords are present
        matches = sum(1 for keyword in search_keywords if keyword in title_lower)
        
        # For "suunto race", we need at least 2 matches
        # For longer terms, we need at least 75% of keywords
        min_matches = max(2, int(len(search_keywords) * 0.75))
        
        is_match = matches >= min_matches
        self.logger.debug(f"Title: '{title[:50]}...' - Keywords: {search_keywords} - Matches: {matches}/{len(search_keywords)} - Match: {is_match}")
        
        return is_match
        
    def check_availability(self, container):
        """Check product availability from search result container."""
        # Look for availability indicators
        availability_text = ""
        
        # Check for "Add to Cart" button
        add_to_cart = container.find('input', {'name': 'submit.add-to-cart'})
        if add_to_cart:
            return {'available': True, 'status': 'In Stock - Add to Cart'}
            
        # Check for "Buy Now" button
        buy_now = container.find('input', {'name': 'submit.buy-now'})
        if buy_now:
            return {'available': True, 'status': 'In Stock - Buy Now'}
            
        # Check for price elements (if price is shown, usually means available)
        price_elem = (
            container.find('span', class_='a-price-whole') or
            container.find('span', class_='a-offscreen') or
            container.find('span', class_='a-color-price') or
            container.find('span', {'data-a-color': 'price'})
        )
        
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            if price_text and '€' in price_text:
                return {'available': True, 'status': f'In Stock - Price: {price_text}', 'price': price_text}
        
        # Check for availability text
        availability_elem = container.find('span', class_='a-color-price')
        if availability_elem:
            availability_text = availability_elem.get_text(strip=True)
            
        # Check for out of stock indicators
        out_of_stock_indicators = [
            'temporarily out of stock',
            'currently unavailable',
            'out of stock',
            'niet op voorraad',
            'tijdelijk niet leverbaar',
            'niet beschikbaar',
            'uitverkocht'
        ]
        
        container_text = container.get_text().lower()
        for indicator in out_of_stock_indicators:
            if indicator in container_text:
                return {'available': False, 'status': f'Out of Stock - {indicator}'}
                
        # If we can't determine availability from search results,
        # assume it's available (since it appeared in search results)
        return {'available': True, 'status': 'Likely Available - Found in search results'}
        
    def check_product_page(self, product_url):
        """Check detailed availability on product page."""
        try:
            self.logger.info(f"Checking product page: {product_url}")
            response = self.session.get(product_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html5lib')
            
            # Look for "Add to Cart" button
            add_to_cart = soup.find('input', {'id': 'add-to-cart-button'})
            if add_to_cart and not add_to_cart.get('disabled'):
                return {'available': True, 'status': 'In Stock'}
                
            # Look for availability message
            availability = soup.find('div', {'id': 'availability'})
            if availability:
                availability_text = availability.get_text(strip=True)
                return {'available': False, 'status': availability_text}
                
            # Look for price (if price is shown, usually means available)
            price = soup.find('span', {'id': 'priceblock_dealprice'}) or soup.find('span', {'id': 'priceblock_ourprice'})
            if price:
                return {'available': True, 'status': 'In Stock - Price Available'}
                
            return {'available': False, 'status': 'Not Available'}
            
        except requests.RequestException as e:
            self.logger.error(f"Error checking product page: {e}")
            return {'available': None, 'status': f'Error: {e}'}
            
    def send_native_notification(self, products):
        """Send native macOS notification about available products."""
        try:
            available_products = [p for p in products if p['available']]
            
            if not available_products:
                return
                
            # Create notification message
            title = "🚨 Suunto Race 2 Titanium Trail Available!"
            message = f"Found {len(available_products)} available product(s) on {self.config.AMAZON_DOMAIN}"
            
            # Add product details to message
            if len(available_products) == 1:
                product = available_products[0]
                message += f"\n\n{product['title'][:50]}..."
                if product.get('price') and product['price'] != 'N/A':
                    message += f"\nPrice: {product['price']}"
            else:
                message += f"\n\nClick to see all {len(available_products)} products"
            
            # Send native macOS notification using osascript
            if platform.system() == "Darwin":  # macOS
                # Try multiple notification methods in order: Banner first, then Voice
                banner_success = False
                voice_success = False
                
                # Method 1: Try terminal-notifier banner with clickable link (preferred order: 2nd)
                try:
                    # Get the first available product URL for the clickable link
                    product_url = None
                    if available_products:
                        product_url = available_products[0]['url']
                    
                    # Use terminal-notifier for better banner notifications with clickable link
                    if product_url:
                        subprocess.run([
                            'terminal-notifier',
                            '-title', title,
                            '-message', message,
                            '-sound', 'Glass',
                            '-open', product_url,
                            '-appIcon', '/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/AlertNoteIcon.icns'
                        ], check=True, timeout=5)
                        self.logger.info(f"Terminal-notifier banner with clickable link sent successfully! URL: {product_url}")
                    else:
                        # Fallback without URL if no product URL available
                        subprocess.run([
                            'terminal-notifier',
                            '-title', title,
                            '-message', message,
                            '-sound', 'Glass',
                            '-appIcon', '/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/AlertNoteIcon.icns'
                        ], check=True, timeout=5)
                        self.logger.info("Terminal-notifier banner sent successfully!")
                    banner_success = True
                except Exception as e:
                    self.logger.debug(f"Terminal-notifier banner failed: {e}")
                    
                    # Fallback to osascript banner
                    try:
                        escaped_title = title.replace('"', '\\"')
                        escaped_message = message.replace('"', '\\"')
                        
                        applescript = f'''
                        display notification "{escaped_message}" with title "{escaped_title}" sound name "Glass"
                        '''
                        
                        subprocess.run(['osascript', '-e', applescript], check=True, timeout=5)
                        self.logger.info("Fallback banner notification sent successfully!")
                        banner_success = True
                    except Exception as e2:
                        self.logger.debug(f"Fallback banner notification failed: {e2}")
                
                # Method 2: Audio notification (preferred order: 3rd)
                try:
                    audio_message = f"Amazon monitor alert. Suunto Race 2 Titanium Trail is now available on Amazon."
                    subprocess.run(['say', audio_message], check=True, timeout=10)
                    self.logger.info("Audio notification sent successfully!")
                    voice_success = True
                except Exception as e:
                    self.logger.warning(f"Audio notification failed: {e}")
                
                # Method 3: Fallback to dialog popup if both banner and voice fail
                if not banner_success and not voice_success:
                    try:
                        dialog_message = f"{title}\n\n{message}\n\nClick OK to acknowledge."
                        escaped_dialog = dialog_message.replace('"', '\\"')
                        
                        applescript = f'''
                        display dialog "{escaped_dialog}" with title "Amazon Monitor Alert" buttons {{"OK"}} default button "OK" with icon note
                        '''
                        
                        subprocess.run(['osascript', '-e', applescript], check=True, timeout=10)
                        self.logger.info("System dialog notification sent successfully!")
                    except Exception as e:
                        self.logger.error(f"System dialog notification failed: {e}")
                
                if not banner_success and not voice_success:
                    self.logger.error("All notification methods failed!")
            else:
                self.logger.warning("Native notifications only supported on macOS")
            
        except Exception as e:
            self.logger.error(f"Error sending native notification: {e}")
            
    def send_email_notification(self, products):
        """Send email notification about available products."""
        if not self.config.EMAIL_USER or not self.config.EMAIL_PASSWORD:
            self.logger.warning("Email credentials not configured. Skipping email notification.")
            return
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.EMAIL_USER
            msg['To'] = self.config.NOTIFICATION_EMAIL
            msg['Subject'] = f"🚨 Suunto Race 2 Titanium Trail Available on {self.config.AMAZON_DOMAIN}!"
            
            body = "Great news! The Suunto Race 2 Titanium Trail is now available:\n\n"
            
            for product in products:
                if product['available']:
                    body += f"✅ {product['title']}\n"
                    body += f"   Status: {product['status']}\n"
                    body += f"   Price: {product.get('price', 'N/A')}\n"
                    body += f"   URL: {product['url']}\n\n"
                    
            body += "\nHurry up and grab yours before it's gone again!"
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT)
            server.starttls()
            server.login(self.config.EMAIL_USER, self.config.EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(self.config.EMAIL_USER, self.config.NOTIFICATION_EMAIL, text)
            server.quit()
            
            self.logger.info("Email notification sent successfully!")
            
        except Exception as e:
            self.logger.error(f"Error sending email notification: {e}")
            
    def send_telegram_notification(self, products):
        """Send Telegram notification about available products."""
        if not self.config.TELEGRAM_BOT_TOKEN or not self.config.TELEGRAM_CHAT_ID:
            self.logger.warning("Telegram credentials not configured. Skipping Telegram notification.")
            return
            
        try:
            available_products = [p for p in products if p['available']]
            
            if not available_products:
                return
                
            # Create Telegram message
            message = f"🚨 *Suunto Race 2 Titanium Trail Available!*\n\n"
            message += f"Found {len(available_products)} available product(s) on {self.config.AMAZON_DOMAIN}:\n\n"
            
            for i, product in enumerate(available_products, 1):
                message += f"{i}. *{product['title'][:60]}...*\n"
                message += f"   Status: {product['status']}\n"
                if product.get('price') and product['price'] != 'N/A':
                    message += f"   Price: {product['price']}\n"
                message += f"   [View on Amazon]({product['url']})\n\n"
                
            message += "Hurry up and grab yours before it's gone again! 🏃‍♂️"
            
            # Send to Telegram
            telegram_url = f"https://api.telegram.org/bot{self.config.TELEGRAM_BOT_TOKEN}/sendMessage"
            
            payload = {
                'chat_id': self.config.TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': False
            }
            
            response = self.session.post(telegram_url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.logger.info("Telegram notification sent successfully!")
            
        except Exception as e:
            self.logger.error(f"Error sending Telegram notification: {e}")
            
    def send_notification(self, products):
        """Send notifications based on configuration."""
        notification_types = [nt.strip().lower() for nt in self.config.NOTIFICATION_TYPE.split(',')]
        
        # Send notifications in preferred order: 1. Telegram, 2. Banner, 3. Voice
        if 'telegram' in notification_types:
            self.send_telegram_notification(products)
            
        if 'email' in notification_types:
            self.send_email_notification(products)
            
        if 'native' in notification_types:
            self.send_native_notification(products)
            
    def monitor(self):
        """Main monitoring function."""
        self.logger.info("Starting Amazon product monitoring...")
        
        # Determine search method
        if self.config.PRODUCT_EAN:
            self.logger.info(f"Using EAN-based monitoring: {self.config.PRODUCT_EAN}")
            search_method = "EAN"
        else:
            self.logger.info(f"Using text-based monitoring: {self.config.PRODUCT_SEARCH_TERM}")
            search_method = "TEXT"
        
        while True:
            try:
                # Search for the product
                if search_method == "EAN":
                    products = self.search_amazon(ean=self.config.PRODUCT_EAN)
                else:
                    products = self.search_amazon(self.config.PRODUCT_SEARCH_TERM)
                
                if products:
                    available_products = [p for p in products if p['available']]
                    
                    if available_products:
                        self.logger.info(f"Found {len(available_products)} available products!")
                        self.send_notification(available_products)
                    else:
                        self.logger.info("Product not available yet. Continuing to monitor...")
                        
                    # Log all found products for debugging
                    for product in products:
                        self.logger.info(f"Product: {product['title'][:50]}... - Available: {product['available']}")
                else:
                    self.logger.warning("No products found in search results")
                    
            except Exception as e:
                self.logger.error(f"Error during monitoring cycle: {e}")
                
            # Wait before next check
            self.logger.info(f"Waiting {self.config.CHECK_INTERVAL_MINUTES} minutes before next check...")
            time.sleep(self.config.CHECK_INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    monitor = AmazonMonitor()
    monitor.monitor()
