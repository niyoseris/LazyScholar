#!/usr/bin/env python3
"""
Unit tests for the exceptions module.
"""

import pytest
from web_scraper.exceptions import (
    WebScraperException,
    BrowserException,
    CaptchaException,
    BlockedSiteException,
    PDFDownloadException,
    SearchEngineException
)

class TestExceptions:
    """Tests for the custom exceptions."""
    
    def test_web_scraper_exception(self):
        """Test the base WebScraperException."""
        # Create an exception with a message
        message = "Test exception message"
        exception = WebScraperException(message)
        
        # Check that the message is stored correctly
        assert str(exception) == message
        
        # Check that it's a subclass of Exception
        assert issubclass(WebScraperException, Exception)
        
        # Check that the exception can be raised and caught
        with pytest.raises(WebScraperException) as excinfo:
            raise WebScraperException(message)
        assert str(excinfo.value) == message
    
    def test_browser_exception(self):
        """Test the BrowserException."""
        # Create an exception with a message
        message = "Browser error"
        exception = BrowserException(message)
        
        # Check that the message is stored correctly
        assert str(exception) == message
        
        # Check that it's a subclass of WebScraperException
        assert issubclass(BrowserException, WebScraperException)
        
        # Check that the exception can be raised and caught
        with pytest.raises(BrowserException) as excinfo:
            raise BrowserException(message)
        assert str(excinfo.value) == message
        
        # Check that it can also be caught as a WebScraperException
        with pytest.raises(WebScraperException) as excinfo:
            raise BrowserException(message)
    
    def test_captcha_exception(self):
        """Test the CaptchaException."""
        # Create an exception with a message
        message = "CAPTCHA detected"
        exception = CaptchaException(message)
        
        # Check that the message is stored correctly
        assert str(exception) == message
        
        # Check that it's a subclass of WebScraperException
        assert issubclass(CaptchaException, WebScraperException)
        
        # Check that the exception can be raised and caught
        with pytest.raises(CaptchaException) as excinfo:
            raise CaptchaException(message)
        assert str(excinfo.value) == message
    
    def test_blocked_site_exception(self):
        """Test the BlockedSiteException."""
        # Create an exception with a message
        message = "Site is blocking access"
        exception = BlockedSiteException(message)
        
        # Check that the message is stored correctly
        assert str(exception) == message
        
        # Check that it's a subclass of WebScraperException
        assert issubclass(BlockedSiteException, WebScraperException)
        
        # Check that the exception can be raised and caught
        with pytest.raises(BlockedSiteException) as excinfo:
            raise BlockedSiteException(message)
        assert str(excinfo.value) == message
    
    def test_pdf_download_exception(self):
        """Test the PDFDownloadException."""
        # Create an exception with a message
        message = "Failed to download PDF"
        exception = PDFDownloadException(message)
        
        # Check that the message is stored correctly
        assert str(exception) == message
        
        # Check that it's a subclass of WebScraperException
        assert issubclass(PDFDownloadException, WebScraperException)
        
        # Check that the exception can be raised and caught
        with pytest.raises(PDFDownloadException) as excinfo:
            raise PDFDownloadException(message)
        assert str(excinfo.value) == message
    
    def test_search_engine_exception(self):
        """Test the SearchEngineException."""
        # Create an exception with a message
        message = "Search engine error"
        exception = SearchEngineException(message)
        
        # Check that the message is stored correctly
        assert str(exception) == message
        
        # Check that it's a subclass of WebScraperException
        assert issubclass(SearchEngineException, WebScraperException)
        
        # Check that the exception can be raised and caught
        with pytest.raises(SearchEngineException) as excinfo:
            raise SearchEngineException(message)
        assert str(excinfo.value) == message
    
    def test_exception_with_additional_info(self):
        """Test exceptions with additional information."""
        # Create an exception with additional information
        message = "Error occurred"
        url = "https://example.com"
        status_code = 403
        
        # Create a custom exception class that accepts additional parameters
        class CustomWebScraperException(WebScraperException):
            def __init__(self, message, url=None, status_code=None):
                super().__init__(message)
                self.url = url
                self.status_code = status_code
        
        exception = CustomWebScraperException(message, url=url, status_code=status_code)
        
        # Check that the message and additional info are stored correctly
        assert str(exception) == message
        assert exception.url == url
        assert exception.status_code == status_code
        
        # Check that the exception can be raised and caught
        with pytest.raises(CustomWebScraperException) as excinfo:
            raise exception
        
        # Check that the additional info is preserved
        assert excinfo.value.url == url
        assert excinfo.value.status_code == status_code 