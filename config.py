"""Configuration settings for Amazon product monitor."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Notification settings
    NOTIFICATION_TYPE = os.getenv('NOTIFICATION_TYPE', 'native')  # 'native', 'email', 'telegram', or combinations like 'native,telegram'
    
    # Email settings (optional)
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL')
    
    # Telegram settings (optional)
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # Monitoring settings
    CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', 15))
    PRODUCT_SEARCH_TERM = os.getenv('PRODUCT_SEARCH_TERM', 'suunto race 2 titanium trail')
    PRODUCT_EAN = os.getenv('PRODUCT_EAN', '')  # EAN for more precise searching
    AMAZON_DOMAIN = os.getenv('AMAZON_DOMAIN', 'amazon.nl')
    TEST_DOMAIN = os.getenv('TEST_DOMAIN', 'amazon.de')  # For testing with known available products
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Request settings
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    REQUEST_DELAY = 2  # seconds between requests
    MAX_RETRIES = 3
