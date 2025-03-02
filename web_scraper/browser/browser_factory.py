"""
Browser factory module for creating browser instances.
"""

import os
import sys
import logging
import tempfile
from typing import Optional, Any

# Configure logger
logger = logging.getLogger(__name__)

def create_browser(browser_type: str = "chrome", headless: bool = False, user_data_dir: Optional[str] = None) -> Any:
    """
    Create and return a browser instance.
    
    Args:
        browser_type: Type of browser to create (chrome, firefox, or safari)
        headless: Whether to run the browser in headless mode
        user_data_dir: Directory to store user data
        
    Returns:
        Browser instance
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
    except ImportError as e:
        logger.error(f"Error importing Selenium: {e}")
        print("Error: Selenium is required for browser automation.")
        print("Please install it with: pip install selenium")
        sys.exit(1)
    
    # Try to import webdriver managers
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        chrome_manager_available = True
    except ImportError:
        chrome_manager_available = False
        logger.warning("ChromeDriverManager not available. Chrome browser might not work.")
    
    try:
        from webdriver_manager.firefox import GeckoDriverManager
        firefox_manager_available = True
    except ImportError:
        firefox_manager_available = False
        logger.warning("GeckoDriverManager not available. Firefox browser might not work.")
    
    # Normalize browser type
    browser_type = browser_type.lower()
    
    # Create a browser instance based on the specified type
    if browser_type == "chrome":
        return create_chrome_browser(headless, user_data_dir, chrome_manager_available)
    elif browser_type == "firefox":
        return create_firefox_browser(headless, user_data_dir, firefox_manager_available)
    elif browser_type == "safari":
        return create_safari_browser(headless)
    else:
        logger.error(f"Unsupported browser type: {browser_type}")
        print(f"Error: Unsupported browser type: {browser_type}")
        print("Supported browsers: chrome, firefox, safari")
        sys.exit(1)

def create_chrome_browser(headless: bool, user_data_dir: Optional[str], manager_available: bool) -> Any:
    """
    Create and return a Chrome browser instance.
    
    Args:
        headless: Whether to run the browser in headless mode
        user_data_dir: Directory to store user data
        manager_available: Whether ChromeDriverManager is available
        
    Returns:
        Chrome browser instance
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    
    # Set up Chrome options
    options = ChromeOptions()
    
    # Set headless mode
    if headless:
        options.add_argument("--headless=new")
    
    # Set user data directory
    if user_data_dir:
        options.add_argument(f"--user-data-dir={user_data_dir}")
    
    # Add common options
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    
    # Add user agent
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    try:
        # Create Chrome browser instance
        if manager_available:
            from webdriver_manager.chrome import ChromeDriverManager
            service = ChromeService(ChromeDriverManager().install())
            browser = webdriver.Chrome(service=service, options=options)
        else:
            browser = webdriver.Chrome(options=options)
        
        logger.info("Chrome browser created successfully")
        return browser
    except Exception as e:
        logger.error(f"Error creating Chrome browser: {e}")
        print(f"Error creating Chrome browser: {e}")
        return None

def create_firefox_browser(headless: bool, user_data_dir: Optional[str], manager_available: bool) -> Any:
    """
    Create and return a Firefox browser instance.
    
    Args:
        headless: Whether to run the browser in headless mode
        user_data_dir: Directory to store user data
        manager_available: Whether GeckoDriverManager is available
        
    Returns:
        Firefox browser instance
    """
    from selenium import webdriver
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    
    # Set up Firefox options
    options = FirefoxOptions()
    
    # Set headless mode
    if headless:
        options.add_argument("--headless")
    
    # Set user data directory
    if user_data_dir:
        options.set_preference("profile", user_data_dir)
    
    # Add common options
    options.set_preference("dom.webnotifications.enabled", False)
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    
    # Add user agent
    options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0")
    
    try:
        # Create Firefox browser instance
        if manager_available:
            from webdriver_manager.firefox import GeckoDriverManager
            service = FirefoxService(GeckoDriverManager().install())
            browser = webdriver.Firefox(service=service, options=options)
        else:
            browser = webdriver.Firefox(options=options)
        
        logger.info("Firefox browser created successfully")
        return browser
    except Exception as e:
        logger.error(f"Error creating Firefox browser: {e}")
        print(f"Error creating Firefox browser: {e}")
        return None

def create_safari_browser(headless: bool) -> Any:
    """
    Create and return a Safari browser instance.
    
    Args:
        headless: Whether to run the browser in headless mode (not supported by Safari)
        
    Returns:
        Safari browser instance
    """
    from selenium import webdriver
    
    if headless:
        logger.warning("Headless mode is not supported by Safari. Ignoring.")
    
    try:
        # Create Safari browser instance
        browser = webdriver.Safari()
        
        logger.info("Safari browser created successfully")
        return browser
    except Exception as e:
        logger.error(f"Error creating Safari browser: {e}")
        print(f"Error creating Safari browser: {e}")
        print("Note: Safari requires enabling 'Allow Remote Automation' in Safari's Develop menu.")
        return None 