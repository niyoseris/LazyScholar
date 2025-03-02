#!/usr/bin/env python3
"""
Unit tests for the browser module.
"""

import pytest
from unittest.mock import MagicMock, patch
import logging

from web_scraper.browser import setup_browser, close_browser
from web_scraper.exceptions import BrowserException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@pytest.mark.browser
class TestBrowserSetup:
    """Tests for browser setup functionality."""
    
    @patch('selenium.webdriver.Chrome')
    @patch('selenium.webdriver.chrome.service.Service')
    @patch('selenium.webdriver.chrome.options.Options')
    def test_setup_chrome_browser(self, mock_options, mock_service, mock_chrome):
        """Test setting up a Chrome browser."""
        # Mock Chrome options
        options_instance = MagicMock()
        mock_options.return_value = options_instance
        
        # Mock Chrome service
        service_instance = MagicMock()
        mock_service.return_value = service_instance
        
        # Mock Chrome webdriver
        browser_instance = MagicMock()
        mock_chrome.return_value = browser_instance
        
        # Call setup_browser with Chrome
        browser = setup_browser(browser_type="chrome", headless=True)
        
        # Check that the browser was set up correctly
        assert browser == browser_instance
        
        # Check that the options were set correctly
        options_instance.add_argument.assert_any_call("--headless")
        
        # Check that the Chrome webdriver was created with the right parameters
        mock_chrome.assert_called_once_with(service=service_instance, options=options_instance)
    
    @patch('selenium.webdriver.Firefox')
    @patch('selenium.webdriver.firefox.service.Service')
    @patch('selenium.webdriver.firefox.options.Options')
    def test_setup_firefox_browser(self, mock_options, mock_service, mock_firefox):
        """Test setting up a Firefox browser."""
        # Mock Firefox options
        options_instance = MagicMock()
        mock_options.return_value = options_instance
        
        # Mock Firefox service
        service_instance = MagicMock()
        mock_service.return_value = service_instance
        
        # Mock Firefox webdriver
        browser_instance = MagicMock()
        mock_firefox.return_value = browser_instance
        
        # Call setup_browser with Firefox
        browser = setup_browser(browser_type="firefox", headless=True)
        
        # Check that the browser was set up correctly
        assert browser == browser_instance
        
        # Check that the options were set correctly
        options_instance.add_argument.assert_any_call("-headless")
        
        # Check that the Firefox webdriver was created with the right parameters
        mock_firefox.assert_called_once_with(service=service_instance, options=options_instance)
    
    @patch('selenium.webdriver.Edge')
    @patch('selenium.webdriver.edge.service.Service')
    @patch('selenium.webdriver.edge.options.Options')
    def test_setup_edge_browser(self, mock_options, mock_service, mock_edge):
        """Test setting up an Edge browser."""
        # Mock Edge options
        options_instance = MagicMock()
        mock_options.return_value = options_instance
        
        # Mock Edge service
        service_instance = MagicMock()
        mock_service.return_value = service_instance
        
        # Mock Edge webdriver
        browser_instance = MagicMock()
        mock_edge.return_value = browser_instance
        
        # Call setup_browser with Edge
        browser = setup_browser(browser_type="edge", headless=True)
        
        # Check that the browser was set up correctly
        assert browser == browser_instance
        
        # Check that the options were set correctly
        options_instance.add_argument.assert_any_call("--headless")
        
        # Check that the Edge webdriver was created with the right parameters
        mock_edge.assert_called_once_with(service=service_instance, options=options_instance)
    
    def test_setup_unsupported_browser(self):
        """Test setting up an unsupported browser type."""
        # Call setup_browser with an unsupported browser type
        with pytest.raises(BrowserException) as excinfo:
            setup_browser(browser_type="unsupported")
        
        # Check that the exception message mentions the unsupported browser type
        assert "unsupported" in str(excinfo.value).lower()
    
    @patch('selenium.webdriver.Chrome')
    @patch('selenium.webdriver.chrome.service.Service')
    @patch('selenium.webdriver.chrome.options.Options')
    def test_setup_browser_with_user_agent(self, mock_options, mock_service, mock_chrome):
        """Test setting up a browser with a custom user agent."""
        # Mock Chrome options
        options_instance = MagicMock()
        mock_options.return_value = options_instance
        
        # Mock Chrome service
        service_instance = MagicMock()
        mock_service.return_value = service_instance
        
        # Mock Chrome webdriver
        browser_instance = MagicMock()
        mock_chrome.return_value = browser_instance
        
        # Custom user agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Custom User Agent"
        
        # Call setup_browser with a custom user agent
        browser = setup_browser(browser_type="chrome", headless=True, user_agent=user_agent)
        
        # Check that the user agent was set correctly
        options_instance.add_argument.assert_any_call(f"user-agent={user_agent}")
    
    @patch('selenium.webdriver.Chrome')
    @patch('selenium.webdriver.chrome.service.Service')
    @patch('selenium.webdriver.chrome.options.Options')
    def test_setup_browser_with_additional_options(self, mock_options, mock_service, mock_chrome):
        """Test setting up a browser with additional options."""
        # Mock Chrome options
        options_instance = MagicMock()
        mock_options.return_value = options_instance
        
        # Mock Chrome service
        service_instance = MagicMock()
        mock_service.return_value = service_instance
        
        # Mock Chrome webdriver
        browser_instance = MagicMock()
        mock_chrome.return_value = browser_instance
        
        # Additional options
        additional_options = ["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]
        
        # Call setup_browser with additional options
        browser = setup_browser(browser_type="chrome", headless=True, additional_options=additional_options)
        
        # Check that the additional options were set correctly
        for option in additional_options:
            options_instance.add_argument.assert_any_call(option)

@pytest.mark.browser
class TestBrowserClose:
    """Tests for browser close functionality."""
    
    def test_close_browser(self):
        """Test closing a browser."""
        # Mock browser
        mock_browser = MagicMock()
        
        # Call close_browser
        close_browser(mock_browser)
        
        # Check that the browser was closed
        mock_browser.quit.assert_called_once()
    
    def test_close_browser_with_exception(self):
        """Test closing a browser that raises an exception."""
        # Mock browser that raises an exception when quit is called
        mock_browser = MagicMock()
        mock_browser.quit.side_effect = Exception("Failed to quit")
        
        # Call close_browser
        # Should not raise an exception
        close_browser(mock_browser)
        
        # Check that the browser.quit was called
        mock_browser.quit.assert_called_once()
    
    def test_close_browser_with_none(self):
        """Test closing a None browser."""
        # Call close_browser with None
        # Should not raise an exception
        close_browser(None) 