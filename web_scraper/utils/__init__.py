"""
Utilities module for the web scraper package.
Contains utility functions for PDF handling, text extraction, and other helper functions.
"""

import os
import re
import logging
import requests
import time
from typing import Dict, List, Optional, Any, Tuple, Union
from io import BytesIO

# Import file utilities
from .file_utils import ensure_directory, save_json, load_json, create_temp_file, generate_output_filename

# Configure logger
logger = logging.getLogger(__name__)

def sanitize_search_term(search_term: str) -> str:
    """
    Sanitize a search term for use in URLs and queries.
    
    Args:
        search_term: The search term to sanitize
        
    Returns:
        str: The sanitized search term
    """
    # Remove special characters that might cause issues in URLs or queries
    sanitized = re.sub(r'[^\w\s\-\.]', ' ', search_term)
    
    # Replace multiple spaces with a single space
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    return sanitized

def check_for_pdf_links(browser: Any) -> List[str]:
    """
    Check for PDF links on the current page.
    
    Args:
        browser: The browser instance
        
    Returns:
        List[str]: A list of PDF URLs found on the page
    """
    try:
        from selenium.webdriver.common.by import By
    except ImportError:
        logger.warning("Selenium not available, cannot check for PDF links")
        return []
        
    pdf_links = []
    
    try:
        # Find all links on the page
        links = browser.find_elements(By.TAG_NAME, "a")
        
        # Check each link for PDF indicators
        for link in links:
            try:
                href = link.get_attribute("href")
                if href and (href.lower().endswith(".pdf") or "pdf" in href.lower()):
                    pdf_links.append(href)
            except Exception as e:
                logger.debug(f"Error checking link for PDF: {e}")
                continue
        
        logger.info(f"Found {len(pdf_links)} PDF links on the page")
        return pdf_links
    except Exception as e:
        logger.error(f"Error checking for PDF links: {e}")
        return []

def download_pdf(url: str, max_size_mb: int = 10) -> Optional[bytes]:
    """
    Download a PDF from a URL.
    
    Args:
        url: The URL of the PDF to download
        max_size_mb: The maximum size of the PDF in MB
        
    Returns:
        Optional[bytes]: The PDF content as bytes, or None if download failed
    """
    try:
        # Check if requests is available
        if 'requests' not in globals():
            logger.error("Requests module not available, cannot download PDF")
            return None
            
        # Set a timeout and user agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Stream the response to check size before downloading completely
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        
        # Check if the response is successful
        if response.status_code != 200:
            logger.warning(f"Failed to download PDF from {url}, status code: {response.status_code}")
            return None
        
        # Check content type
        content_type = response.headers.get("Content-Type", "").lower()
        if "pdf" not in content_type and "application/octet-stream" not in content_type:
            logger.warning(f"URL does not point to a PDF: {content_type}")
            # Continue anyway, as some servers might not set the correct content type
        
        # Check content length if available
        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > max_size_mb * 1024 * 1024:
            logger.warning(f"PDF is too large: {int(content_length) / (1024 * 1024):.2f} MB (max: {max_size_mb} MB)")
            return None
        
        # Download the PDF content
        pdf_content = BytesIO()
        downloaded_size = 0
        
        for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
            downloaded_size += len(chunk)
            
            # Check if we've exceeded the maximum size
            if downloaded_size > max_size_mb * 1024 * 1024:
                logger.warning(f"PDF download exceeded maximum size of {max_size_mb} MB")
                return None
                
            pdf_content.write(chunk)
        
        logger.info(f"Successfully downloaded PDF from {url} ({downloaded_size / (1024 * 1024):.2f} MB)")
        return pdf_content.getvalue()
    except Exception as e:
        logger.error(f"Error downloading PDF from {url}: {e}")
        return None

def extract_text_from_pdf(pdf_content: bytes) -> Optional[str]:
    """
    Extract text from a PDF.
    
    Args:
        pdf_content: The PDF content as bytes
        
    Returns:
        Optional[str]: The extracted text, or None if extraction failed
    """
    try:
        # Try to import PyPDF2
        try:
            import PyPDF2
            from PyPDF2 import PdfReader
            PYPDF2_AVAILABLE = True
        except ImportError:
            logger.warning("PyPDF2 not available, trying pdfplumber")
            PYPDF2_AVAILABLE = False
        
        # Try to import pdfplumber
        try:
            import pdfplumber
            PDFPLUMBER_AVAILABLE = True
        except ImportError:
            if not PYPDF2_AVAILABLE:
                logger.error("Neither PyPDF2 nor pdfplumber are available, cannot extract text from PDF")
                return None
            PDFPLUMBER_AVAILABLE = False
        
        # Create a BytesIO object from the PDF content
        pdf_file = BytesIO(pdf_content)
        
        # Try to extract text with PyPDF2
        if PYPDF2_AVAILABLE:
            try:
                reader = PdfReader(pdf_file)
                text = ""
                
                for page in reader.pages:
                    text += page.extract_text() + "\n\n"
                
                if text.strip():
                    logger.info("Successfully extracted text from PDF with PyPDF2")
                    return text
                else:
                    logger.warning("PyPDF2 extracted empty text, trying pdfplumber")
            except Exception as e:
                logger.warning(f"Error extracting text with PyPDF2: {e}")
        
        # Try to extract text with pdfplumber
        if PDFPLUMBER_AVAILABLE:
            try:
                with pdfplumber.open(pdf_file) as pdf:
                    text = ""
                    
                    for page in pdf.pages:
                        text += page.extract_text() + "\n\n"
                    
                    if text.strip():
                        logger.info("Successfully extracted text from PDF with pdfplumber")
                        return text
                    else:
                        logger.warning("pdfplumber extracted empty text")
            except Exception as e:
                logger.warning(f"Error extracting text with pdfplumber: {e}")
        
        logger.error("Failed to extract text from PDF with all available methods")
        return None
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return None

def show_search_progress(browser: Any, message: str, engine: Optional[str] = None, progress: int = 0) -> None:
    """
    Show search progress in the browser.
    
    Args:
        browser: The browser instance
        message: The message to display
        engine: The search engine being used
        progress: The progress percentage (0-100)
    """
    try:
        # Ensure progress is between 0 and 100
        progress = max(0, min(100, progress))
        
        # Create a progress message
        engine_text = f" ({engine})" if engine else ""
        progress_text = f"{progress}%" if progress > 0 else ""
        
        # Create the progress bar HTML
        progress_bar = f"""
        <div style="width: 100%; background-color: #f0f0f0; border-radius: 5px; margin-top: 5px;">
            <div style="width: {progress}%; height: 20px; background-color: #4CAF50; border-radius: 5px; text-align: center; line-height: 20px; color: white;">
                {progress_text}
            </div>
        </div>
        """ if progress > 0 else ""
        
        # Create the notification HTML
        notification_html = f"""
        <div id="search_progress_notification" style="position: fixed; top: 0; left: 0; width: 100%; background-color: #3498db; color: white; padding: 15px; z-index: 9999; text-align: center; font-weight: bold; font-size: 16px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
            <div>{message}{engine_text}</div>
            {progress_bar}
        </div>
        """
        
        # Inject the notification into the page
        browser.execute_script(f"""
        // Remove existing notification if present
        const existingNotification = document.getElementById('search_progress_notification');
        if (existingNotification) {{
            existingNotification.remove();
        }}
        
        // Create and add the new notification
        const div = document.createElement('div');
        div.innerHTML = `{notification_html}`;
        document.body.appendChild(div.firstChild);
        """)
        
        logger.debug(f"Showing search progress: {message}{engine_text} ({progress}%)")
    except Exception as e:
        logger.warning(f"Error showing search progress: {e}")

def hide_search_progress(browser: Any) -> None:
    """
    Hide the search progress notification in the browser.
    
    Args:
        browser: The browser instance
    """
    try:
        browser.execute_script("""
        const notification = document.getElementById('search_progress_notification');
        if (notification) {
            notification.remove();
        }
        """)
        
        logger.debug("Hiding search progress notification")
    except Exception as e:
        logger.warning(f"Error hiding search progress: {e}")

def check_for_site_blocking(browser: Any, url: str) -> bool:
    """
    Check if a site is blocking automated access.
    
    Args:
        browser: The browser instance
        url: The URL being accessed
        
    Returns:
        bool: True if the site is blocking access, False otherwise
    """
    from ..config import add_to_blocked_sites
    from ..exceptions import BlockedSiteException
    
    # Check for common blocking indicators in the page source
    blocking_indicators = [
        "access denied",
        "automated access",
        "bot detected",
        "captcha",
        "cloudflare",
        "ddos protection",
        "denied access",
        "forbidden",
        "human verification",
        "security check",
        "too many requests",
        "unusual traffic",
        "your ip has been blocked"
    ]
    
    try:
        page_source = browser.page_source.lower()
        page_title = browser.title.lower()
        current_url = browser.current_url.lower()
        
        # Check if we've been redirected to a known blocking page
        blocking_urls = [
            "cloudflare.com/",
            "captcha",
            "challenge",
            "blocked",
            "security-check",
            "access-denied",
            "403",
            "forbidden"
        ]
        
        # Check if we've been redirected to a blocking URL
        for blocking_url in blocking_urls:
            if blocking_url in current_url and blocking_url not in url:
                logger.warning(f"Redirected to blocking URL: {current_url}")
                blocked_domain = add_to_blocked_sites(url)
                raise BlockedSiteException(f"Site {blocked_domain} appears to be blocking automated access")
        
        # Check for blocking indicators in the page source
        for indicator in blocking_indicators:
            if indicator in page_source or indicator in page_title:
                logger.warning(f"Blocking indicator found: {indicator}")
                blocked_domain = add_to_blocked_sites(url)
                raise BlockedSiteException(f"Site {blocked_domain} appears to be blocking automated access")
        
        # Check for very short page source (often indicates blocking)
        if len(page_source) < 200 and "404" in page_source:
            logger.warning("Very short page source, possible blocking")
            blocked_domain = add_to_blocked_sites(url)
            raise BlockedSiteException(f"Site {blocked_domain} returned a very short page, possible blocking")
        
        return False
    except BlockedSiteException:
        # Re-raise BlockedSiteException
        raise
    except Exception as e:
        logger.error(f"Error checking for site blocking: {e}")
        return False

def handle_cookie_consent(browser: Any) -> bool:
    """
    Handle cookie consent dialogs on websites.
    
    Args:
        browser: The browser instance
        
    Returns:
        bool: True if a cookie consent dialog was handled, False otherwise
    """
    try:
        from selenium.webdriver.common.by import By
    except ImportError:
        logger.warning("Selenium not available, cannot handle cookie consent")
        return False
        
    # Common cookie consent button selectors
    cookie_button_selectors = [
        # Common class names and IDs
        ".accept-cookies", "#accept-cookies",
        ".accept-cookie", "#accept-cookie",
        ".accept", "#accept",
        ".agree", "#agree",
        ".agree-button", "#agree-button",
        ".cookie-accept", "#cookie-accept",
        ".cookie-consent-accept", "#cookie-consent-accept",
        ".cc-accept", "#cc-accept",
        ".cc-dismiss", "#cc-dismiss",
        ".cc-allow", "#cc-allow",
        
        # Common text content
        "//button[contains(text(), 'Accept')]",
        "//button[contains(text(), 'Accept All')]",
        "//button[contains(text(), 'I Accept')]",
        "//button[contains(text(), 'Agree')]",
        "//button[contains(text(), 'I Agree')]",
        "//button[contains(text(), 'OK')]",
        "//button[contains(text(), 'Got it')]",
        "//button[contains(text(), 'Allow')]",
        "//button[contains(text(), 'Allow All')]",
        "//button[contains(text(), 'Continue')]",
        
        # Links with similar text
        "//a[contains(text(), 'Accept')]",
        "//a[contains(text(), 'Accept All')]",
        "//a[contains(text(), 'I Accept')]",
        "//a[contains(text(), 'Agree')]",
        "//a[contains(text(), 'I Agree')]",
        "//a[contains(text(), 'OK')]",
        "//a[contains(text(), 'Got it')]",
        "//a[contains(text(), 'Allow')]",
        "//a[contains(text(), 'Allow All')]",
        "//a[contains(text(), 'Continue')]",
    ]
    
    # Try each selector
    for selector in cookie_button_selectors:
        try:
            # Determine the selector type
            if selector.startswith("//"):
                by = By.XPATH
            else:
                by = By.CSS_SELECTOR
                
            # Find elements matching the selector
            elements = browser.find_elements(by, selector)
            
            # Try to click each element
            for element in elements:
                if element.is_displayed():
                    element.click()
                    logger.info(f"Clicked cookie consent button: {selector}")
                    time.sleep(1)  # Wait for any animations to complete
                    return True
        except Exception as e:
            # Ignore errors and try the next selector
            continue
    
    # No cookie consent dialog found or handled
    return False
