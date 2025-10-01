# Amazon Product Monitor

A Python application to monitor Amazon.nl for product availability and send email notifications when items become available.

## Features

- 🔍 Searches Amazon.nl for specific products
- 🔔 **Native macOS notifications** - Get instant alerts on your Mac
- 📧 Optional email notifications (configurable)
- ⏰ Configurable monitoring intervals
- 📝 Comprehensive logging
- 🛡️ Respects rate limits and handles errors gracefully
- 🎯 Smart product matching for accurate results

## Setup

### Quick Setup (Recommended)

Run the automated setup script:

```bash
./setup.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Create a configuration file
- Test notifications

### Manual Setup

If you prefer to set up manually:

#### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2. Configure Environment

```bash
cp env_example.txt .env
```

Edit `.env` with your configuration:

```env
# Notification Configuration
NOTIFICATION_TYPE=native  # Options: 'native', 'email', or 'both'

# Email Configuration (only needed if NOTIFICATION_TYPE is 'email' or 'both')
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
NOTIFICATION_EMAIL=your-email@gmail.com

# Monitoring Configuration
CHECK_INTERVAL_MINUTES=15
PRODUCT_SEARCH_TERM=suunto race 2 titanium trail
AMAZON_DOMAIN=amazon.nl
```

#### 3. Notification Setup

**For Native macOS Notifications (Recommended):**
- No additional setup required! The app will use your Mac's built-in notification system
- Make sure notifications are enabled for Terminal/Python in System Preferences > Notifications

**For Email Notifications (Optional):**
- Enable 2-factor authentication on your Gmail account
- Generate an "App Password" for this application
- Use the app password in the `EMAIL_PASSWORD` field

## Usage

### Quick Start

After running `./setup.sh`, simply start monitoring:

```bash
./start_monitor.sh
```

### Manual Start

If you prefer to start manually:

```bash
source venv/bin/activate
python run_monitor.py
```

The application will:
1. Search Amazon.nl for "suunto race 2 titanium trail"
2. Check availability of matching products
3. Send native macOS notification if any are available
4. Wait 15 minutes (configurable) and repeat

### Stop the Monitor

Press `Ctrl+C` to stop the monitoring.

## Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `NOTIFICATION_TYPE` | How to notify: 'native', 'email', or 'both' | native |
| `CHECK_INTERVAL_MINUTES` | How often to check for availability | 15 |
| `PRODUCT_SEARCH_TERM` | What to search for on Amazon | suunto race 2 titanium trail |
| `AMAZON_DOMAIN` | Which Amazon domain to monitor | amazon.nl |
| `LOG_LEVEL` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) | INFO |

## Logs

The application creates detailed logs in `amazon_monitor.log` including:
- Search results
- Product availability status
- Email notifications sent
- Errors and warnings

## How It Works

1. **Search**: Uses Amazon's search functionality to find products matching your criteria
2. **Filter**: Identifies products that match the Suunto Race 2 Titanium Trail
3. **Check Availability**: Determines if products are in stock or available for purchase
4. **Notify**: Sends email alert if any matching products are available
5. **Repeat**: Waits and checks again at the configured interval

## Troubleshooting

### No Products Found
- Check your internet connection
- Verify the search term is correct
- Amazon may have changed their page structure

### Notifications Not Working
- **Native notifications**: Check System Preferences > Notifications > Terminal (or Python) to ensure notifications are enabled
- **Email notifications**: Verify your email credentials, check that 2FA is enabled and you're using an app password

### Rate Limiting
- The app includes delays between requests
- If you get blocked, increase the `CHECK_INTERVAL_MINUTES`

## Legal Notice

This tool is for personal use only. Please respect Amazon's Terms of Service and robots.txt. The application includes reasonable delays between requests to avoid overloading Amazon's servers.

## Customization

To monitor different products:
1. Change `PRODUCT_SEARCH_TERM` in your `.env` file
2. Modify the `is_target_product()` method in `amazon_monitor.py` if needed for different matching logic

To use different notification methods:
- Modify the `send_notification()` method to add SMS, Slack, or other notification channels
