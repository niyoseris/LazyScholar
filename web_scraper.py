"""
Web Scraper Module - Handles automated academic database searching using Selenium.
"""

import os
import sys
import time
import json
import random
import logging
import requests
import subprocess
import re
import urllib
from urllib.parse import quote_plus, urlparse, urlencode
from datetime import datetime
from io import BytesIO
import base64
import string
from typing import Dict, List, Optional, Tuple, Union, Any
from selenium.webdriver.common.keys import Keys  # Add Keys import

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import optional dependencies with clean error handling

# For handling binary data and requests
try:
    REQUESTS_AVAILABLE = True
except ImportError as e:
    REQUESTS_AVAILABLE = False
    logger.warning(f"Requests or related modules not available: {e}")

# Try to import PIL
PIL_AVAILABLE = False
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    logger.warning("PIL not available. Screenshot functionality will be limited.")

# Try to import Google Generative AI
GENAI_AVAILABLE = False
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
    logger.info("Google Generative AI module loaded successfully")
except ImportError:
    logger.warning("Google Generative AI not available. Vision-assisted searching will be disabled.")

# Try to import Selenium and related components
SELENIUM_AVAILABLE = False
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import (
        WebDriverException, 
        NoSuchElementException, 
        TimeoutException,
        ElementNotInteractableException
    )
    SELENIUM_AVAILABLE = True
    logger.info("Selenium core components available")
except ImportError as e:
    logger.warning(f"Selenium not available: {e}")

# Try to import browser-specific components
CHROME_AVAILABLE = False
try:
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    CHROME_AVAILABLE = True
    logger.info("Chrome WebDriver components available")
except ImportError:
    logger.warning("Chrome WebDriver components not available")

FIREFOX_AVAILABLE = False
try:
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.firefox.service import Service as FirefoxService
    FIREFOX_AVAILABLE = True
    logger.info("Firefox WebDriver components available")
except ImportError:
    logger.warning("Firefox WebDriver components not available")

SAFARI_AVAILABLE = False
try:
    from selenium.webdriver.safari.options import Options as SafariOptions
    from selenium.webdriver.safari.service import Service as SafariService
    SAFARI_AVAILABLE = True
    logger.info("Safari WebDriver components available")
except ImportError:
    logger.warning("Safari WebDriver components not available")

# Try to import WebDriver managers
WEBDRIVER_MANAGER_AVAILABLE = False
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
    logger.info("ChromeDriverManager available")
except ImportError:
    logger.warning("ChromeDriverManager not available")

# Try to import geckodriver autoinstaller
GECKO_AUTOINSTALLER_AVAILABLE = False
try:
    import geckodriver_autoinstaller
    GECKO_AUTOINSTALLER_AVAILABLE = True
    logger.info("geckodriver_autoinstaller available")
except ImportError:
    logger.warning("geckodriver_autoinstaller not available. Firefox browser setup may fail.")

# Try to import tkinter for UI (optional)
TKINTER_AVAILABLE = False
try:
    import tkinter as tk
    from tkinter import scrolledtext, messagebox
    TKINTER_AVAILABLE = True
    logger.info("tkinter available for UI components")
except ImportError:
    logger.warning("tkinter not available. GUI elements will be disabled.")

# Global list to track blocked sites
BLOCKED_SITES = set()
# File to persist blocked sites between runs
BLOCKED_SITES_FILE = "blocked_sites.json"

# CAPTCHA handling configuration
CAPTCHA_DETECTION_ENABLED = True
CAPTCHA_AUTO_SOLVE_ENABLED = False  # Disabled by default as it requires external services
CAPTCHA_WAIT_TIME = 60  # Default: wait up to 60 seconds for manual CAPTCHA solving
CAPTCHA_SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "captcha_screenshots")

# Create captcha_screenshots directory if it doesn't exist
os.makedirs(CAPTCHA_SCREENSHOT_DIR, exist_ok=True)

class BlockedSiteException(Exception):
    """Exception raised when a site is blocked or blocking access."""
    pass

def load_blocked_sites():
    """Load previously blocked sites from file."""
    try:
        if os.path.exists(BLOCKED_SITES_FILE):
            with open(BLOCKED_SITES_FILE, 'r') as f:
                sites = json.load(f)
                BLOCKED_SITES.update(sites)
                logger.info(f"Loaded {len(sites)} blocked sites from file")
    except Exception as e:
        logger.error(f"Error loading blocked sites: {e}")
        # Continue with empty set if file can't be loaded

def save_blocked_sites():
    """Save blocked sites to file."""
    try:
        with open(BLOCKED_SITES_FILE, 'w') as f:
            json.dump(list(BLOCKED_SITES), f)
        logger.info(f"Saved {len(BLOCKED_SITES)} blocked sites to file")
    except Exception as e:
        logger.error(f"Error saving blocked sites: {e}")

def add_to_blocked_sites(url):
    """Add a URL to the blocked sites list."""
    # Extract base domain for blocking
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    base_domain = parsed_url.netloc
    
    BLOCKED_SITES.add(base_domain)
    logger.warning(f"Added {base_domain} to blocked sites")
    save_blocked_sites()
    return base_domain

def is_site_blocked(url):
    """Check if a site is in the blocked list."""
    for pattern in BLOCKED_SITES:
        if pattern in url:
            return True
    return False

def detect_captcha(browser):
    """
    Detect if a captcha is present on the current page.
    
    Args:
        browser: Selenium WebDriver instance
        
    Returns:
        bool: True if captcha detected, False otherwise
        str: Type of captcha detected or None
    """
    page_source = browser.page_source.lower()
    
    # Common captcha indicators
    captcha_indicators = {
        "recaptcha": [
            "recaptcha", 
            "g-recaptcha", 
            "google.com/recaptcha"
        ],
        "hcaptcha": [
            "hcaptcha.com", 
            "h-captcha"
        ],
        "text_captcha": [
            "enter the characters", 
            "type the text", 
            "enter the code"
        ],
        "image_captcha": [
            "select all images",
            "select all squares",
            "click on"
        ],
        "general_captcha": [
            "captcha",
            "security check",
            "human verification",
            "verify you are human",
            "bot check"
        ]
    }
    
    # Check for captcha elements
    captcha_elements = [
        "iframe[src*='captcha']",
        "iframe[src*='recaptcha']",
        "iframe[src*='hcaptcha']",
        "div.g-recaptcha",
        "div.h-captcha",
        "div[class*='captcha']",
        "img[alt*='captcha']"
    ]
    
    # Check page source for text indicators
    for captcha_type, indicators in captcha_indicators.items():
        for indicator in indicators:
            if indicator in page_source:
                logger.info(f"Detected {captcha_type} via text indicator: {indicator}")
                return True, captcha_type
    
    # Check for captcha elements
    for selector in captcha_elements:
        try:
            elements = browser.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                logger.info(f"Detected captcha via element: {selector}")
                return True, "element_captcha"
        except Exception as e:
            # Ignore errors when searching for elements
            pass
    
    return False, None

def handle_captcha(browser, url, wait_time=None):
    """
    Handle captcha challenges on the current page.
    
    Args:
        browser: Selenium WebDriver instance
        url: Current URL being accessed
        wait_time: Optional override for CAPTCHA_WAIT_TIME (in seconds)
        
    Returns:
        bool: True if captcha was handled successfully, False otherwise
    """
    if not CAPTCHA_DETECTION_ENABLED:
        return False
        
    captcha_detected, captcha_type = detect_captcha(browser)
    
    if not captcha_detected:
        return False
        
    logger.warning(f"Captcha detected on {url} (Type: {captcha_type})")
    
    # Create a unique filename for the screenshot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(CAPTCHA_SCREENSHOT_DIR, f"captcha_{timestamp}.png")
    
    # Take a screenshot to show the captcha
    try:
        browser.save_screenshot(screenshot_path)
        logger.info(f"Captcha screenshot saved to {screenshot_path}")
    except Exception as e:
        logger.warning(f"Error saving captcha screenshot: {e}")
        screenshot_path = None
    
    if CAPTCHA_AUTO_SOLVE_ENABLED:
        # Here you would integrate with a captcha solving service
        # This is commented out as it would require external services
        """
        try:
            solution = solve_captcha_with_service(browser, captcha_type)
            if solution:
                logger.info("Captcha solved automatically")
                return True
        except Exception as e:
            logger.error(f"Auto-solve captcha error: {e}")
        """
        pass
    
    # Display a notification in the browser
    try:
        browser.execute_script("""
            const div = document.createElement('div');
            div.id = 'captcha_notification';
            div.style.position = 'fixed';
            div.style.top = '0';
            div.style.left = '0';
            div.style.width = '100%';
            div.style.backgroundColor = '#ffeb3b';
            div.style.color = '#000';
            div.style.padding = '15px';
            div.style.zIndex = '9999';
            div.style.textAlign = 'center';
            div.style.fontWeight = 'bold';
            div.style.fontSize = '18px';
            div.style.boxShadow = '0 2px 5px rgba(0,0,0,0.3)';
            div.innerHTML = '<span style="color: red; font-size: 20px;">⚠️ CAPTCHA DETECTED ⚠️</span><br>' + 
                            'Please solve the CAPTCHA manually to continue.<br>' + 
                            'The system will automatically proceed once the CAPTCHA is solved.';
            
            // Check if notification already exists
            if (!document.getElementById('captcha_notification')) {
                document.body.appendChild(div);
            }
        """)
    except Exception as e:
        logger.warning(f"Error displaying captcha notification: {e}")
    
    # Show terminal message for user
    captcha_info = f"""
{'='*80}
CAPTCHA DETECTED - USER ACTION REQUIRED
{'='*80}
A CAPTCHA has been detected on the page at: {url}
Type: {captcha_type}

Please switch to the browser window and solve the CAPTCHA manually.
The research process will automatically continue once the CAPTCHA is solved.

Screenshot saved to: {screenshot_path if screenshot_path else "Error saving screenshot"}
{'='*80}
"""
    print(captcha_info)
    
    # If system has 'say' command (macOS), use it to alert user with voice
    if platform.system() == 'Darwin':
        try:
            os.system('say "CAPTCHA detected. Please solve it to continue."')
        except:
            pass
    
    # Wait for manual solving - use provided wait_time if available
    solving_time = wait_time if wait_time is not None else CAPTCHA_WAIT_TIME
    interval = 3  # Check every 3 seconds for better responsiveness
    
    logger.info(f"Waiting up to {solving_time} seconds for manual captcha solving...")
    
    for i in range(solving_time // interval):
        time.sleep(interval)
        
        # Check if we're still on a captcha page
        still_captcha, _ = detect_captcha(browser)
        if not still_captcha:
            # Remove the notification banner if captcha is solved
            try:
                browser.execute_script("""
                    const notification = document.getElementById('captcha_notification');
                    if (notification) {
                        notification.remove();
                    }
                """)
            except:
                pass
                
            print(f"\n{'='*80}\nCAPTCHA SOLVED SUCCESSFULLY! Continuing research process...\n{'='*80}")
            if platform.system() == 'Darwin':
                try:
                    os.system('say "CAPTCHA solved. Continuing research."')
                except:
                    pass
                    
            logger.info("Captcha appears to be solved")
            return True
        
        # Print a progress indicator every few seconds
        if i % 5 == 0:
            remaining = solving_time - (i * interval)
            print(f"Waiting for CAPTCHA solution... {remaining} seconds remaining")
    
    # If we reach here, the captcha wasn't solved
    print(f"\n{'='*80}\nCAPTCHA NOT SOLVED within the {solving_time} second time limit.\nResearch process will try to continue, but may fail.\n{'='*80}")
    logger.warning("Captcha not solved within the waiting period")
    return False

def setup_browser(headless=True, browser_type=None):
    """Set up a Selenium browser for web scraping.
    
    Args:
        headless (bool): Whether to run the browser in headless mode
        browser_type (str): Type of browser to configure ('chrome', 'firefox', 'duckduckgo', etc.)
    
    Returns:
        browser: Selenium WebDriver instance or MockBrowser if Selenium is not available
        
    Note:
        Can be used as a context manager with 'with' statement:
        with setup_browser(headless=True, browser_type='duckduckgo') as browser:
            # Use browser here
    """
    
    # Create the browser instance
    browser = _create_browser(headless, browser_type)
    
    # Define a context manager class that allows this function to be used with 'with'
    class BrowserContextManager:
        def __init__(self, browser_instance):
            self.browser = browser_instance
            
        def __enter__(self):
            return self.browser
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.browser and not isinstance(self.browser, MockBrowser):
                try:
                    self.browser.quit()
                except Exception as e:
                    logger.warning(f"Error closing browser: {e}")
    
    # Add a context manager as an attribute to the browser
    browser._context_manager = BrowserContextManager(browser)
    browser.__enter__ = browser._context_manager.__enter__
    browser.__exit__ = browser._context_manager.__exit__
    
    # Return the browser with context manager capabilities
    return browser

def _create_browser(headless=True, browser_type=None):
    """Internal function to create a browser instance"""
    # Check if Selenium is available
    if not SELENIUM_AVAILABLE:
        logger.warning("Selenium not available, using mock browser for development")
        return MockBrowser()
    
    # Define common user agents
    user_agents = {
        'chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'firefox': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'safari': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
        'duckduckgo': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 DuckDuckGo/110',
    }
    
    # Get DuckDuckGo specific user agent if requested
    if browser_type == 'duckduckgo':
        logger.info("Setting up browser with DuckDuckGo configuration")
        user_agent = user_agents.get('duckduckgo')
    else:
        # Get default user agent based on browser type
        user_agent = user_agents.get(browser_type, user_agents['chrome'])
    
    # Try to set up Chrome/Chromium browser
    if CHROME_AVAILABLE:
        try:
            options = ChromeOptions()
            if headless:
                options.add_argument('--headless')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument(f'user-agent={user_agent}')
            
            # Add DuckDuckGo specific options
            if browser_type == 'duckduckgo':
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_experimental_option('excludeSwitches', ['enable-automation'])
                options.add_experimental_option('useAutomationExtension', False)
            
            if WEBDRIVER_MANAGER_AVAILABLE:
                service = ChromeService(executable_path=ChromeDriverManager().install())
                browser = webdriver.Chrome(service=service, options=options)
            else:
                # Try with the default Chrome driver location
                browser = webdriver.Chrome(options=options)
            
            # Additional setup for DuckDuckGo emulation
            if browser_type == 'duckduckgo':
                browser.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
                browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return browser
        except Exception as e:
            logger.warning(f"Chrome browser setup failed: {e}")
    
    # Try to set up Firefox browser
    if FIREFOX_AVAILABLE:
        try:
            options = FirefoxOptions()
            if headless:
                options.add_argument('--headless')
            
            options.set_preference('general.useragent.override', user_agent)
            
            # Install geckodriver if needed and available
            if GECKO_AUTOINSTALLER_AVAILABLE:
                geckodriver_autoinstaller.install()
            
            browser = webdriver.Firefox(options=options)
            
            # Additional setup for DuckDuckGo emulation for Firefox
            if browser_type == 'duckduckgo':
                browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return browser
        except Exception as e:
            logger.warning(f"Firefox browser setup failed: {e}")
    
    # Try to set up Safari browser on macOS
    if SAFARI_AVAILABLE and platform.system() == "Darwin":
        try:
            browser = webdriver.Safari()
            return browser
        except Exception as e:
            logger.warning(f"Safari browser setup failed: {e}")
    
    logger.error("All browser setup attempts failed, using mock browser")
    return MockBrowser()

class MockBrowser:
    """A mock browser class for testing."""
    
    def __init__(self, visible=False):
        self.visible = visible
        self.current_url = None
        self.page_source = ""
        logger.info("Mock browser created" + (" (visible mode)" if visible else ""))
        
        # Create a simple visual indicator if in visible mode
        if visible and TKINTER_AVAILABLE:
            try:
                self.window = tk.Tk()
                self.window.title("Mock Browser - Demo Mode")
                self.window.geometry("800x600")
                
                self.url_entry = tk.Entry(self.window, width=70)
                self.url_entry.pack(pady=10, padx=10)
                self.url_entry.insert(0, "https://demo-mode.example.com")
                
                self.browser_content = scrolledtext.ScrolledText(self.window, width=90, height=30)
                self.browser_content.pack(pady=10, padx=10)
                self.browser_content.insert(tk.END, "Mock Browser in Demo Mode\n\nNo real browser is available.\nThis is a simulated environment for testing purposes.")
                
                self.status_label = tk.Label(self.window, text="Status: Ready (Demo Mode)")
                self.status_label.pack(pady=5)
                
                # Schedule updates
                self.window.update()
            except Exception as e:
                logger.error(f"Error setting up tkinter UI: {e}")
                self.window = None
        else:
            if visible and not TKINTER_AVAILABLE:
                logger.warning("Visible mode requested but tkinter is not available. Using console-only mode.")
            self.window = None
    
    def get(self, url):
        """Simulate browser navigation to URL."""
        logger.info(f"Mock browser navigating to: {url}")
        self.current_url = url
        self.page_source = self._generate_mock_page_source(url)
        
        # Update the UI if in visible mode
        if self.visible and self.window and TKINTER_AVAILABLE:
            try:
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, url)
                self.browser_content.delete(1.0, tk.END)
                self.browser_content.insert(tk.END, f"Simulated content for: {url}\n\n{self._generate_mock_content(url)}")
                self.status_label.config(text=f"Status: Loaded {url} (Demo Mode)")
                self.window.update()
                # Simulate loading delay
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Error updating mock browser UI: {e}")
        
        return self
    
    def find_element(self, by, value):
        """Mock find_element method that returns a MockElement."""
        logger.info(f"Mock browser finding element: {by}={value}")
        return MockElement(self, by, value)
    
    def find_elements(self, by, value):
        """Mock find_elements method that returns a list of MockElements."""
        logger.info(f"Mock browser finding elements: {by}={value}")
        return [MockElement(self, by, value, index=i) for i in range(random.randint(3, 8))]
    
    def close(self):
        """Simulate closing the browser."""
        logger.info("Mock browser closed")
        if self.visible and self.window:
            try:
                self.window.destroy()
            except:
                pass
    
    def quit(self):
        """Simulate quitting the browser."""
        logger.info("Mock browser quit")
        self.close()
    
    def refresh(self):
        """Simulate refreshing the page."""
        logger.info("Mock browser refreshed")
        if self.current_url:
            self.get(self.current_url)
    
    def switch_to(self):
        """Provide a mock switch_to interface."""
        return MockSwitchTo(self)
        
    def execute_script(self, script, *args):
        """Mock execute_script method that logs the script and returns a default value."""
        logger.info(f"Mock browser executing script: {script[:50]}...")
        return None
    
    def save_screenshot(self, filename):
        """Mock save_screenshot method that creates a simple screenshot file."""
        logger.info(f"Mock browser saving screenshot to: {filename}")
        
        # Create a very simple image (solid color with text) if PIL is available
        try:
            if PIL_AVAILABLE:
                width, height = 800, 600
                img = Image.new('RGB', (width, height), color=(240, 240, 240))
                d = ImageDraw.Draw(img)
                d.text((10, 10), f"Mock Screenshot - {self.current_url}", fill=(0, 0, 0))
                d.text((10, 30), f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fill=(0, 0, 0))
                d.rectangle([(50, 100), (750, 500)], outline="black")
                d.text((400, 300), "Mock Content", fill=(100, 100, 100))
                img.save(filename)
                return True
            else:
                # If PIL is not available, create an empty file
                with open(filename, 'w') as f:
                    f.write("Mock screenshot (PIL not available)")
                return True
        except Exception as e:
            logger.error(f"Error creating mock screenshot: {e}")
            # Fall back to creating an empty file
            try:
                with open(filename, 'w') as f:
                    f.write(f"Mock screenshot - Error: {str(e)}")
                return True
            except:
                logger.error(f"Could not create screenshot file at all: {filename}")
                return False
    
    def _generate_mock_page_source(self, url):
        """Generate mock HTML content based on the URL."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mock Page - {url}</title>
        </head>
        <body>
            <h1>Mock Browser Content</h1>
            <p>This is simulated content for: {url}</p>
            <div id="search-results">
                {self._generate_mock_content(url)}
            </div>
        </body>
        </html>
        """
    
    def _generate_mock_content(self, url):
        """Generate relevant mock content based on the URL."""
        if "scholar.google.com" in url or "academic" in url:
            return self._generate_mock_academic_results()
        elif "search" in url:
            return self._generate_mock_search_results()
        else:
            return "<p>Generic mock content for testing purposes.</p>"
    
    def _generate_mock_academic_results(self):
        """Generate mock academic search results."""
        result_html = "<h2>Mock Academic Search Results</h2>"
        
        titles = [
            "Advances in Machine Learning: A Comprehensive Review",
            "Artificial Intelligence in Healthcare: Current Applications and Future Perspectives",
            "Deep Learning Approaches for Natural Language Processing",
            "Ethical Considerations in AI Development",
            "Quantum Computing: Principles and Applications",
            "Blockchain Technology: Beyond Cryptocurrencies",
            "The Internet of Things: Challenges and Opportunities",
            "Cybersecurity in the Age of Big Data",
            "Neural Networks and Their Applications in Image Recognition",
            "Sustainable Computing: Energy-Efficient Algorithms and Systems"
        ]
        
        authors = [
            "Smith, J. & Johnson, A.",
            "Williams, R. et al.",
            "Brown, M., Davis, L. & Wilson, T.",
            "Miller, S. & Anderson, K.",
            "Taylor, E., Moore, C. & White, R.",
            "Thomas, P. & Jackson, D.",
            "Harris, B. et al.",
            "Clark, F. & Lewis, N.",
            "Young, H., Walker, G. & Allen, J.",
            "King, M. & Wright, S."
        ]
        
        journals = [
            "Journal of Computer Science",
            "IEEE Transactions on Pattern Analysis",
            "Nature Digital Intelligence",
            "Proceedings of the National Academy of Sciences",
            "Journal of Artificial Intelligence Research",
            "ACM Computing Surveys",
            "Science Advances",
            "Communications of the ACM",
            "International Journal of Machine Learning",
            "Computational Intelligence and Neuroscience"
        ]
        
        years = list(range(2018, 2025))
        
        for i in range(5):
            title = random.choice(titles)
            author = random.choice(authors)
            journal = random.choice(journals)
            year = random.choice(years)
            
            result_html += f"""
            <div class="gs_ri">
                <h3 class="gs_rt"><a href="#">{title}</a></h3>
                <div class="gs_a">{author} - {journal}, {year}</div>
                <div class="gs_rs">This is a mock abstract for "{title}". It contains simulated content describing research findings, methodology, and conclusions related to the topic of the paper.</div>
                <div class="gs_fl">Cited by {random.randint(5, 500)} - Related articles - View PDF</div>
            </div>
            """
        
        return result_html
    
    def _generate_mock_search_results(self):
        """Generate mock general search results."""
        result_html = "<h2>Mock Search Results</h2>"
        
        for i in range(5):
            result_html += f"""
            <div class="result">
                <h3><a href="#">Mock Search Result #{i+1}</a></h3>
                <div class="url">https://example.com/result{i+1}</div>
                <div class="description">This is a mock search result description containing some simulated content for testing purposes.</div>
            </div>
            """
        
        return result_html


class MockElement:
    """A mock element class for testing."""
    
    def __init__(self, browser, by, value, index=0):
        self.browser = browser
        self.by = by
        self.value = value
        self.index = index
        self.text = self._generate_mock_text()
        self.is_displayed_value = True
        self.is_enabled_value = True
    
    def click(self):
        """Simulate clicking the element."""
        logger.info(f"Mock element clicked: {self.by}={self.value}")
        return self
    
    def send_keys(self, keys):
        """Simulate sending keys to the element."""
        logger.info(f"Mock element send_keys: {self.by}={self.value}, keys={keys}")
        return self
    
    def clear(self):
        """Simulate clearing the element."""
        logger.info(f"Mock element cleared: {self.by}={self.value}")
        return self
    
    def get_attribute(self, name):
        """Simulate getting an attribute from the element."""
        logger.info(f"Mock element get_attribute: {self.by}={self.value}, attribute={name}")
        
        if name == "href":
            return f"https://example.com/mock-link-{random.randint(1, 100)}"
        elif name == "src":
            return f"https://example.com/mock-image-{random.randint(1, 100)}.jpg"
        elif name == "class":
            return "mock-class-name"
        else:
            return f"mock-attribute-{name}"
    
    def find_element(self, by, value):
        """Mock find_element method that returns another MockElement."""
        logger.info(f"Mock element finding sub-element: {by}={value}")
        return MockElement(self.browser, by, value)
    
    def find_elements(self, by, value):
        """Mock find_elements method that returns a list of MockElements."""
        logger.info(f"Mock element finding sub-elements: {by}={value}")
        return [MockElement(self.browser, by, value, index=i) for i in range(random.randint(2, 5))]
    
    def is_displayed(self):
        """Simulate checking if the element is displayed."""
        return self.is_displayed_value
    
    def is_enabled(self):
        """Simulate checking if the element is enabled."""
        return self.is_enabled_value
    
    def submit(self):
        """Simulate submitting a form element."""
        logger.info(f"Mock element submitted: {self.by}={self.value}")
        return self
    
    def _generate_mock_text(self):
        """Generate mock text content for the element."""
        element_texts = {
            "a": ["Link Text", "Click Here", "Read More", "Learn More", "Download"],
            "button": ["Submit", "Search", "Cancel", "OK", "Apply"],
            "input": ["", "Search term", "Example input", "Username", "Password"],
            "h1": ["Page Title", "Main Heading", "Welcome to the Site", "Search Results", "Dashboard"],
            "h2": ["Section Heading", "Features", "About Us", "Services", "Products"],
            "p": ["This is a mock paragraph with simulated text content for testing purposes.",
                 "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                 "Mock content for testing Selenium interactions with web elements.",
                 "This text is generated for a mock element to test web scraping functionality.",
                 "Placeholder text for a paragraph element in the mock browser."],
            "div": ["Container content", "Section content", "Panel content", "Widget text", "Module content"],
            "span": ["Label", "Badge", "Tag", "Indicator", "Counter"],
            "li": ["List item 1", "List item 2", "Option A", "Category", "Result item"]
        }
        
        if self.value.lower() in element_texts:
            text_options = element_texts[self.value.lower()]
        else:
            text_options = ["Mock text", "Element content", "Test data", f"Element {self.index + 1}", "Sample text"]
        
        return random.choice(text_options)


class MockSwitchTo:
    """A mock switch_to class for testing."""
    
    def __init__(self, browser):
        self.browser = browser
    
    def alert(self):
        """Simulate switching to an alert."""
        logger.info("Mock browser switching to alert")
        return MockAlert(self.browser)
    
    def default_content(self):
        """Simulate switching to default content."""
        logger.info("Mock browser switching to default content")
        return self.browser
    
    def frame(self, frame_reference):
        """Simulate switching to a frame."""
        logger.info(f"Mock browser switching to frame: {frame_reference}")
        return self.browser
    
    def window(self, window_name):
        """Simulate switching to a window."""
        logger.info(f"Mock browser switching to window: {window_name}")
        return self.browser


class MockAlert:
    """A mock alert class for testing."""
    
    def __init__(self, browser):
        self.browser = browser
        self.text = "This is a mock alert message"
    
    def accept(self):
        """Simulate accepting an alert."""
        logger.info("Mock alert accepted")
        return None
    
    def dismiss(self):
        """Simulate dismissing an alert."""
        logger.info("Mock alert dismissed")
        return None
    
    def send_keys(self, keys):
        """Simulate sending keys to an alert."""
        logger.info(f"Mock alert send_keys: {keys}")
        return None

def capture_screenshot(browser):
    """Capture a screenshot of the current page."""
    if not PIL_AVAILABLE:
        logger.warning("PIL not available. Cannot capture screenshot.")
        return None
        
    try:
        # First try the standard method
        temp_path = f"/tmp/screenshot_{int(time.time())}.png"
        browser.save_screenshot(temp_path)
        
        try:
            image = Image.open(temp_path)
            logger.info(f"Screenshot captured successfully")
            return image
        except Exception as e:
            logger.warning(f"Failed to open screenshot from file: {e}")
            
        # If that fails, try get_screenshot_as_png
        try:
            screenshot_bytes = browser.get_screenshot_as_png()
            if screenshot_bytes:
                image = Image.open(BytesIO(screenshot_bytes))
                return image
        except Exception as e:
            logger.warning(f"Failed with get_screenshot_as_png: {e}")
        
        # If all methods fail, create a blank image
        return Image.new('RGB', (800, 600), color='white')
        
    except Exception as e:
        logger.error(f"Failed to capture screenshot: {str(e)}", exc_info=True)
        # Return a blank image as fallback
        return Image.new('RGB', (800, 600), color='white')

def analyze_page_with_vision(image, goal):
    """
    Analyze a page screenshot using a vision model.
    
    Args:
        image: PIL Image instance of the screenshot
        goal: String describing what we're trying to accomplish
    
    Returns:
        dict: Instructions for interacting with the page
    """
    # Check if Google Generative AI module is available
    if not GENAI_AVAILABLE:
        logger.warning("Google Generative AI not available. Falling back to default behavior.")
        return {
            "suggested_action": "Try to locate search box manually",
            "interaction_steps": ["Look for search input", "Enter search terms", "Click search button"]
        }
    
    # Get API key from environment
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        logger.warning("GOOGLE_API_KEY environment variable is not set. Vision model will not work.")
        return {
            "suggested_action": "Try to locate search box manually",
            "interaction_steps": ["Look for search input", "Enter search terms", "Click search button"]
        }
    
    try:
        # Configure the genai module with API key
        genai.configure(api_key=api_key)
        
        # Convert image to base64 for API
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        
        # Create the prompt for the vision model
        prompt = f"""
        I'm looking at a screenshot of a webpage. I need to {goal}.
        
        Please provide detailed instructions for interacting with this page in JSON format:
        1. Identify the search box (give CSS selector if possible)
        2. Identify the search button (give CSS selector if possible)
        3. If any visible results are shown, extract them
        
        Return a JSON object with the following structure:
        {{
            "search_box_selector": "The CSS selector for the search input field",
            "search_button_selector": "The CSS selector for the search button",
            "visible_results": ["List of visible result titles or text"],
            "suggested_action": "Brief description of recommended next action"
        }}
        """
        
        # Generate content with the Gemini Pro Vision model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content([
            prompt,
            {"mime_type": "image/png", "data": img_bytes}
        ])
        
        logger.info("Vision model analysis completed")
        
        # Parse the response
        try:
            # Try to extract JSON from the text (sometimes it's embedded in markdown)
            text_response = response.text
            json_match = re.search(r'```json\s*(.*?)\s*```', text_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # If not in markdown, try to extract anything that looks like JSON
                json_match = re.search(r'({.*})', text_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = text_response
            
            # Clean up any non-JSON content
            json_str = re.sub(r'[^\x00-\x7F]+', '', json_str)  # Remove non-ASCII chars
            
            # Parse JSON response
            try:
                result = json.loads(json_str)
                logger.info(f"Successfully parsed vision model response: {list(result.keys())}")
                
                # Add fallback values for any missing keys
                if "search_box_selector" not in result:
                    result["search_box_selector"] = "input[type='search'], input[name='q']"
                if "search_button_selector" not in result:
                    result["search_button_selector"] = "button[type='submit'], input[type='submit']"
                if "visible_results" not in result:
                    result["visible_results"] = []
                if "suggested_action" not in result:
                    result["suggested_action"] = "Try to use the search functionality"
                
                return result
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON from vision model: {e}")
                # If we couldn't parse JSON, return default response
                return {
                    "search_box_selector": "input[type='search'], input[name='q']",
                    "search_button_selector": "button[type='submit'], input[type='submit']",
                    "suggested_action": "Try to locate search box manually",
                    "visible_results": []
                }
                
        except Exception as e:
            logger.warning(f"Error processing vision model response: {e}")
            return {
                "search_box_selector": "input[type='search'], input[name='q']",
                "search_button_selector": "button[type='submit'], input[type='submit']",
                "suggested_action": "Try to locate search box manually",
                "visible_results": []
            }
            
    except Exception as e:
        logger.warning(f"Error using vision model: {e}")
        return {
            "search_box_selector": "input[type='search'], input[name='q']",
            "search_button_selector": "button[type='submit'], input[type='submit']",
            "suggested_action": "Try to locate search box manually",
            "visible_results": []
        }

def search_with_vision_assistance(browser, url, search_term, database_name, settings=None):
    """
    Search a database using vision model assistance to find UI elements.
    
    Args:
        browser: Selenium WebDriver instance
        url: URL of the database to search
        search_term: Term to search for
        database_name: Name of the database (for logging)
        settings: Optional dictionary of settings (e.g., 'captcha_wait_time')
        
    Returns:
        tuple: (search_success, screenshot_of_results)
            - search_success: Boolean indicating if the search was completed
            - screenshot_of_results: Screenshot of the results page if successful
    """
    logger.info(f"Searching {database_name} with vision assistance: {search_term}")
    
    # Check if site is in the blocked list
    if is_site_blocked(url):
        logger.warning(f"Skipping {url} as it's in the blocked sites list")
        return False, None
    
    # Check if PIL is available
    if not PIL_AVAILABLE:
        logger.warning("PIL not available. Cannot use vision-assisted search.")
        return False, None
    
    # Check if genai is available
    if not GENAI_AVAILABLE:
        logger.warning("Google Generative AI not available. Cannot use vision-assisted search.")
        return False, None
        
    # Check if API key is set
    if not os.environ.get('GOOGLE_API_KEY'):
        logger.warning("GOOGLE_API_KEY not set. Cannot use vision-assisted search.")
        return False, None
    
    try:
        # Navigate to the URL
        browser.get(url)
        logger.info(f"Navigated to {url}")
        
        # Wait for page to load
        time.sleep(3)
        
        # Check for captchas and attempt to handle them
        if detect_captcha(browser)[0]:
            logger.info("Detected captcha during initial page load")
            if not handle_captcha(browser, url, wait_time=settings.get('captcha_wait_time') if settings else None):
                logger.warning("Failed to handle captcha, continuing anyway")
        
        # Check if the site is blocking our access
        if check_for_site_blocking(browser, url):
            logger.warning(f"Site appears to be blocking access: {url}")
            return False, None
            
        # Handle cookie consent if present
        if handle_cookie_consent(browser):
            logger.info("Cookie consent handled")
            time.sleep(2)  # Wait for page to settle after consent
        
        # Take a screenshot
        screenshot_path = f"/tmp/{database_name}_search_page.png"
        try:
            browser.save_screenshot(screenshot_path)
            logger.info(f"Screenshot saved to {screenshot_path}")
        except Exception as e:
            logger.warning(f"Error saving screenshot: {e}")
            return False, None
        
        # Open the screenshot with PIL
        try:
            screenshot = Image.open(screenshot_path)
            logger.info("Screenshot loaded successfully")
        except Exception as e:
            logger.warning(f"Error loading screenshot: {e}")
            return False, None
        
        # Use vision model to analyze the page
        analysis_goal = f"search for '{search_term}' on this {database_name} page"
        
        # Get analysis from vision model
        try:
            analysis = analyze_page_with_vision(screenshot, analysis_goal)
            logger.info(f"Vision analysis complete: {list(analysis.keys())}")
        except Exception as e:
            logger.warning(f"Error analyzing page: {e}")
            return False, None
        
        # Extract search box and button selectors
        search_box_selector = analysis.get("search_box_selector", "input[type='search'], input[name='q']")
        search_button_selector = analysis.get("search_button_selector", "button[type='submit'], input[type='submit']")
        
        logger.info(f"Using selectors - Search box: {search_box_selector}, Search button: {search_button_selector}")
        
        # Find and interact with the search box
        try:
            # First try with WebDriverWait to handle dynamic pages
            search_box = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, search_box_selector))
            )
            logger.info("Search box found using vision-provided selector")
        except Exception as e:
            logger.warning(f"Error finding search box with selector {search_box_selector}: {e}")
            # Try some fallback selectors
            fallback_selectors = [
                "input[type='search']", 
                "input[name='q']", 
                "input.search-box",
                "input.searchBox",
                "input.search",
                "input[placeholder*='search' i]",
                "input[aria-label*='search' i]"
            ]
            search_box = None
            for selector in fallback_selectors:
                try:
                    search_box = browser.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"Search box found using fallback selector: {selector}")
                    break
                except:
                    continue
            
            if not search_box:
                logger.warning("Could not find search box with any selector")
                return False, None
        
        # Clear any existing text and enter search term
        try:
            search_box.clear()
            search_box.send_keys(search_term)
            logger.info(f"Entered search term: {search_term}")
        except Exception as e:
            logger.warning(f"Error entering search term: {e}")
            return False, None
        
        # Click the search button
        try:
            # First try with WebDriverWait to handle dynamic pages
            search_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, search_button_selector))
            )
            search_button.click()
            logger.info("Clicked search button using vision-provided selector")
        except Exception as e:
            logger.warning(f"Error clicking search button with selector {search_button_selector}: {e}")
            # Try pressing Enter key as fallback
            try:
                search_box.send_keys(Keys.RETURN)
                logger.info("Pressed Enter key as fallback for search button")
            except Exception as e2:
                logger.warning(f"Error pressing Enter key: {e2}")
                return False, None
        
        # Wait for results to load
        time.sleep(5)
        
        # Check if site is blocking after search
        if check_for_site_blocking(browser, browser.current_url):
            logger.warning(f"Site appears to be blocking access after search: {browser.current_url}")
            return False, None
        
        # Take a screenshot of the results
        search_term_str = search_term if isinstance(search_term, str) else str(search_term)
        results_screenshot_path = f"/tmp/{database_name}_results_{search_term_str.replace(' ', '_')}.png"
        try:
            browser.save_screenshot(results_screenshot_path)
            results_screenshot = Image.open(results_screenshot_path)
            logger.info(f"Results screenshot saved to {results_screenshot_path}")
            return True, results_screenshot
        except Exception as e:
            logger.warning(f"Error capturing results screenshot: {e}")
            return True, None  # Return True since search completed, even if screenshot failed
            
    except Exception as e:
        logger.error(f"Error during vision-assisted search: {str(e)}", exc_info=True)
        return False, None

def search_google_scholar(browser, search_term, settings=None):
    """
    Search Google Scholar using Selenium.
    
    Args:
        browser: Selenium WebDriver instance
        search_term: Term to search for (string or dict)
        settings: Optional dictionary of settings (e.g., 'captcha_wait_time')
    
    Returns:
        list: List of search results
    """
    url = "https://scholar.google.com"
    results = []
    
    # Ensure search_term is a string
    if isinstance(search_term, dict) and 'topic' in search_term:
        search_term = search_term['topic']
    elif not isinstance(search_term, str):
        search_term = str(search_term)
    
    # Check if site is blocked
    if is_site_blocked(url):
        logger.warning(f"Google Scholar is in the blocked sites list. Attempting to access anyway.")
        # Instead of generating mock results, we'll try to access it anyway
    
    try:
        # Navigate to Google Scholar
        browser.get(url)
        logger.info("Navigated to Google Scholar")
        
        # Wait for the page to load
        time.sleep(3)
        
        # Check for captchas and attempt to handle them
        if detect_captcha(browser)[0]:
            logger.info("Detected captcha during initial page load")
            if not handle_captcha(browser, url, wait_time=settings.get('captcha_wait_time') if settings else None):
                logger.warning("Failed to handle captcha, continuing anyway")
        
        # Check for site blocking (not CAPTCHA)
        if check_for_site_blocking(browser, url):
            logger.warning("Google Scholar appears to be blocking access")
            return []  # Return empty results instead of mock results
        
        # Handle cookie consent if present
        if handle_cookie_consent(browser):
            logger.info("Handled cookie consent on Google Scholar")
            time.sleep(2)
        
        # Use vision-assisted search
        search_success, results_screenshot = search_with_vision_assistance(
            browser, url, search_term, "Google Scholar", settings=settings
        )
        
        # If search was successful and we have results screenshot
        if search_success and results_screenshot:
            # Analyze results using vision model
            results_analysis = analyze_page_with_vision(
                results_screenshot,
                f"Extract research paper titles and publication details from the Google Scholar search results for '{search_term}'"
            )
            
            # Use the vision model's analysis of visible results
            visible_results = results_analysis.get('visible_results', [])
            if visible_results:
                logger.info(f"Vision model found {len(visible_results)} results")
                for i, title in enumerate(visible_results[:10]):  # Limit to first 10 results
                    result = {
                        'title': title,
                        'source': 'Google Scholar',
                        'url': browser.current_url,
                        'snippet': f"Found via vision model analysis (result #{i+1})",
                        'year': 'N/A',
                        'authors': 'N/A'
                    }
                    results.append(result)
                
                # Log the screenshot for verification
                logger.info(f"Screenshot captured for results")
        
        # If vision model didn't find results or search failed, try traditional methods
        if not search_success or not results:
            # Try traditional methods to search
            try:
                # Try different selectors for the search box
                selectors = [
                    "input[name='q']", 
                    "input[aria-label='Search']",
                    "input.gs_in_txt",
                    "input[type='search']",
                    "input.gsc-input"
                ]
                
                search_box = None
                for selector in selectors:
                    try:
                        search_box = browser.find_element(By.CSS_SELECTOR, selector)
                        if search_box:
                            break
                    except NoSuchElementException:
                        continue
                
                if not search_box:
                    logger.warning("Could not find search box on Google Scholar")
                    return []  # Return empty results instead of mock results
                
                # Clear any existing text and enter search term
                search_box.clear()
                search_box.send_keys(search_term)
                search_box.send_keys(Keys.RETURN)
                time.sleep(3)  # Wait for results to load
                
                # Check if CAPTCHA appeared after search
                captcha_detected, captcha_type = detect_captcha(browser)
                if captcha_detected:
                    logger.warning(f"CAPTCHA detected after search on Google Scholar ({captcha_type})")
                    # Handle the CAPTCHA and wait for user to solve it
                    captcha_solved = handle_captcha(browser, url, wait_time=settings.get('captcha_wait_time') if settings else None)
                    if not captcha_solved:
                        logger.error("CAPTCHA not solved within the time limit. Cannot proceed with Google Scholar search.")
                        return []  # Return empty results instead of mock results
                    
                    # If CAPTCHA was solved, wait for the results to load
                    time.sleep(3)
            except Exception as e:
                logger.warning(f"Error interacting with Google Scholar search: {e}")
                return []  # Return empty results instead of mock results
        
        # Try traditional methods to extract results
        try:
            # Wait for results to load
            try:
                wait = WebDriverWait(browser, 10)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".gs_ri")))
            except Exception as e:
                logger.warning(f"Timeout waiting for Google Scholar results: {e}")
            
            # Extract search results
            time.sleep(2)  # Additional wait for JavaScript rendering
            
            # Take a screenshot for analysis if needed
            screenshot_path = capture_screenshot(browser)
            if screenshot_path:
                logger.info(f"Screenshot saved to: {screenshot_path}")
            
            # Find all result elements
            result_elements = browser.find_elements(By.CSS_SELECTOR, ".gs_ri")
            
            if not result_elements:
                logger.warning("No result elements found on Google Scholar")
                return []  # Return empty results instead of mock results
            
            for i, element in enumerate(result_elements[:5]):  # Limit to first 5 results
                try:
                    # Extract title, might be in different elements
                    title_element = element.find_element(By.CSS_SELECTOR, "h3")
                    title = title_element.text
                    
                    # Extract link if available
                    link = ""
                    try:
                        link_element = title_element.find_element(By.TAG_NAME, "a")
                        link = link_element.get_attribute("href")
                    except:
                        # If direct link not found, try data-href attribute or other locations
                        try:
                            link = title_element.get_attribute("data-href")
                        except:
                            pass
                    
                    # Extract snippet/abstract
                    snippet = ""
                    try:
                        snippet_element = element.find_element(By.CSS_SELECTOR, ".gs_rs")
                        snippet = snippet_element.text
                    except:
                        pass
                    
                    # Extract authors and publication info
                    authors = ""
                    try:
                        author_element = element.find_element(By.CSS_SELECTOR, ".gs_a")
                        authors = author_element.text
                    except:
                        pass
                    
                    # Create a result dictionary
                    result = {
                        'title': title,
                        'url': link if link else url,
                        'snippet': snippet,
                        'source': 'Google Scholar',
                        'authors': authors,
                        'search_term': search_term
                    }
                    
                    results.append(result)
                    logger.info(f"Found Google Scholar result: {title}")
                except Exception as e:
                    logger.warning(f"Error extracting result {i}: {e}")
        except Exception as e:
            logger.warning(f"Error extracting Google Scholar results: {e}")
            return []  # Return empty results instead of mock results
        
        # Look for PDF links in the results page and process them
        try:
            # Check for PDF links on the current page
            pdf_links = check_for_pdf_links(browser)
            logger.info(f"Found {len(pdf_links)} potential PDF links")
            
            # Process up to 3 PDFs to avoid excessive downloading
            for i, pdf_url in enumerate(pdf_links[:3]):
                try:
                    # Download the PDF
                    pdf_content = download_pdf(pdf_url)
                    
                    if pdf_content:
                        # Extract text from the PDF
                        pdf_text = extract_text_from_pdf(pdf_content)
                        
                        # Add the PDF content to the corresponding result
                        # Find the most likely related result based on URL similarity
                        best_match = None
                        best_score = 0
                        
                        for result in results:
                            if 'url' in result:
                                # Calculate simple similarity score between URLs
                                url1 = result['url'].lower()
                                url2 = pdf_url.lower()
                                
                                # Count matching characters/segments
                                parts1 = url1.split('/')
                                parts2 = url2.split('/')
                                
                                matching_parts = sum(1 for p1, p2 in zip(parts1, parts2) if p1 == p2)
                                score = matching_parts / max(len(parts1), len(parts2))
                                
                                if score > best_score:
                                    best_score = score
                                    best_match = result
                        
                        # If we found a matching result, add the PDF text
                        if best_match and best_score > 0.3:
                            best_match['pdf_text'] = pdf_text[:5000]  # Limit to first 5000 chars
                            best_match['has_full_text'] = True
                            logger.info(f"Added PDF text to result: {best_match.get('title', 'Unknown')}")
                        # Otherwise, create a new result entry
                        else:
                            new_result = {
                                'title': f"Full Text Document {i+1}",
                                'url': pdf_url,
                                'pdf_text': pdf_text[:5000],  # Limit to first 5000 chars
                                'snippet': pdf_text[:200] + "..." if len(pdf_text) > 200 else pdf_text,
                                'has_full_text': True,
                                'source': 'Google Scholar',
                                'search_term': search_term
                            }
                            results.append(new_result)
                            logger.info(f"Added new result with PDF text: {new_result['title']}")
                
                except Exception as e:
                    logger.error(f"Error processing PDF {pdf_url}: {e}")
                    continue
        except Exception as e:
            logger.warning(f"Error processing PDF links: {e}")
        
    except Exception as e:
        logger.warning(f"Error searching Google Scholar: {e}")
        return []  # Return empty results instead of mock results
    
    # Return whatever real results we found, even if empty
    return results

def search_research_gate(browser, search_term, settings=None):
    """
    Search ResearchGate using Selenium.
    
    Args:
        browser: Selenium WebDriver instance
        search_term: Term to search for (string or dict)
        settings: Optional dictionary of settings (e.g., 'captcha_wait_time')
    
    Returns:
        list: List of search results
    """
    url = "https://www.researchgate.net"
    results = []
    
    # Ensure search_term is a string
    if isinstance(search_term, dict) and 'topic' in search_term:
        search_term = search_term['topic']
    elif not isinstance(search_term, str):
        search_term = str(search_term)
    
    # Check if site is blocked
    if is_site_blocked(url):
        logger.warning(f"Skipping ResearchGate as it's in the blocked sites list")
        return []  # Return empty results instead of mock results
    
    try:
        logger.info(f"Searching ResearchGate for: '{search_term}'")
        
        # Use vision-assisted search
        search_success, results_screenshot = search_with_vision_assistance(
            browser, url, search_term, "ResearchGate", settings=settings
        )
        
        # If search was successful and we have results screenshot
        if search_success and results_screenshot:
            # Analyze results using vision model
            results_analysis = analyze_page_with_vision(
                results_screenshot,
                f"Extract research paper titles and details from the search results for '{search_term}'"
            )
            
            # Use the vision model's analysis of visible results
            visible_results = results_analysis.get('visible_results', [])
            if visible_results:
                logger.info(f"Vision model found {len(visible_results)} results")
                for i, title in enumerate(visible_results[:10]):  # Limit to first 10 results
                    result = {
                        'title': title,
                        'source': 'ResearchGate',
                        'url': browser.current_url,
                        'snippet': f"Found via vision model analysis (result #{i+1})",
                        'year': 'N/A',
                        'authors': 'N/A'
                    }
                    results.append(result)
                return results
        
        # If vision model didn't find results or search failed, try traditional methods
        if not search_success:
            # Try traditional methods to search
            try:
                # Try different selectors for the search box
                selectors = [
                    "input[name='query']", 
                    "input[placeholder='Search']",
                    "input[placeholder*='search']",
                    "input.search-input",
                    "input.nova-legacy-v-text-input__input",
                    "input[type='search']"
                ]
                
                search_box = None
                for selector in selectors:
                    try:
                        search_box = browser.find_element(By.CSS_SELECTOR, selector)
                        if search_box:
                            break
                    except:
                        continue
                
                if not search_box:
                    logger.warning("Could not find search box on ResearchGate")
                    return []  # Return empty results instead of mock results
                
                # Clear any existing text and enter search term
                search_box.clear()
                search_box.send_keys(search_term)
                search_box.send_keys(Keys.RETURN)
                time.sleep(3)  # Wait for results to load
                
                # Check if CAPTCHA appeared after search
                captcha_detected, captcha_type = detect_captcha(browser)
                if captcha_detected:
                    logger.warning(f"CAPTCHA detected after search on ResearchGate ({captcha_type})")
                    # Handle the CAPTCHA and wait for user to solve it
                    captcha_solved = handle_captcha(browser, url, wait_time=settings.get('captcha_wait_time') if settings else None)
                    if not captcha_solved:
                        logger.error("CAPTCHA not solved within the time limit. Cannot proceed with ResearchGate search.")
                        return []  # Return empty results instead of mock results
                    
                    # If CAPTCHA was solved, wait for the results to load
                    time.sleep(3)
            except Exception as e:
                logger.warning(f"Error interacting with ResearchGate search: {e}")
                return []  # Return empty results instead of mock results
        
        # Try traditional methods to extract results
        try:
            # Try different selectors for result items
            result_selectors = [
                ".search-box-result-item",
                ".nova-legacy-c-card",
                "div.research-detail-item",
                "div.search-result"
            ]
            
            result_elements = []
            for selector in result_selectors:
                try:
                    elements = browser.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        result_elements = elements
                        break
                except:
                    continue
            
            if not result_elements:
                logger.warning("Could not find search results on ResearchGate")
                return []  # Return empty results instead of mock results
            
            # Extract information from result elements
            for i, element in enumerate(result_elements[:10]):  # Limit to first 10 results
                try:
                    title_elem = element.find_element(By.CSS_SELECTOR, "a.nova-legacy-e-link, h3 a, .research-detail-title")
                    title = title_elem.text.strip()
                    
                    # Try to extract author information
                    authors = "Unknown"
                    try:
                        authors_elem = element.find_element(By.CSS_SELECTOR, ".nova-legacy-v-person-list, .authors, .research-detail-authors")
                        authors = authors_elem.text.strip()
                    except:
                        pass
                    
                    # Try to extract year information
                    year = "Unknown"
                    try:
                        year_elem = element.find_element(By.CSS_SELECTOR, ".nova-legacy-e-text--size-m, .publication-date, .research-detail-date")
                        year_match = re.search(r'\b(19|20)\d{2}\b', year_elem.text)
                        year = year_match.group(1) if year_match else "Unknown"
                    except:
                        pass
                    
                    # Try to extract snippet/description
                    snippet = "No description available"
                    try:
                        snippet_elem = element.find_element(By.CSS_SELECTOR, ".nova-legacy-e-text--size-m, .abstract, .research-detail-description")
                        snippet = snippet_elem.text.strip()
                    except:
                        pass
                    
                    result = {
                        'title': title,
                        'source': 'ResearchGate',
                        'url': url if url else browser.current_url,
                        'snippet': snippet,
                        'year': year,
                        'authors': authors
                    }
                    
                    results.append(result)
                    
                    logger.info(f"Found ResearchGate result: {title}")
                except Exception as e:
                    logger.warning(f"Error extracting result {i}: {str(e)}")
            
            return results
        except Exception as e:
            logger.warning(f"Error extracting ResearchGate results: {str(e)}")
            return []  # Return empty results instead of mock results
        
    except Exception as e:
        logger.warning(f"Error searching ResearchGate: {str(e)}")
        return []  # Return empty results instead of mock results

def search_academic_database(browser, database_url, search_terms, settings=None):
    """
    Search an academic database for the given search terms.
    
    Args:
        browser: Selenium WebDriver instance
        database_url: URL of the academic database
        search_terms: List of search terms
        settings: Optional dictionary of settings (e.g., 'captcha_wait_time')
    
    Returns:
        dict: Dictionary mapping search terms to search results
    """
    results = {}
    
    try:
        logger.info(f"Searching database: {database_url}")
        
        # Navigate to the database
        browser.get(database_url)
        time.sleep(2)  # Wait for page to load
        
        # Process each search term
        for search_term in search_terms:
            if search_term not in results:
                results[search_term] = []
            
            logger.info(f"Searching for: {search_term}")
            
            # Perform search for current term
            if "scholar.google.com" in database_url:
                paper_results = search_google_scholar(browser, search_term, settings=settings)
            elif "researchgate.net" in database_url:
                paper_results = search_research_gate(browser, search_term, settings=settings)
            elif "pubmed.ncbi.nlm.nih.gov" in database_url:
                paper_results = search_pubmed(browser, search_term, settings=settings)
            elif "ieeexplore.ieee.org" in database_url:
                paper_results = search_ieee(browser, search_term, settings=settings)
            elif "arxiv.org" in database_url:
                paper_results = search_arxiv(browser, search_term, settings=settings)
            elif "semanticscholar.org" in database_url:
                paper_results = search_semantic_scholar(browser, search_term, settings=settings)
            else:
                logger.warning(f"Unsupported database: {database_url}")
                continue
            
            # Add the database source to each result
            for result in paper_results:
                result['database'] = database_url
                results[search_term].append(result)
            
            logger.info(f"Found {len(paper_results)} results for '{search_term}' on {database_url}")
            
            # Give a small delay between searches to avoid rate limiting
            time.sleep(1)
        
        return results
            
    except Exception as e:
        logger.error(f"Error searching database {database_url}: {str(e)}", exc_info=True)
        return results

def search_academic_databases(topics_subtopics=None, settings=None, browsers=None, headless=True):
    """
    Search for academic papers from Google Scholar and ResearchGate.
    
    Args:
        topics_subtopics (list or dict): Either a list of dictionaries with 'topic' and 'subtopics' keys,
                                         or a list of topics (strings)
        settings (dict): Dictionary of settings
        browsers (list): List of Selenium WebDriver instances (optional)
        headless (bool): Whether to run browsers in headless mode
    
    Returns:
        dict: Dictionary mapping topics to lists of search results
    """
    # Process settings
    if settings is None:
        settings = {}
    
    # Extract headless setting from settings if available
    if 'headless' in settings:
        headless = settings['headless']
    
    # Process topics_subtopics
    topics = []
    subtopics = {}
    
    # Check if topics_subtopics is a list of dictionaries with 'topic' and 'subtopics' keys
    if isinstance(topics_subtopics, list) and topics_subtopics and isinstance(topics_subtopics[0], dict):
        for item in topics_subtopics:
            if 'topic' in item:
                topic = item['topic']
                topics.append(topic)
                if 'subtopics' in item and isinstance(item['subtopics'], list):
                    subtopics[topic] = item['subtopics']
    # If topics_subtopics is already a list of topics
    elif isinstance(topics_subtopics, list):
        topics = topics_subtopics
    # Default topics if none provided
    else:
        topics = ["artificial intelligence", "machine learning"]
    
    # Ensure browsers is a list
    if browsers is None:
        browsers = []
    
    # Load blocked sites at the start
    load_blocked_sites()
    
    # Set up browsers if not provided
    if not browsers:
        browser_type = settings.get('browser_type', None)
        for i in range(settings.get('browser_count', 1)):
            try:
                browser = _create_browser(headless=headless, browser_type=browser_type)
                browsers.append(browser)
            except Exception as e:
                logger.error(f"Error setting up browser {i}: {e}")
                # Try to create at least one browser
                if i == 0:
                    continue
    
    # If no browsers are available, return empty results
    if not browsers:
        logger.error("No browsers available for searching")
        return {}
    
    # Distribute browsers
    google_scholar_browser = browsers[0]
    research_gate_browser = browsers[-1]  # Use the last browser for ResearchGate
    
    all_results = {}
    
    # Search for each topic
    for topic in topics:
        logger.info(f"Searching for topic: {topic}")
        
        # Google Scholar search
        google_scholar_results = search_google_scholar(google_scholar_browser, topic, settings=settings)
        
        # ResearchGate search
        research_gate_results = search_research_gate(research_gate_browser, topic, settings=settings)
        
        # Combine results
        topic_results = google_scholar_results + research_gate_results
        
        # Sort results by relevance (using a simple heuristic)
        topic_results.sort(key=lambda x: 
            (0 if x.get('is_mock', False) else 1,  # Real results first
             len(x.get('snippet', '')) if 'snippet' in x else 0),  # Then by snippet length
            reverse=True)
        
        all_results[topic] = topic_results
        logger.info(f"Found {len(topic_results)} results for topic: {topic}")
        
        # Search for subtopics if available
        if topic in subtopics:
            for subtopic in subtopics[topic]:
                logger.info(f"Searching for subtopic: {subtopic}")
                
                # Google Scholar search for subtopic
                subtopic_google_results = search_google_scholar(google_scholar_browser, f"{topic} {subtopic}", settings=settings)
                
                # ResearchGate search for subtopic
                subtopic_research_results = search_research_gate(research_gate_browser, f"{topic} {subtopic}", settings=settings)
                
                # Combine results
                subtopic_results = subtopic_google_results + subtopic_research_results
                
                # Sort results by relevance
                subtopic_results.sort(key=lambda x: 
                    (0 if x.get('is_mock', False) else 1,  # Real results first
                     len(x.get('snippet', '')) if 'snippet' in x else 0),  # Then by snippet length
                    reverse=True)
                
                all_results[f"{topic} - {subtopic}"] = subtopic_results
                logger.info(f"Found {len(subtopic_results)} results for subtopic: {subtopic}")
    
    # Clean up browsers if we created them
    if not browsers:
        for browser in browsers:
            try:
                browser.quit()
            except:
                pass
    
    # Save blocked sites at the end
    save_blocked_sites()
    
    return all_results

def generate_mock_results(search_term, count=3, source=None):
    """
    Generate mock search results when actual scraping fails.
    
    Args:
        search_term (str): The search term used
        count (int): Number of mock results to generate
        source (str): Optional source name (e.g., "Google Scholar")
    
    Returns:
        list: List of mock result dictionaries
    """
    logger.info(f"Generating {count} mock results for {search_term}")
    
    # Base paper titles that will be customized with the search term
    base_titles = [
        "Advances in {}: A Comprehensive Review",
        "Applications of {} in Modern Research",
        "{}: Current State and Future Directions",
        "Theoretical Foundations of {}",
        "Experimental Approaches to {}",
        "A Survey of Methods in {}",
        "Challenges and Opportunities in {} Research",
        "Emerging Trends in {}",
        "Computational Models for {}",
        "Understanding {} Through Data Analysis"
    ]
    
    # Universities and institutions for author affiliations
    institutions = [
        "Stanford University",
        "Massachusetts Institute of Technology",
        "Harvard University",
        "University of California, Berkeley",
        "University of Oxford",
        "Cambridge University",
        "ETH Zurich",
        "Imperial College London",
        "California Institute of Technology",
        "University of Chicago"
    ]
    
    # Journals for publication info
    journals = [
        "Journal of Computer Science",
        "IEEE Transactions on Pattern Analysis",
        "Nature Digital Intelligence",
        "Proceedings of the National Academy of Sciences",
        "Journal of Artificial Intelligence Research",
        "ACM Computing Surveys",
        "Science Advances",
        "Communications of the ACM",
        "International Journal of Machine Learning",
        "Computational Intelligence and Neuroscience"
    ]
    
    # Years for publication dates
    years = list(range(2018, 2025))
    
    results = []
    for i in range(min(count, len(base_titles))):
        # Generate a realistic-looking academic paper title
        search_term_clean = search_term.replace("research on ", "").replace("studies in ", "")
        title_template = random.choice(base_titles)
        title = title_template.format(search_term_clean)
        
        # Generate author information
        num_authors = random.randint(1, 4)
        authors = []
        for j in range(num_authors):
            first_initial = chr(random.randint(65, 90))  # A-Z
            last_name = random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Lee", "Wang", "Chen", "Kim", "Taylor"])
            authors.append(f"{first_initial}. {last_name}")
        
        author_str = ", ".join(authors)
        
        # Add institution and publication year
        institution = random.choice(institutions)
        journal = random.choice(journals)
        year = random.choice(years)
        author_info = f"{author_str} - {institution} - {journal}, {year}"
        
        # Generate a realistic-looking abstract
        abstract = f"This paper presents a comprehensive review of research in {search_term_clean}. "
        abstract += f"We examine recent developments, methodologies, and key findings in the field. "
        abstract += f"The study analyzes data from various sources to provide insights into {search_term_clean}. "
        abstract += f"Our results indicate significant progress in understanding {search_term_clean}, "
        abstract += f"with implications for both theory and practice in related disciplines."
        
        # Create result dictionary that's COMPATIBLE with extract_paper_information
        result = {
            'title': title,
            'authors': author_str,
            'year': str(year),
            'snippet': abstract,
            'url': f"https://example.org/papers/{i+1}",
            'citations': str(random.randint(5, 500)),
            'journal': journal,
            'is_mock': True  # Flag to indicate this is mock data
        }
        
        if source:
            result['source'] = source
        
        results.append(result)
    
    return results

def test_vision_assisted_search():
    """
    Test function to verify the vision-assisted web scraping functionality.
    This function will search Google Scholar and ResearchGate for a test query.
    """
    import os
    from pprint import pprint
    
    print("\n===== VISION-ASSISTED SEARCH TEST =====")
    
    # Check if GOOGLE_API_KEY exists in the environment
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        logger.error("GOOGLE_API_KEY environment variable is not set. Vision model will not work.")
        print("ERROR: Please set GOOGLE_API_KEY environment variable first!")
        print("You can set it with: export GOOGLE_API_KEY=your_api_key")
        return
    
    # Check if genai module is available
    if not GENAI_AVAILABLE:
        logger.error("Google Generative AI module not available. Please install with: pip install google-generativeai")
        print("ERROR: Please install Google Generative AI module with: pip install google-generativeai")
        return
    
    # Check if PIL is available
    if not PIL_AVAILABLE:
        logger.error("PIL module not available. Please install with: pip install pillow")
        print("ERROR: Please install PIL module with: pip install pillow")
        return
    
    logger.info("Starting vision-assisted search test...")
    
    # Load any previously blocked sites
    load_blocked_sites()
    
    # Test topic
    test_topic = "machine learning computer vision"
    
    # Search settings
    settings = {
        'headless': False,  # Set to False to watch the browser in action
        'max_results_per_topic': 5,
        'use_vision_model': True,
        'screenshot_dir': '/tmp/screenshots'
    }
    
    # Create screenshot directory if it doesn't exist
    os.makedirs(settings['screenshot_dir'], exist_ok=True)
    
    browser = None
    try:
        # Initialize browser
        browser = _create_browser(headless=settings['headless'])
        
        # Test direct vision-assisted search first
        print(f"\n===== Testing Direct Vision-Assisted Search =====")
        try:
            # Test on Google Scholar
            print(f"Testing direct vision search on Google Scholar...")
            success, screenshot = search_with_vision_assistance(
                browser, 
                "https://scholar.google.com", 
                test_topic,
                "Google Scholar"
            )
            
            if success:
                print("✅ Direct vision search on Google Scholar was successful!")
                if screenshot:
                    screenshot.save(f"{settings['screenshot_dir']}/direct_google_scholar_results.png")
                    print(f"Screenshot saved to: {settings['screenshot_dir']}/direct_google_scholar_results.png")
            else:
                print("❌ Direct vision search on Google Scholar failed.")
        except Exception as e:
            logger.error(f"Error testing direct vision search on Google Scholar: {e}", exc_info=True)
            print(f"Error during Google Scholar direct vision test: {str(e)}")
        
        try:
            # Test on ResearchGate
            print(f"\nTesting direct vision search on ResearchGate...")
            success, screenshot = search_with_vision_assistance(
                browser, 
                "https://www.researchgate.net", 
                test_topic,
                "ResearchGate"
            )
            
            if success:
                print("✅ Direct vision search on ResearchGate was successful!")
                if screenshot:
                    screenshot.save(f"{settings['screenshot_dir']}/direct_researchgate_results.png")
                    print(f"Screenshot saved to: {settings['screenshot_dir']}/direct_researchgate_results.png")
            else:
                print("❌ Direct vision search on ResearchGate failed.")
        except Exception as e:
            logger.error(f"Error testing direct vision search on ResearchGate: {e}", exc_info=True)
            print(f"Error during ResearchGate direct vision test: {str(e)}")
            
        # Test individual search functions
        try:
            print(f"\n\n===== Testing Google Scholar search for '{test_topic}' =====")
            google_results = search_google_scholar(browser, test_topic)
            print(f"Found {len(google_results)} results from Google Scholar:")
            for i, result in enumerate(google_results[:3]):  # Show top 3 results
                print(f"\n{i+1}. {result.get('title', 'No title')}")
                if 'authors' in result and result['authors']:
                    print(f"   Authors: {result['authors']}")
                if 'snippet' in result and result['snippet']:
                    snippet = result['snippet']
                    if len(snippet) > 100:
                        snippet = snippet[:100] + "..."
                    print(f"   Snippet: {snippet}")
        except Exception as e:
            logger.error(f"Error testing Google Scholar search: {e}", exc_info=True)
            print(f"Error during Google Scholar search test: {str(e)}")
        
        try:
            print(f"\n\n===== Testing ResearchGate search for '{test_topic}' =====")
            researchgate_results = search_research_gate(browser, test_topic)
            print(f"Found {len(researchgate_results)} results from ResearchGate:")
            for i, result in enumerate(researchgate_results[:3]):  # Show top 3 results
                print(f"\n{i+1}. {result.get('title', 'No title')}")
                if 'authors' in result and result['authors']:
                    print(f"   Authors: {result['authors']}")
                if 'snippet' in result and result['snippet']:
                    snippet = result['snippet']
                    if len(snippet) > 100:
                        snippet = snippet[:100] + "..."
                    print(f"   Snippet: {snippet}")
        except Exception as e:
            logger.error(f"Error testing ResearchGate search: {e}", exc_info=True)
            print(f"Error during ResearchGate search test: {str(e)}")
        
        try:
            print("\n\n===== Testing combined academic database search =====")
            topics = [{"topic": test_topic, "subtopics": ["neural networks", "deep learning"]}]
            all_results = search_academic_databases(topics, settings)
            
            print(f"Total results for '{test_topic}': {len(all_results.get(test_topic, []))}")
            print("\nSample of combined results:")
            for i, result in enumerate(all_results.get(test_topic, [])[:3]):  # Show top 3 results
                print(f"\n{i+1}. {result.get('title', 'No title')}")
                if 'database' in result:
                    print(f"   Source: {result['database']}")
                if 'authors' in result and result['authors']:
                    print(f"   Authors: {result['authors']}")
        except Exception as e:
            logger.error(f"Error testing combined search: {e}", exc_info=True)
            print(f"Error during combined search test: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error in test_vision_assisted_search: {e}", exc_info=True)
        print(f"Error occurred during test: {str(e)}")
    
    finally:
        # Always close the browser when done
        if browser:
            browser.quit()
            logger.info("Test browser closed")
    
    logger.info("Vision-assisted search test completed")
    print("\nTest completed. Check the logs for more details.")

if __name__ == "__main__":
    # Run the test function if this script is executed directly
    test_vision_assisted_search()

# Load blocked sites when module is imported
load_blocked_sites()

def get_search_engine_function(engine_name):
    """
    Get the appropriate search function based on the engine name.
    
    Args:
        engine_name (str): Name of the search engine
        
    Returns:
        function: The search function for the specified engine, or None if not found
    """
    engine_map = {
        "Google Scholar": search_google_scholar,
        "ResearchGate": search_research_gate,
        "PubMed": search_pubmed,
        "IEEE Xplore": search_ieee,
        "arXiv": search_arxiv,
        "Semantic Scholar": search_semantic_scholar,
        "DuckDuckGo": search_duckduckgo
    }
    
    return engine_map.get(engine_name)

def check_for_pdf_links(browser):
    """
    Check for PDF links on the current page.
    
    Args:
        browser: Selenium WebDriver instance
        
    Returns:
        list: List of PDF links found on the page
    """
    pdf_links = []
    
    try:
        # Define more precise indicators for PDF links
        pdf_direct_indicators = ['.pdf', 'download/pdf', 'fulltext.pdf', 'view/pdf']
        pdf_text_indicators = ['pdf', 'full text', 'fulltext', 'download paper', 'download article']
        
        # Find all links on the page
        links = browser.find_elements(By.TAG_NAME, 'a')
        
        for link in links:
            try:
                href = link.get_attribute('href')
                if not href:
                    continue
                    
                link_text = link.text.lower()
                
                # First priority: Direct links to PDF files
                if any(indicator in href.lower() for indicator in pdf_direct_indicators):
                    pdf_links.append(href)
                    logger.info(f"Found likely PDF link (direct indicator): {href}")
                    continue
                    
                # Second priority: Links with PDF-related text
                if link_text and any(indicator in link_text for indicator in pdf_text_indicators):
                    # Check that the link doesn't point to a search results page or citation
                    if 'scholar.google' in href.lower() and any(x in href.lower() for x in ['scholar?', 'citations?']):
                        continue
                        
                    pdf_links.append(href)
                    logger.info(f"Found potential PDF link (text indicator): {href}")
            except Exception as e:
                logger.warning(f"Error checking link: {e}")
                continue
        
        logger.info(f"Found {len(pdf_links)} potential PDF links")
        return pdf_links
    
    except Exception as e:
        logger.error(f"Error checking for PDF links: {e}")
        return pdf_links

def download_pdf(url, max_size_mb=10):
    """
    Download a PDF from a URL.
    
    Args:
        url: URL of the PDF
        max_size_mb: Maximum size in MB to download
        
    Returns:
        bytes: PDF content or None if download failed
    """
    try:
        logger.info(f"Attempting to download PDF from: {url}")
        
        # Set up headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        # Stream the response to check size before downloading completely
        response = requests.get(url, headers=headers, stream=True)
        
        # Check if it's likely a PDF based on content type
        content_type = response.headers.get('Content-Type', '').lower()
        if 'application/pdf' not in content_type and 'pdf' not in content_type:
            # If URL ends with .pdf, continue anyway
            if not url.lower().endswith('.pdf'):
                logger.warning(f"URL does not appear to be a PDF (Content-Type: {content_type})")
                # Only continue with URLs that are likely to be PDFs or PDF landing pages
                if not any(x in url.lower() for x in ['.pdf', '/pdf', 'fulltext', 'download']):
                    return None
        
        # Check size
        content_length = int(response.headers.get('Content-Length', 0))
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if content_length > max_size_bytes:
            logger.warning(f"PDF too large ({content_length / 1024 / 1024:.2f} MB > {max_size_mb} MB)")
            return None
        
        # Download the content
        pdf_content = response.content
        
        # Basic validation that this is actually a PDF
        if pdf_content[:4] != b'%PDF':
            if pdf_content[:4] == b'<htm' or pdf_content[:4] == b'<HTM' or b'<!DOC' in pdf_content[:20]:
                logger.warning("Downloaded content appears to be HTML, not a PDF")
                return None
        
        logger.info(f"Successfully downloaded PDF ({len(pdf_content) / 1024:.2f} KB)")
        
        return pdf_content
    
    except Exception as e:
        logger.error(f"Error downloading PDF: {e}")
        return None

def extract_text_from_pdf(pdf_content):
    """
    Extract text from PDF content.
    
    Args:
        pdf_content: PDF content as bytes
        
    Returns:
        str: Extracted text from the PDF
    """
    try:
        # Basic validation check for PDF header
        if not pdf_content or len(pdf_content) < 4 or pdf_content[:4] != b'%PDF':
            logger.warning("Content does not appear to be a valid PDF (missing PDF header)")
            return "Not a valid PDF file - missing PDF header"
        
        import io
        from pdfminer.high_level import extract_text as pdfminer_extract_text
        
        # Create a BytesIO object
        pdf_file = io.BytesIO(pdf_content)
        
        # Extract text from the PDF
        text = pdfminer_extract_text(pdf_file)
        
        # Verify we actually got some text
        if not text or len(text.strip()) < 10:
            logger.warning("Extracted text is empty or too short")
            return "PDF appears to be empty or contains no extractable text"
        
        logger.info(f"Successfully extracted {len(text)} characters from PDF")
        
        return text
    
    except ImportError:
        logger.warning("pdfminer.six not available. Using mock extraction.")
        # If pdfminer isn't available, return a limited amount of text
        return f"PDF content extracted (mock - pdfminer.six not available). Content length: {len(pdf_content)} bytes"
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return f"Error extracting text: {str(e)}"

def search_pubmed(browser, search_term, settings=None):
    """
    Search PubMed using Selenium.
    
    Args:
        browser: Selenium WebDriver instance
        search_term: Term to search for (string or dict)
        settings: Optional dictionary of settings (e.g., 'captcha_wait_time')
    
    Returns:
        list: List of search results
    """
    if isinstance(search_term, dict):
        search_term = search_term.get('search_term', '')
    
    results = []
    
    try:
        url = "https://pubmed.ncbi.nlm.nih.gov/"
        logger.info(f"Searching PubMed for: {search_term}")
        
        # Navigate to PubMed
        browser.get(url)
        time.sleep(3)
        
        # Check for captchas and attempt to handle them
        if detect_captcha(browser)[0]:
            logger.info("Detected captcha on PubMed")
            if not handle_captcha(browser, url, wait_time=settings.get('captcha_wait_time') if settings else None):
                logger.warning("Failed to handle captcha, continuing anyway")
        
        # Check for site blocking
        if check_for_site_blocking(browser, url):
            logger.warning("PubMed access appears to be blocked")
            return []
        
        try:
            # Find search box and perform search
            search_input = browser.find_element(By.NAME, "term")
            search_input.clear()
            search_input.send_keys(search_term)
            search_input.send_keys(Keys.RETURN)
            time.sleep(5)
            
            # Check for captchas again after search
            if detect_captcha(browser)[0]:
                logger.info("Detected captcha after search on PubMed")
                if not handle_captcha(browser, browser.current_url, wait_time=settings.get('captcha_wait_time') if settings else None):
                    logger.warning("Failed to handle captcha, continuing anyway")
                    return []
            
            # Extract results
            result_elements = browser.find_elements(By.CSS_SELECTOR, ".docsum-content")
            
            for i, result_element in enumerate(result_elements[:10]):  # Limit to first 10 results
                try:
                    title_elem = result_element.find_element(By.CSS_SELECTOR, ".docsum-title")
                    title = title_elem.text.strip()
                    
                    # Try to get authors
                    try:
                        authors_elem = result_element.find_element(By.CSS_SELECTOR, ".docsum-authors")
                        authors = authors_elem.text.strip()
                    except:
                        authors = "Unknown"
                    
                    # Try to get year
                    try:
                        citation_elem = result_element.find_element(By.CSS_SELECTOR, ".docsum-journal-citation")
                        year_match = re.search(r'(\d{4})', citation_elem.text)
                        year = year_match.group(1) if year_match else "Unknown"
                    except:
                        year = "Unknown"
                    
                    # Get URL of the paper
                    try:
                        link = title_elem.find_element(By.XPATH, "./a").get_attribute("href")
                    except:
                        link = browser.current_url
                    
                    # Get snippet/abstract if available
                    try:
                        snippet_elem = result_element.find_element(By.CSS_SELECTOR, ".full-view-snippet")
                        snippet = snippet_elem.text.strip()
                    except:
                        snippet = "No abstract available"
                    
                    result = {
                        'title': title,
                        'authors': authors,
                        'year': year,
                        'url': link,
                        'snippet': snippet,
                        'source': 'PubMed'
                    }
                    
                    results.append(result)
                    
                    logger.info(f"Found PubMed result: {title}")
                except Exception as e:
                    logger.warning(f"Error extracting PubMed result {i}: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.warning(f"Error searching PubMed: {str(e)}")
            return []
            
    except Exception as e:
        logger.warning(f"Error accessing PubMed: {str(e)}")
        return []

def search_ieee(browser, search_term, settings=None):
    """
    Search IEEE Xplore using Selenium.
    
    Args:
        browser: Selenium WebDriver instance
        search_term: Term to search for (string or dict)
        settings: Optional dictionary of settings (e.g., 'captcha_wait_time')
    
    Returns:
        list: List of search results
    """
    if isinstance(search_term, dict):
        search_term = search_term.get('search_term', '')
    
    results = []
    
    try:
        url = "https://ieeexplore.ieee.org/search/searchresult.jsp"
        logger.info(f"Searching IEEE Xplore for: {search_term}")
        
        # Navigate to IEEE Xplore
        browser.get(url)
        time.sleep(5)  # IEEE needs a bit more time to load
        
        # Check for captchas and attempt to handle them
        if detect_captcha(browser)[0]:
            logger.info("Detected captcha on IEEE Xplore")
            if not handle_captcha(browser, url, wait_time=settings.get('captcha_wait_time') if settings else None):
                logger.warning("Failed to handle captcha, continuing anyway")
        
        # Check for site blocking
        if check_for_site_blocking(browser, url):
            logger.warning("IEEE Xplore access appears to be blocked")
            return []
        
        try:
            # Find search box and perform search
            search_input = browser.find_element(By.ID, "LayoutWrapper:BasicSearchForm:SearchField")
            search_input.clear()
            search_input.send_keys(search_term)
            
            # Try different ways to submit the search
            try:
                # First try to press Enter key
                search_input.send_keys(Keys.RETURN)
            except Exception as e:
                logger.warning(f"Failed to submit search with Enter key: {e}")
                try:
                    # Then try to submit the form
                    search_input.submit()
                except Exception as e:
                    logger.warning(f"Failed to submit search form: {e}")
                    try:
                        # Finally try to find and click a search button
                        search_buttons = [
                            (By.CSS_SELECTOR, "input[type='submit']"),
                            (By.CSS_SELECTOR, "button[type='submit']"),
                            (By.CSS_SELECTOR, ".search__button"),
                            (By.CSS_SELECTOR, ".search-btn"),
                        ]
                        
                        for button_selector in search_buttons:
                            try:
                                button = browser.find_element(*button_selector)
                                button.click()
                                break
                            except:
                                continue
                                
                    except Exception as e:
                        logger.error(f"All methods to submit search failed: {e}")
                        return []
            
            # Wait for results to load with multiple selector options
            wait_time = 10
            results_found = False
            result_selectors = [
                (By.CSS_SELECTOR, ".List-results-items"),
                (By.CSS_SELECTOR, ".result-item"),
                (By.CSS_SELECTOR, ".search-results"),
                (By.CSS_SELECTOR, ".result"),
            ]
            
            for selector in result_selectors:
                try:
                    WebDriverWait(browser, 10).until(
                        EC.presence_of_element_located(selector)
                    )
                    results_found = True
                    logger.info(f"Found results with selector: {selector}")
                    break
                except Exception as e:
                    logger.warning(f"Selector {selector} failed: {e}")
                    continue
                    
            if not results_found:
                logger.warning("No results found or results selector changed on IEEE Xplore")
                # Take a screenshot for debugging
                try:
                    timestamp = int(time.time())
                    screenshot_path = f"ieee_debug_{timestamp}.png"
                    browser.save_screenshot(screenshot_path)
                    logger.info(f"Saved debug screenshot to {screenshot_path}")
                except:
                    pass
                
                # Attempt to extract results anyway as a fallback
                try:
                    time.sleep(5)  # Wait a bit more just in case
                    page_source = browser.page_source
                    if "No results found" in page_source:
                        logger.warning("IEEE Xplore explicitly reported no results found")
                        return []
                except:
                    pass
        
            # Extract results
            result_elements = []
            for selector in result_selectors:
                try:
                    elements = browser.find_elements(*selector)
                    if elements:
                        result_elements = elements
                        break
                except:
                    continue
        
            for i, result_element in enumerate(result_elements[:10]):  # Limit to first 10 results
                try:
                    title_element = result_element.find_element(By.CSS_SELECTOR, "h3")
                    title = title_element.text
                    
                    # Get URL
                    try:
                        link = title_element.get_attribute("href")
                    except:
                        link = browser.current_url
                    
                    # Try to get authors
                    try:
                        authors_elem = result_element.find_element(By.CSS_SELECTOR, ".author-names")
                        authors = authors_elem.text.strip()
                    except:
                        authors = "Unknown"
                    
                    # Try to get year
                    try:
                        year_elem = result_element.find_element(By.CSS_SELECTOR, ".publisher-info-container")
                        year_match = re.search(r'(\d{4})', year_elem.text)
                        year = year_match.group(1) if year_match else "Unknown"
                    except:
                        year = "Unknown"
                    
                    # Try to get abstract
                    try:
                        snippet_elem = result_element.find_element(By.CSS_SELECTOR, ".abstract-text")
                        snippet = snippet_elem.text.strip()
                    except:
                        snippet = "No abstract available."
                    
                    result = {
                        'title': title,
                        'authors': authors,
                        'year': year,
                        'url': link,
                        'snippet': snippet,
                        'source': 'IEEE Xplore'
                    }
                    
                    results.append(result)
                    logger.info(f"Found IEEE result: {title}")
                    
                except Exception as e:
                    logger.warning(f"Error extracting IEEE result {i}: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.warning(f"Error searching IEEE Xplore: {str(e)}")
            return []
            
    except Exception as e:
        logger.warning(f"Error accessing IEEE Xplore: {str(e)}")
        return []

def search_arxiv(browser, search_term, settings=None):
    """
    Search arXiv using Selenium.
    
    Args:
        browser: Selenium WebDriver instance
        search_term: Term to search for (string or dict)
        settings: Optional dictionary of settings (e.g., 'captcha_wait_time')
    
    Returns:
        list: List of search results
    """
    if isinstance(search_term, dict):
        search_term = search_term.get('search_term', '')
    
    results = []
    
    try:
        url = "https://arxiv.org/search/"
        logger.info(f"Searching arXiv for: {search_term}")
        
        # Navigate to arXiv
        browser.get(url)
        time.sleep(3)
        
        # Check for captchas and attempt to handle them
        if detect_captcha(browser)[0]:
            logger.info("Detected captcha on arXiv")
            if not handle_captcha(browser, url, wait_time=settings.get('captcha_wait_time') if settings else None):
                logger.warning("Failed to handle captcha, continuing anyway")
        
        # Check for site blocking
        if check_for_site_blocking(browser, url):
            logger.warning("arXiv access appears to be blocked")
            return []
        
        try:
            # Find search box and perform search
            search_input = browser.find_element(By.NAME, "query")
            search_input.clear()
            search_input.send_keys(search_term)
            search_input.send_keys(Keys.RETURN)
            time.sleep(3)
            
            # Check for captchas again after search
            if detect_captcha(browser)[0]:
                logger.info("Detected captcha after search on arXiv")
                if not handle_captcha(browser, browser.current_url, wait_time=settings.get('captcha_wait_time') if settings else None):
                    logger.warning("Failed to handle captcha, continuing anyway")
                    return []
            
            # Extract results
            result_elements = browser.find_elements(By.CSS_SELECTOR, ".arxiv-result")
            
            for i, result_element in enumerate(result_elements[:10]):  # Limit to first 10 results
                try:
                    title_elem = result_element.find_element(By.CSS_SELECTOR, ".title")
                    title = title_elem.text.strip()
                    
                    # Get URL
                    try:
                        link_elem = result_element.find_element(By.CSS_SELECTOR, ".list-title a")
                        link = link_elem.get_attribute("href")
                    except:
                        link = browser.current_url
                    
                    # Try to get authors
                    try:
                        authors_elem = result_element.find_element(By.CSS_SELECTOR, ".authors")
                        authors = authors_elem.text.replace("Authors:", "").strip()
                    except:
                        authors = "Unknown"
                    
                    # Try to get year
                    try:
                        date_elem = result_element.find_element(By.CSS_SELECTOR, ".is-size-7")
                        year_match = re.search(r'(\d{4})', date_elem.text)
                        year = year_match.group(1) if year_match else "Unknown"
                    except:
                        year = "Unknown"
                    
                    # Try to get abstract
                    try:
                        snippet_elem = result_element.find_element(By.CSS_SELECTOR, ".abstract-full")
                        snippet = snippet_elem.text.replace("Abstract:", "").strip()
                    except:
                        try:
                            snippet_elem = result_element.find_element(By.CSS_SELECTOR, ".abstract")
                            snippet = snippet_elem.text.replace("Abstract:", "").strip()
                        except:
                            snippet = "No abstract available."
                    
                    result = {
                        'title': title,
                        'authors': authors,
                        'year': year,
                        'url': link,
                        'snippet': snippet,
                        'source': 'arXiv'
                    }
                    
                    results.append(result)
                    logger.info(f"Found arXiv result: {title}")
                    
                except Exception as e:
                    logger.warning(f"Error extracting arXiv result {i}: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.warning(f"Error searching arXiv: {str(e)}")
            return []
            
    except Exception as e:
        logger.warning(f"Error accessing arXiv: {str(e)}")
        return []

def search_semantic_scholar(browser, search_term, settings=None):
    """
    Search Semantic Scholar using Selenium.
    
    Args:
        browser: Selenium WebDriver instance
        search_term: Term to search for (string or dict)
        settings: Optional dictionary of settings (e.g., 'captcha_wait_time')
    
    Returns:
        list: List of search results
    """
    if isinstance(search_term, dict):
        search_term = search_term.get('search_term', '')
    
    results = []
    
    try:
        url = "https://www.semanticscholar.org/"
        logger.info(f"Searching Semantic Scholar for: {search_term}")
        
        # Navigate to Semantic Scholar
        browser.get(url)
        time.sleep(3)
        
        # Check for captchas and attempt to handle them
        if detect_captcha(browser)[0]:
            logger.info("Detected captcha on Semantic Scholar")
            if not handle_captcha(browser, url, wait_time=settings.get('captcha_wait_time') if settings else None):
                logger.warning("Failed to handle captcha, continuing anyway")
        
        # Check for site blocking
        if check_for_site_blocking(browser, url):
            logger.warning("Semantic Scholar appears to be blocking access")
            return []
        
        try:
            # Accept cookies if the banner appears
            try:
                cookie_button = browser.find_element(By.ID, "onetrust-accept-btn-handler")
                cookie_button.click()
                time.sleep(1)
            except:
                pass
                
            # Find search box and perform search
            search_input = browser.find_element(By.CSS_SELECTOR, "input[name='q']")
            search_input.clear()
            search_input.send_keys(search_term)
            search_input.send_keys(Keys.RETURN)
            time.sleep(5)
            
            # Check for captchas again after search
            if detect_captcha(browser)[0]:
                logger.info("Detected captcha after search on Semantic Scholar")
                if not handle_captcha(browser, browser.current_url, wait_time=settings.get('captcha_wait_time') if settings else None):
                    logger.warning("Failed to handle captcha, continuing anyway")
                    return []
            
            # Extract results
            result_elements = browser.find_elements(By.CSS_SELECTOR, ".cl-paper-row")
            
            for i, result_element in enumerate(result_elements[:10]):  # Limit to first 10 results
                try:
                    title_elem = result_element.find_element(By.CSS_SELECTOR, ".cl-paper-title")
                    title = title_elem.text.strip()
                    
                    # Get URL
                    try:
                        link = title_elem.get_attribute("href")
                        if not link:
                            link_elem = title_elem.find_element(By.XPATH, ".//a")
                            link = link_elem.get_attribute("href")
                    except:
                        link = browser.current_url
                    
                    # Try to get authors
                    try:
                        authors_elem = result_element.find_element(By.CSS_SELECTOR, ".cl-paper-authors")
                        authors = authors_elem.text.strip()
                    except:
                        authors = "Unknown"
                    
                    # Try to get year
                    try:
                        year_elem = result_element.find_element(By.CSS_SELECTOR, ".cl-paper-publication-date")
                        year_match = re.search(r'(\d{4})', year_elem.text)
                        year = year_match.group(1) if year_match else "Unknown"
                    except:
                        year = "Unknown"
                    
                    # Try to get abstract
                    try:
                        snippet_elem = result_element.find_element(By.CSS_SELECTOR, ".cl-paper-abstract")
                        snippet = snippet_elem.text.strip()
                    except:
                        snippet = "No abstract available."
                    
                    result = {
                        'title': title,
                        'authors': authors,
                        'year': year,
                        'url': link,
                        'snippet': snippet,
                        'source': 'Semantic Scholar'
                    }
                    
                    results.append(result)
                    logger.info(f"Found Semantic Scholar result: {title}")
                    
                except Exception as e:
                    logger.warning(f"Error extracting Semantic Scholar result {i}: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.warning(f"Error searching Semantic Scholar: {str(e)}")
            return []
            
    except Exception as e:
        logger.warning(f"Error accessing Semantic Scholar: {str(e)}")
        return []

def show_search_progress(browser, message, engine=None, progress=0):
    """
    Display a search progress indicator in the browser using a simpler approach
    to avoid Content Security Policy issues.
    
    Args:
        browser: Selenium WebDriver instance
        message: Main message to display
        engine: Current search engine (optional)
        progress: Progress percentage (0-100)
    """
    try:
        # Escape any quotes to prevent JavaScript errors
        message = message.replace("'", "\\'").replace('"', '\\"')
        if engine:
            engine = engine.replace("'", "\\'").replace('"', '\\"')
        
        # Create a simpler progress indicator
        script = """
            (function() {
                // Create or get container
                var container = document.getElementById('search_progress');
                if (!container) {
                    container = document.createElement('div');
                    container.id = 'search_progress';
                    container.style.position = 'fixed';
                    container.style.top = '0';
                    container.style.left = '0';
                    container.style.width = '100%';
                    container.style.backgroundColor = '#4285f4';
                    container.style.color = 'white';
                    container.style.padding = '15px';
                    container.style.zIndex = '9999';
                    container.style.textAlign = 'center';
                    container.style.fontSize = '16px';
                    container.style.fontFamily = 'Arial, sans-serif';
                    div.textContent = '%s';
                    
                    // Add engine info if available
                    if ('%s' && '%s' !== 'None') {
                        var engineElement = document.createElement('div');
                        engineElement.textContent = 'Current engine: ' + '%s';
                        engineElement.style.marginTop = '5px';
                        container.appendChild(engineElement);
                    }
                    
                    // Add progress percentage
                    var percentElement = document.createElement('div');
                    percentElement.textContent = '%s%%';
                    percentElement.style.marginTop = '5px';
                    container.appendChild(percentElement);
                    
                    // Add progress bar container
                    var progressBarContainer = document.createElement('div');
                    progressBarContainer.style.marginTop = '10px';
                    progressBarContainer.style.backgroundColor = 'rgba(255, 255, 255, 0.3)';
                    progressBarContainer.style.height = '10px';
                    progressBarContainer.style.borderRadius = '5px';
                    container.appendChild(progressBarContainer);
                    
                    // Add progress bar
                    var progressBar = document.createElement('div');
                    progressBar.style.width = '%s%%';
                    progressBar.style.height = '100%%';
                    progressBar.style.backgroundColor = 'white';
                    progressBar.style.borderRadius = '5px';
                    progressBarContainer.appendChild(progressBar);
                }
                
                // Update existing container
                else {
                    container.innerHTML = '';
                    var msgElement = document.createElement('div');
                    msgElement.style.fontWeight = 'bold';
                    msgElement.textContent = '%s';
                    container.appendChild(msgElement);
                    
                    if ('%s' && '%s' !== 'None') {
                        var engineElement = document.createElement('div');
                        engineElement.textContent = 'Current engine: ' + '%s';
                        engineElement.style.marginTop = '5px';
                        container.appendChild(engineElement);
                    }
                    
                    var percentElement = document.createElement('div');
                    percentElement.textContent = '%s%%';
                    percentElement.style.marginTop = '5px';
                    container.appendChild(percentElement);
                    
                    var progressBarContainer = document.createElement('div');
                    progressBarContainer.style.marginTop = '10px';
                    progressBarContainer.style.backgroundColor = 'rgba(255, 255, 255, 0.3)';
                    progressBarContainer.style.height = '10px';
                    progressBarContainer.style.borderRadius = '5px';
                    container.appendChild(progressBarContainer);
                    
                    var progressBar = document.createElement('div');
                    progressBar.style.width = '%s%%';
                    progressBar.style.height = '100%%';
                    progressBar.style.backgroundColor = 'white';
                    progressBar.style.borderRadius = '5px';
                    progressBarContainer.appendChild(progressBar);
                }
                
                // Append to body if not already
                if (!document.body.contains(container)) {
                    document.body.appendChild(container);
                }
            })();
        """ % (message, engine, engine, engine, progress, progress)
        
        browser.execute_script(script)
    except Exception as e:
        logger.warning(f"Failed to show search progress: {e}")

def hide_search_progress(browser):
    """
    Hide the search progress indicator.
    
    Args:
        browser: Selenium WebDriver instance
    """
    try:
        browser.execute_script("""
            const notification = document.getElementById('search_progress');
            if (notification) {
                notification.remove();
            }
        """)
    except Exception as e:
        logger.warning(f"Failed to hide search progress: {e}")

def check_for_site_blocking(browser, url):
    """
    Check if a site is blocking our access.
    
    Args:
        browser: Selenium WebDriver instance
        url: URL of the site to check
        
    Returns:
        bool: True if site appears to be blocking access, False otherwise
        
    Raises:
        BlockedSiteException: If the site is in blocked_sites list or appears to be blocking access
    """
    # First check if the site is in the blocked sites list
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    
    if is_site_blocked(domain):
        logger.warning(f"Site is in blocked sites list: {domain}")
        raise BlockedSiteException(f"Site is in blocked sites list: {domain}")
    
    try:
        # Check for common blocking indicators
        blocking_indicators = [
            "Access Denied",
            "Forbidden",
            "Not Found",
            "404",
            "403",
            "Your request has been blocked",
            "Our systems have detected unusual traffic",
            "Please enable cookies",
            "Please enable JavaScript"
        ]
        
        page_source = browser.page_source.lower()
        
        for indicator in blocking_indicators:
            if indicator.lower() in page_source:
                logger.warning(f"Site appears to be blocking access: {url}")
                raise BlockedSiteException(f"Site appears to be blocking access: {url} (Detected: {indicator})")
        
        # If no indicators found, assume site is not blocking
        return False
    
    except BlockedSiteException:
        raise
    except Exception as e:
        logger.warning(f"Error checking for site blocking: {e}")
        return False

def handle_cookie_consent(browser):
    """
    Handle cookie consent banners.
    
    Args:
        browser: Selenium WebDriver instance
        
    Returns:
        bool: True if cookie consent was handled, False otherwise
    """
    try:
        # Check for common cookie consent banners
        consent_indicators = [
            "cookie consent",
            "accept cookies",
            "cookie policy",
            "cookie notice"
        ]
        
        page_source = browser.page_source.lower()
        
        for indicator in consent_indicators:
            if indicator in page_source:
                # Try to find and click the accept button
                try:
                    accept_button = browser.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Agree')]")
                    accept_button.click()
                    logger.info("Cookie consent handled")
                    return True
                except:
                    pass
        
        # If no indicators found, assume no cookie consent is required
        return False
    
    except Exception as e:
        logger.warning(f"Error handling cookie consent: {e}")
        return False

def search_duckduckgo(browser, search_term, settings=None):
    """
    Search DuckDuckGo for academic papers and extract results.
    
    Args:
        browser: Selenium WebDriver
        search_term: Search query
        settings: Dictionary with settings, including:
            - prioritize_pdf: Whether to prioritize PDF results (default: True)
            - max_results: Maximum number of results to return
            - debug: Whether to enable debug mode (default: False)
    
    Returns:
        list: List of dictionaries containing search results
    """
    if settings is None:
        settings = {}
    
    prioritize_pdf = settings.get('prioritize_pdf', True)
    max_results = settings.get('max_results', 10)
    debug_mode = settings.get('debug', False)
    
    results = []
    
    # Process search term if it's a dictionary
    if isinstance(search_term, dict):
        if 'query' in search_term:
            search_term = search_term['query']
        elif 'topic' in search_term:
            search_term = search_term['topic']
    
    # Add filetype:pdf to search term if prioritizing PDFs
    if prioritize_pdf and 'filetype:pdf' not in search_term.lower():
        search_term = f"{search_term} filetype:pdf"
    
    logger.info(f"DuckDuckGo search term: {search_term}")
    
    # Safely show search progress
    def show_progress(message=None):
        try:
            browser.execute_script(
                f"""
                if (!document.getElementById('academic-search-progress')) {{
                    var div = document.createElement('div');
                    div.id = 'academic-search-progress';
                    div.style.position = 'fixed';
                    div.style.top = '0';
                    div.style.left = '0';
                    div.style.width = '100%';
                    div.style.backgroundColor = '#4285f4';
                    div.style.color = 'white';
                    div.style.padding = '10px';
                    div.style.zIndex = '9999';
                    div.style.textAlign = 'center';
                    div.style.fontSize = '16px';
                    div.style.fontFamily = 'Arial, sans-serif';
                    div.textContent = '{message or "Searching DuckDuckGo for academic papers..."}';
                    document.body.appendChild(div);
                }}
                """
            )
        except Exception as e:
            logger.warning(f"Failed to show search progress: {e}")
    
    # Safely hide search progress
    def hide_progress():
        try:
            browser.execute_script(
                """
                var div = document.getElementById('academic-search-progress');
                if (div) {
                    div.parentNode.removeChild(div);
                }
                """
            )
        except Exception as e:
            logger.warning(f"Failed to hide search progress: {e}")
    
    # Debug function to log the page source
    def debug_page():
        if debug_mode:
            try:
                logger.info("=" * 50)
                logger.info(f"Current URL: {browser.current_url}")
                logger.info("Page Title: " + browser.title)
                
                # Save screenshot
                timestamp = int(time.time())
                screenshot_path = f"duckduckgo_debug_{timestamp}.png"
                browser.save_screenshot(screenshot_path)
                logger.info(f"Debug screenshot saved to {screenshot_path}")
                
                # Log HTML source in chunks
                source = browser.page_source
                logger.info(f"Page source length: {len(source)} characters")
                logger.info("=" * 50)
            except Exception as e:
                logger.error(f"Debug error: {e}")
    
    try:
        logger.info("Using DuckDuckGo browser mode")
        
        # Show progress
        show_progress()
        
        # Navigate to DuckDuckGo
        browser.get("https://duckduckgo.com/")
        time.sleep(2)
        
        if debug_mode:
            debug_page()
        
        # Try different selectors for the search box 
        search_box = None
        search_selectors = [
            "input[name='q']",
            "#search_form_input_homepage",
            "#search_form_input",
            "input[type='text']",
            "input.js-search-input"
        ]
        
        for selector in search_selectors:
            try:
                logger.info(f"Trying search box selector: {selector}")
                search_box = WebDriverWait(browser, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                logger.info(f"Found search box using selector: {selector}")
                break
            except Exception as e:
                logger.warning(f"Selector {selector} failed: {e}")
                continue
        
        if not search_box:
            logger.error("Could not find search box on DuckDuckGo")
            hide_progress()
            debug_page()
            return results
        
        # Clear and enter search term
        search_box.clear()
        search_box.send_keys(search_term)
        logger.info(f"Entered search term: {search_term}")
        
        # Try different methods to submit the search
        submit_success = False
        
        try:
            # Method 1: Press Enter
            logger.info("Trying to submit search with Enter key")
            search_box.send_keys(Keys.RETURN)
            submit_success = True
        except Exception as e:
            logger.warning(f"Enter key submission failed: {e}")
            try:
                # Method 2: Click search button
                logger.info("Trying to submit search with search button")
                submit_buttons = [
                    "input[type='submit']",
                    "button[type='submit']",
                    ".search__button",
                    ".search-btn"
                ]
                
                for button_selector in submit_buttons:
                    try:
                        submit_button = browser.find_element(By.CSS_SELECTOR, button_selector)
                        submit_button.click()
                        submit_success = True
                        logger.info(f"Clicked search button with selector: {button_selector}")
                        break
                    except Exception as button_e:
                        logger.warning(f"Button selector {button_selector} failed: {button_e}")
                        continue
            except Exception as e2:
                logger.warning(f"Button click submission failed: {e2}")
                try:
                    # Method 3: Submit the form
                    search_form = browser.find_element(By.CSS_SELECTOR, "#search_form")
                    search_form.submit()
                    submit_success = True
                    logger.info("Form submission successful")
                except Exception as e3:
                    logger.error(f"All methods to submit search failed: {e3}")
                    hide_progress()
                    debug_page()
                    return results
        
        if submit_success:
            logger.info("Search submission successful")
            # Wait for results to load
            time.sleep(3)
            
            if debug_mode:
                debug_page()
            
            # Update progress
            show_progress("Processing search results...")
            
            # Look for "no results" message
            try:
                no_results = browser.find_element(By.CSS_SELECTOR, ".no-results")
                if "No results found" in no_results.text:
                    logger.warning("No results found on DuckDuckGo")
                    hide_progress()
                    return results
            except:
                pass  # No "no results" message found, continue
            
            # Different possible result selectors
            result_selectors = [
                ".result__body", 
                ".result", 
                ".result-link",
                ".nrn-react-div",
                "article",
                ".web-result",
                ".links_main",
                ".serp__results .react-results--main .react-results"
            ]
            
            result_elements = []
            
            for selector in result_selectors:
                try:
                    logger.info(f"Trying result selector: {selector}")
                    result_elements = browser.find_elements(By.CSS_SELECTOR, selector)
                    if result_elements:
                        logger.info(f"Found {len(result_elements)} results with selector: {selector}")
                        break
                except Exception as e:
                    logger.warning(f"Result selector {selector} failed: {e}")
                    continue
            
            logger.info(f"Found {len(result_elements)} potential results")
            
            if not result_elements and debug_mode:
                logger.warning("No result elements found with standard selectors. Trying generic links.")
                try:
                    # As a last resort, try to find any links that might be results
                    links = browser.find_elements(By.TAG_NAME, "a")
                    logger.info(f"Found {len(links)} generic links on the page")
                    
                    # Filter links that look like results (non-empty text, has href)
                    result_links = []
                    for link in links:
                        try:
                            href = link.get_attribute("href")
                            text = link.text.strip()
                            if href and text and not href.startswith("https://duckduckgo.com"):
                                result_links.append(link)
                        except:
                            continue
                    
                    logger.info(f"Filtered to {len(result_links)} potential result links")
                    
                    # If we found some links, create results from them
                    for link in result_links[:max_results]:
                        try:
                            title = link.text.strip() or "Unknown Title"
                            url = link.get_attribute("href")
                            
                            # Skip if no URL or it's an advertisement
                            if not url or "duckduckgo.com/y.js" in url:
                                continue
                                
                            is_pdf = url.lower().endswith(".pdf") or "pdf" in url.lower()
                            
                            # Create result entry
                            result_entry = {
                                "title": title,
                                "url": url,
                                "snippet": "",
                                "source": "DuckDuckGo",
                                "is_pdf": is_pdf,
                            }
                            
                            results.append(result_entry)
                            
                        except Exception as e:
                            logger.error(f"Error processing generic link: {e}")
                            continue
                except Exception as e:
                    logger.error(f"Error processing generic links: {e}")
            
            for result in result_elements[:max_results]:
                try:
                    # Extract title and link using different possible selectors
                    title_element = None
                    link_element = None
                    
                    # Try to find title element
                    for title_selector in [".result__title a", "h2 a", "a.result__a", "a", "h3 a", ".title a"]:
                        try:
                            title_elements = result.find_elements(By.CSS_SELECTOR, title_selector)
                            if title_elements:
                                title_element = title_elements[0]
                                logger.info(f"Found title element with selector: {title_selector}")
                                break
                        except:
                            continue
                    
                    if not title_element:
                        logger.warning("No title element found for result")
                        continue
                    
                    title = title_element.text.strip()
                    logger.info(f"Found result title: {title}")
                    
                    # Use the title element as the link element
                    link_element = title_element
                    
                    url = link_element.get_attribute("href")
                    logger.info(f"Found result URL: {url}")
                    
                    # Skip if no URL found or if it's an advertisement
                    if not url or "duckduckgo.com/y.js" in url:
                        logger.warning(f"Skipping result with invalid URL: {url}")
                        continue
                    
                    # Try to extract snippet
                    snippet = ""
                    for snippet_selector in [".result__snippet", ".result__extras", ".result__body", ".snippet", ".subtitle", "p"]:
                        try:
                            snippet_element = result.find_element(By.CSS_SELECTOR, snippet_selector)
                            snippet = snippet_element.text.strip()
                            if snippet:
                                logger.info(f"Found snippet with selector: {snippet_selector}")
                                break
                        except:
                            continue
                    
                    # Filter for PDF results if prioritizing PDFs
                    is_pdf = False
                    if prioritize_pdf:
                        is_pdf = (
                            url.lower().endswith(".pdf") or 
                            "filetype:pdf" in snippet.lower() or
                            "pdf" in url.lower() or
                            "[PDF]" in title
                        )
                        
                        if not is_pdf and "pdf" not in url.lower() and "pdf" not in snippet.lower():
                            logger.info(f"Skipping non-PDF result: {title}")
                            continue
                        
                        logger.info(f"Found PDF result: {title}")
                    
                    # Extract year if available 
                    year = None
                    year_match = re.search(r'\b(19|20)\d{2}\b', snippet)
                    if year_match:
                        year = year_match.group(0)
                    
                    # Extract author if available (names followed by et al. or multiple names)
                    authors = None
                    author_match = re.search(r'([A-Z][a-z]+ (?:[A-Z][a-z]+))(?: et al\.?|,? (?:and |& )?[A-Z][a-z]+ (?:[A-Z][a-z]+))', snippet)
                    if author_match:
                        authors = author_match.group(0)
                    
                    # Extract journal if available (text in italics or between quotes)
                    journal = None
                    journal_match = re.search(r'["\']([^"\']+)["\']', snippet)
                    if journal_match:
                        journal = journal_match.group(1)
                    
                    # Create result entry
                    result_entry = {
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "source": "DuckDuckGo",
                        "is_pdf": is_pdf,
                    }
                    
                    # Add optional fields if found
                    if year:
                        result_entry["year"] = year
                    if authors:
                        result_entry["authors"] = authors
                    if journal:
                        result_entry["journal"] = journal
                    
                    results.append(result_entry)
                    
                except Exception as e:
                    logger.error(f"Error processing result: {e}")
                    continue
        
        hide_progress()
        return results
        
    except WebDriverException as e:
        logger.error(f"WebDriver error when searching DuckDuckGo: {e}")
        debug_page()
        hide_progress()
        return results
    except Exception as e:
        logger.error(f"Unexpected error when searching DuckDuckGo: {e}")
        debug_page()
        hide_progress()
        return results

def search_academic_databases(topics_subtopics=None, settings=None, browsers=None, headless=True):
    """
    Search for academic papers from Google Scholar and ResearchGate.
    
    Args:
        topics_subtopics (list or dict): Either a list of dictionaries with 'topic' and 'subtopics' keys,
                                         or a list of topics (strings)
        settings (dict): Dictionary of settings
        browsers (list): List of Selenium WebDriver instances (optional)
        headless (bool): Whether to run browsers in headless mode
    
    Returns:
        dict: Dictionary mapping topics to lists of search results
    """
    if settings is None:
        settings = {}
    
    # Default settings
    default_settings = {
        'captcha_wait_time': CAPTCHA_WAIT_TIME,
        'engines': ['google_scholar', 'research_gate', 'pubmed', 'arxiv', 'duckduckgo'],
        'max_results_per_topic': 10,
        'browser_count': 1
    }
    
    # Update settings with defaults for missing keys
    for key, value in default_settings.items():
        if key not in settings:
            settings[key] = value
    
    # Special handling for DuckDuckGo-only mode
    if 'duckduckgo_only' in settings and settings['duckduckgo_only']:
        settings['engines'] = ['duckduckgo']
        logger.info("Using DuckDuckGo as the exclusive search engine")
    
    # Ensure browsers is a list
    if browsers is None:
        browsers = []
    
    # Load blocked sites at the start
    load_blocked_sites()
    
    # Set up browsers if not provided
    if not browsers:
        browser_type = settings.get('browser_type', None)
        for i in range(settings.get('browser_count', 1)):
            try:
                browser = _create_browser(headless=headless, browser_type=browser_type)
                browsers.append(browser)
            except Exception as e:
                logger.error(f"Error setting up browser {i}: {e}")
                # Try to create at least one browser
                if i == 0:
                    continue
    
    # If no browsers are available, return empty results
    if not browsers:
        logger.error("No browsers available for searching")
        return {}
    
    # Distribute browsers
    google_scholar_browser = browsers[0]
    research_gate_browser = browsers[-1]  # Use the last browser for ResearchGate
    
    all_results = {}
    
    # Search for each topic
    for topic in topics_subtopics:
        logger.info(f"Searching for topic: {topic}")
        
        # Google Scholar search
        google_scholar_results = search_google_scholar(google_scholar_browser, topic, settings=settings)
        
        # ResearchGate search
        research_gate_results = search_research_gate(research_gate_browser, topic, settings=settings)
        
        # Combine results
        topic_results = google_scholar_results + research_gate_results
        
        # Sort results by relevance (using a simple heuristic)
        topic_results.sort(key=lambda x: 
            (0 if x.get('is_mock', False) else 1,  # Real results first
             len(x.get('snippet', '')) if 'snippet' in x else 0),  # Then by snippet length
            reverse=True)
        
        all_results[topic] = topic_results
        logger.info(f"Found {len(topic_results)} results for topic: {topic}")
        
        # Search for subtopics if available
        if 'subtopics' in topics_subtopics and topics_subtopics['subtopics']:
            for subtopic in topics_subtopics['subtopics']:
                logger.info(f"Searching for subtopic: {subtopic}")
                
                # Google Scholar search for subtopic
                subtopic_google_results = search_google_scholar(google_scholar_browser, f"{topic} {subtopic}", settings=settings)
                
                # ResearchGate search for subtopic
                subtopic_research_results = search_research_gate(research_gate_browser, f"{topic} {subtopic}", settings=settings)
                
                # Combine results
                subtopic_results = subtopic_google_results + subtopic_research_results
                
                # Sort results by relevance
                subtopic_results.sort(key=lambda x: 
                    (0 if x.get('is_mock', False) else 1,  # Real results first
                     len(x.get('snippet', '')) if 'snippet' in x else 0),  # Then by snippet length
                    reverse=True)
                
                all_results[f"{topic} - {subtopic}"] = subtopic_results
                logger.info(f"Found {len(subtopic_results)} results for subtopic: {subtopic}")
    
    # Clean up browsers if we created them
    if not browsers:
        for browser in browsers:
            try:
                browser.quit()
            except:
                pass
    
    # Save blocked sites at the end
    save_blocked_sites()
    
    return all_results

def sanitize_search_term(search_term):
    """
    Sanitize a search term to make it safe for use in URLs and JavaScript.
    
    Args:
        search_term (str): The search term to sanitize
        
    Returns:
        str: The sanitized search term
    """
    if isinstance(search_term, dict):
        search_term = search_term.get('search_term', '')
    
    # Convert to string if not already
    search_term = str(search_term)
    
    # Replace multiple spaces with a single space
    search_term = ' '.join(search_term.split())
    
    # Remove or escape special characters that might cause issues
    search_term = search_term.replace("'", " ").replace('"', " ")
    
    # Truncate very long search terms
    if len(search_term) > 150:
        search_term = search_term[:150] + "..."
        
    return search_term.strip()
