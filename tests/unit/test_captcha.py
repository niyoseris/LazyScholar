#!/usr/bin/env python3
"""
Unit tests for the CAPTCHA module.
"""

import pytest
from unittest.mock import MagicMock, patch
import os
import time

from web_scraper.captcha import detect_captcha, handle_captcha

@pytest.mark.captcha
class TestDetectCaptcha:
    """Tests for the detect_captcha function."""
    
    def test_no_captcha(self):
        """Test when no CAPTCHA is present."""
        # Mock browser with no CAPTCHA indicators
        mock_browser = MagicMock()
        mock_browser.page_source = """
        <html>
            <body>
                <div>Normal content</div>
                <p>No CAPTCHA here</p>
            </body>
        </html>
        """
        mock_browser.find_elements.return_value = []
        
        is_captcha, captcha_type = detect_captcha(mock_browser)
        assert is_captcha is False
        assert captcha_type is None
    
    def test_text_based_captcha(self):
        """Test detection of text-based CAPTCHA indicators."""
        # Mock browser with CAPTCHA text indicators
        mock_browser = MagicMock()
        mock_browser.page_source = """
        <html>
            <body>
                <div>Please complete the CAPTCHA</div>
                <p>Verify you are not a robot</p>
            </body>
        </html>
        """
        mock_browser.find_elements.return_value = []
        
        is_captcha, captcha_type = detect_captcha(mock_browser)
        assert is_captcha is True
        assert captcha_type == "text"
    
    def test_recaptcha_element(self):
        """Test detection of reCAPTCHA elements."""
        # Mock browser with reCAPTCHA elements
        mock_browser = MagicMock()
        mock_browser.page_source = "<html><body>Normal content</body></html>"
        
        # First call for reCAPTCHA elements returns elements
        mock_element = MagicMock()
        mock_browser.find_elements.side_effect = [
            [mock_element],  # reCAPTCHA elements
            []               # hCaptcha elements
        ]
        
        is_captcha, captcha_type = detect_captcha(mock_browser)
        assert is_captcha is True
        assert captcha_type == "recaptcha"
    
    def test_hcaptcha_element(self):
        """Test detection of hCaptcha elements."""
        # Mock browser with hCaptcha elements
        mock_browser = MagicMock()
        mock_browser.page_source = "<html><body>Normal content</body></html>"
        
        # First call for reCAPTCHA elements returns empty, second call for hCaptcha returns elements
        mock_element = MagicMock()
        mock_browser.find_elements.side_effect = [
            [],               # reCAPTCHA elements
            [mock_element]    # hCaptcha elements
        ]
        
        is_captcha, captcha_type = detect_captcha(mock_browser)
        assert is_captcha is True
        assert captcha_type == "hcaptcha"
    
    def test_exception_during_detection(self):
        """Test handling of exceptions during CAPTCHA detection."""
        # Mock browser that raises an exception
        mock_browser = MagicMock()
        mock_browser.page_source = "<html><body>Normal content</body></html>"
        mock_browser.find_elements.side_effect = Exception("Element not found")
        
        is_captcha, captcha_type = detect_captcha(mock_browser)
        # Should default to no CAPTCHA when an exception occurs
        assert is_captcha is False
        assert captcha_type is None

@pytest.mark.captcha
class TestHandleCaptcha:
    """Tests for the handle_captcha function."""
    
    @patch('time.sleep', return_value=None)
    @patch('os.path.exists', return_value=True)
    @patch('os.makedirs')
    def test_captcha_handling_with_screenshot(self, mock_makedirs, mock_path_exists, mock_sleep):
        """Test CAPTCHA handling with screenshot."""
        # Mock browser
        mock_browser = MagicMock()
        mock_browser.save_screenshot.return_value = True
        
        # Mock detect_captcha to initially return True, then False after "solving"
        with patch('web_scraper.captcha.detect_captcha') as mock_detect:
            mock_detect.side_effect = [(True, "recaptcha"), (False, None)]
            
            # Call handle_captcha
            result = handle_captcha(mock_browser, "recaptcha", wait_time=1)
            
            # Verify the function took a screenshot
            mock_browser.save_screenshot.assert_called_once()
            
            # Verify the function checked if the CAPTCHA was solved
            assert mock_detect.call_count == 2
            
            # Verify the function returned True (CAPTCHA solved)
            assert result is True
    
    @patch('time.sleep', return_value=None)
    @patch('os.path.exists', return_value=False)
    @patch('os.makedirs')
    def test_captcha_handling_creates_directory(self, mock_makedirs, mock_path_exists, mock_sleep):
        """Test that CAPTCHA handling creates the screenshot directory if it doesn't exist."""
        # Mock browser
        mock_browser = MagicMock()
        
        # Mock detect_captcha to return True (CAPTCHA not solved)
        with patch('web_scraper.captcha.detect_captcha', return_value=(True, "recaptcha")):
            # Call handle_captcha with a short wait time
            handle_captcha(mock_browser, "recaptcha", wait_time=0.1)
            
            # Verify the function created the directory
            mock_makedirs.assert_called_once()
    
    @patch('time.sleep', return_value=None)
    def test_captcha_not_solved(self, mock_sleep):
        """Test when CAPTCHA is not solved within the wait time."""
        # Mock browser
        mock_browser = MagicMock()
        
        # Mock detect_captcha to always return True (CAPTCHA not solved)
        with patch('web_scraper.captcha.detect_captcha', return_value=(True, "recaptcha")):
            # Call handle_captcha with a short wait time
            result = handle_captcha(mock_browser, "recaptcha", wait_time=0.1)
            
            # Verify the function returned False (CAPTCHA not solved)
            assert result is False
    
    @patch('time.sleep', return_value=None)
    @patch('web_scraper.captcha.detect_captcha')
    def test_exception_during_handling(self, mock_detect, mock_sleep):
        """Test handling of exceptions during CAPTCHA handling."""
        # Mock browser
        mock_browser = MagicMock()
        
        # Mock detect_captcha to raise an exception
        mock_detect.side_effect = Exception("Detection error")
        
        # Call handle_captcha
        result = handle_captcha(mock_browser, "recaptcha", wait_time=0.1)
        
        # Verify the function returned False due to the exception
        assert result is False 