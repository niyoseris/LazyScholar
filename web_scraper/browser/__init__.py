"""
Browser Module - Handles browser setup, configuration, and management for web scraping.
"""

import os
import time
import logging
import platform
from typing import Optional, Any, Dict, Tuple
from datetime import datetime

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import Selenium components
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.safari.options import Options as SafariOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.safari.service import Service as SafariService
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import (
        TimeoutException, 
        NoSuchElementException, 
        WebDriverException,
        StaleElementReferenceException
    )
    
    # Try to import webdriver manager
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        from webdriver_manager.firefox import GeckoDriverManager
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        WEBDRIVER_MANAGER_AVAILABLE = True
    except ImportError:
        WEBDRIVER_MANAGER_AVAILABLE = False
        logger.warning("webdriver-manager not available. Will use system drivers.")
    
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("Selenium not available. Browser functionality will be limited.")

def setup_browser(headless: bool = True, browser_type: Optional[str] = None) -> Any:
    """
    Set up and configure a browser for web scraping.
    
    Args:
        headless: Whether to run the browser in headless mode
        browser_type: Type of browser to use ('chrome', 'firefox', 'edge', 'safari')
        
    Returns:
        WebDriver: Configured browser instance
    """
    if not SELENIUM_AVAILABLE:
        raise ImportError("Selenium is required for browser setup. Please install it with 'pip install selenium'.")
    
    # Determine browser type if not specified
    if browser_type is None:
        # Default to Chrome, but try to detect system browser
        system = platform.system()
        if system == "Darwin":  # macOS
            if os.path.exists("/Applications/Google Chrome.app"):
                browser_type = "chrome"
            elif os.path.exists("/Applications/Firefox.app"):
                browser_type = "firefox"
            elif os.path.exists("/Applications/Safari.app"):
                browser_type = "safari"
            else:
                browser_type = "chrome"  # Default
        elif system == "Windows":
            # Check for Edge first as it's built-in
            browser_type = "edge" if os.path.exists(os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'Microsoft\\Edge\\Application\\msedge.exe')) else "chrome"
        else:  # Linux or other
            browser_type = "firefox" if os.system("which firefox > /dev/null 2>&1") == 0 else "chrome"
    
    browser_type = browser_type.lower()
    
    # Set up the browser based on type
    if browser_type == "chrome":
        return setup_chrome(headless)
    elif browser_type == "firefox":
        return setup_firefox(headless)
    elif browser_type == "edge":
        return setup_edge(headless)
    elif browser_type == "safari":
        return setup_safari(headless)
    else:
        logger.warning(f"Unsupported browser type: {browser_type}. Falling back to Chrome.")
        return setup_chrome(headless)

def setup_chrome(headless: bool = True) -> Any:
    """
    Set up and configure a Chrome browser.
    
    Args:
        headless: Whether to run in headless mode
        
    Returns:
        WebDriver: Configured Chrome browser instance
    """
    options = ChromeOptions()
    
    if headless:
        options.add_argument("--headless=new")
    
    # Common options for web scraping
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    
    # Set user agent to avoid detection
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Experimental options to avoid detection
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Create service and driver
    if WEBDRIVER_MANAGER_AVAILABLE:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)
    
    # Execute CDP commands to avoid detection
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
    })
    
    return driver

def setup_firefox(headless: bool = True) -> Any:
    """
    Set up and configure a Firefox browser.
    
    Args:
        headless: Whether to run in headless mode
        
    Returns:
        WebDriver: Configured Firefox browser instance
    """
    options = FirefoxOptions()
    
    if headless:
        options.add_argument("--headless")
    
    # Common options for web scraping
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")
    options.set_preference("dom.webnotifications.enabled", False)
    options.set_preference("dom.push.enabled", False)
    
    # Set user agent to avoid detection
    options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0")
    
    # Disable WebDriver mode
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    
    # Create service and driver
    if WEBDRIVER_MANAGER_AVAILABLE:
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
    else:
        driver = webdriver.Firefox(options=options)
    
    return driver

def setup_edge(headless: bool = True) -> Any:
    """
    Set up and configure a Microsoft Edge browser.
    
    Args:
        headless: Whether to run in headless mode
        
    Returns:
        WebDriver: Configured Edge browser instance
    """
    options = EdgeOptions()
    
    if headless:
        options.add_argument("--headless=new")
    
    # Common options for web scraping
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    
    # Set user agent to avoid detection
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0")
    
    # Experimental options to avoid detection
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Create service and driver
    if WEBDRIVER_MANAGER_AVAILABLE:
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
    else:
        driver = webdriver.Edge(options=options)
    
    # Execute CDP commands to avoid detection
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
    })
    
    return driver

def setup_safari(headless: bool = True) -> Any:
    """
    Set up and configure a Safari browser.
    Note: Safari does not support headless mode.
    
    Args:
        headless: Whether to run in headless mode (ignored for Safari)
        
    Returns:
        WebDriver: Configured Safari browser instance
    """
    if headless:
        logger.warning("Safari does not support headless mode. Running in normal mode.")
    
    options = SafariOptions()
    
    # Create service and driver
    service = SafariService()
    driver = webdriver.Safari(service=service, options=options)
    
    return driver

def capture_screenshot(browser: Any, filename: Optional[str] = None, directory: Optional[str] = None) -> str:
    """
    Capture a screenshot of the current browser window.
    
    Args:
        browser: WebDriver instance
        filename: Optional filename for the screenshot
        directory: Optional directory to save the screenshot
        
    Returns:
        str: Path to the saved screenshot
    """
    if not SELENIUM_AVAILABLE:
        raise ImportError("Selenium is required for capturing screenshots.")
    
    # Create directory if it doesn't exist
    if directory is None:
        directory = os.path.join(os.getcwd(), "screenshots")
    
    os.makedirs(directory, exist_ok=True)
    
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
    
    # Ensure filename has .png extension
    if not filename.endswith(".png"):
        filename += ".png"
    
    # Full path to save the screenshot
    filepath = os.path.join(directory, filename)
    
    # Capture the screenshot
    try:
        browser.save_screenshot(filepath)
        logger.info(f"Screenshot saved to {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error capturing screenshot: {e}")
        return ""

def safe_get(browser: Any, url: str, timeout: int = 30) -> bool:
    """
    Safely navigate to a URL with error handling.
    
    Args:
        browser: WebDriver instance
        url: URL to navigate to
        timeout: Timeout in seconds
        
    Returns:
        bool: True if navigation was successful, False otherwise
    """
    try:
        browser.set_page_load_timeout(timeout)
        browser.get(url)
        return True
    except TimeoutException:
        logger.warning(f"Timeout while loading {url}")
        return False
    except WebDriverException as e:
        logger.error(f"Error navigating to {url}: {e}")
        return False

def wait_for_element(browser: Any, by: str, value: str, timeout: int = 10) -> Optional[Any]:
    """
    Wait for an element to be present on the page.
    
    Args:
        browser: WebDriver instance
        by: Type of selector (e.g., By.ID, By.CSS_SELECTOR)
        value: Value of the selector
        timeout: Timeout in seconds
        
    Returns:
        WebElement or None: The element if found, None otherwise
    """
    try:
        element = WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        logger.warning(f"Timeout waiting for element {by}={value}")
        return None
    except Exception as e:
        logger.error(f"Error waiting for element {by}={value}: {e}")
        return None

def wait_for_elements(browser: Any, by: str, value: str, timeout: int = 10) -> list:
    """
    Wait for elements to be present on the page.
    
    Args:
        browser: WebDriver instance
        by: Type of selector (e.g., By.ID, By.CSS_SELECTOR)
        value: Value of the selector
        timeout: Timeout in seconds
        
    Returns:
        list: List of elements if found, empty list otherwise
    """
    try:
        elements = WebDriverWait(browser, timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )
        return elements
    except TimeoutException:
        logger.warning(f"Timeout waiting for elements {by}={value}")
        return []
    except Exception as e:
        logger.error(f"Error waiting for elements {by}={value}: {e}")
        return []

def scroll_to_element(browser: Any, element: Any) -> None:
    """
    Scroll to an element on the page.
    
    Args:
        browser: WebDriver instance
        element: WebElement to scroll to
    """
    try:
        browser.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)  # Small delay to allow the page to settle
    except Exception as e:
        logger.error(f"Error scrolling to element: {e}")

def scroll_down(browser: Any, amount: int = 300) -> None:
    """
    Scroll down the page by a specified amount.
    
    Args:
        browser: WebDriver instance
        amount: Amount to scroll in pixels
    """
    try:
        browser.execute_script(f"window.scrollBy(0, {amount});")
        time.sleep(0.5)  # Small delay to allow the page to settle
    except Exception as e:
        logger.error(f"Error scrolling down: {e}")

def scroll_to_bottom(browser: Any) -> None:
    """
    Scroll to the bottom of the page.
    
    Args:
        browser: WebDriver instance
    """
    try:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)  # Small delay to allow the page to settle
    except Exception as e:
        logger.error(f"Error scrolling to bottom: {e}")

def execute_javascript(browser: Any, script: str) -> Any:
    """
    Execute JavaScript in the browser.
    
    Args:
        browser: WebDriver instance
        script: JavaScript code to execute
        
    Returns:
        Any: Result of the JavaScript execution
    """
    try:
        return browser.execute_script(script)
    except Exception as e:
        logger.error(f"Error executing JavaScript: {e}")
        return None

def close_browser(browser: Any) -> None:
    """
    Safely close a browser instance.
    
    Args:
        browser: The browser instance to close
    """
    if browser is None:
        logger.warning("Attempted to close a None browser instance")
        return
    
    try:
        browser.quit()
        logger.info("Browser closed successfully")
    except Exception as e:
        logger.error(f"Error closing browser: {e}")
        print(f"Error closing browser: {e}")
