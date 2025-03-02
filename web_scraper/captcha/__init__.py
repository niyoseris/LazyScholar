"""
Captcha module for the web scraper package.
Contains functions for detecting and handling captchas.
"""

import os
import time
import logging
import platform
from datetime import datetime
from typing import Tuple, Optional, Any

from ..config import CAPTCHA_DETECTION_ENABLED, CAPTCHA_AUTO_SOLVE_ENABLED, CAPTCHA_WAIT_TIME, CAPTCHA_SCREENSHOT_DIR

# Configure logger
logger = logging.getLogger(__name__)

def detect_captcha(browser: Any) -> Tuple[bool, Optional[str]]:
    """
    Detect if a captcha is present on the current page.
    
    Args:
        browser: Selenium WebDriver instance
        
    Returns:
        bool: True if captcha detected, False otherwise
        str: Type of captcha detected or None
    """
    try:
        from selenium.webdriver.common.by import By
    except ImportError:
        logger.warning("Selenium not available, captcha detection disabled")
        return False, None
        
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

def handle_captcha(browser: Any, url: str, wait_time: Optional[int] = None) -> bool:
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
