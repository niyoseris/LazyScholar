#!/usr/bin/env python3
"""
Unit tests for the utils module.
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open
import io
import logging

from web_scraper.utils import (
    sanitize_search_term,
    check_for_pdf_links,
    download_pdf,
    extract_text_from_pdf,
    show_search_progress,
    hide_search_progress,
    check_for_site_blocking,
    handle_cookie_consent
)
from web_scraper.exceptions import PDFDownloadException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestSanitizeSearchTerm:
    """Tests for the sanitize_search_term function."""
    
    def test_basic_sanitization(self):
        """Test basic sanitization of search terms."""
        # Test removing special characters
        assert sanitize_search_term("machine learning!@#$%^&*()") == "machine learning"
        
        # Test trimming whitespace
        assert sanitize_search_term("  machine learning  ") == "machine learning"
        
        # Test replacing multiple spaces with single space
        assert sanitize_search_term("machine    learning") == "machine learning"
        
        # Test converting to lowercase
        assert sanitize_search_term("MACHINE LEARNING") == "machine learning"
        
        # Test complex sanitization
        assert sanitize_search_term("  MACHINE   LEARNING!@#$%^&*()  ") == "machine learning"
    
    def test_empty_input(self):
        """Test sanitization of empty input."""
        assert sanitize_search_term("") == ""
        assert sanitize_search_term("   ") == ""
    
    def test_non_string_input(self):
        """Test sanitization of non-string input."""
        # Should convert to string and sanitize
        assert sanitize_search_term(123) == "123"
        assert sanitize_search_term(None) == "none"
        assert sanitize_search_term(["machine", "learning"]) == "machine learning"

@pytest.mark.browser
class TestCheckForPdfLinks:
    """Tests for the check_for_pdf_links function."""
    
    def test_no_pdf_links(self):
        """Test when no PDF links are present."""
        # Mock browser with no PDF links
        mock_browser = MagicMock()
        mock_browser.find_elements.return_value = []
        
        # Call the function
        pdf_links = check_for_pdf_links(mock_browser)
        
        # Verify empty result
        assert pdf_links == []
    
    def test_with_pdf_links(self):
        """Test when PDF links are present."""
        # Mock browser with PDF links
        mock_browser = MagicMock()
        
        # Create mock link elements
        mock_link1 = MagicMock()
        mock_link1.get_attribute.return_value = "https://example.com/paper1.pdf"
        
        mock_link2 = MagicMock()
        mock_link2.get_attribute.return_value = "https://example.com/paper2.pdf"
        
        mock_browser.find_elements.return_value = [mock_link1, mock_link2]
        
        # Call the function
        pdf_links = check_for_pdf_links(mock_browser)
        
        # Verify the links were found
        assert len(pdf_links) == 2
        assert "https://example.com/paper1.pdf" in pdf_links
        assert "https://example.com/paper2.pdf" in pdf_links
    
    def test_with_non_pdf_links(self):
        """Test when non-PDF links are present."""
        # Mock browser with mixed links
        mock_browser = MagicMock()
        
        # Create mock link elements
        mock_link1 = MagicMock()
        mock_link1.get_attribute.return_value = "https://example.com/paper1.pdf"
        
        mock_link2 = MagicMock()
        mock_link2.get_attribute.return_value = "https://example.com/paper2.html"
        
        mock_link3 = MagicMock()
        mock_link3.get_attribute.return_value = "https://example.com/paper3.PDF"  # Test case insensitivity
        
        mock_browser.find_elements.return_value = [mock_link1, mock_link2, mock_link3]
        
        # Call the function
        pdf_links = check_for_pdf_links(mock_browser)
        
        # Verify only PDF links were found
        assert len(pdf_links) == 2
        assert "https://example.com/paper1.pdf" in pdf_links
        assert "https://example.com/paper3.PDF" in pdf_links
        assert "https://example.com/paper2.html" not in pdf_links

@pytest.mark.pdf
class TestDownloadPdf:
    """Tests for the download_pdf function."""
    
    @patch('requests.get')
    def test_successful_download(self, mock_get):
        """Test successful PDF download."""
        # Mock response with PDF content
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/pdf'}
        mock_response.content = b'%PDF-1.4 mock PDF content'
        mock_get.return_value = mock_response
        
        # Call the function
        pdf_content = download_pdf("https://example.com/paper.pdf")
        
        # Verify the PDF content was returned
        assert pdf_content == b'%PDF-1.4 mock PDF content'
        
        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            "https://example.com/paper.pdf",
            headers={'User-Agent': pytest.approx(str)},
            timeout=pytest.approx(int)
        )
    
    @patch('requests.get')
    def test_non_pdf_content_type(self, mock_get):
        """Test handling of non-PDF content type."""
        # Mock response with non-PDF content
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.content = b'<html>Not a PDF</html>'
        mock_get.return_value = mock_response
        
        # Call the function, should raise an exception
        with pytest.raises(PDFDownloadException) as excinfo:
            download_pdf("https://example.com/paper.html")
        
        # Verify the exception message
        assert "not a PDF" in str(excinfo.value).lower()
    
    @patch('requests.get')
    def test_failed_download(self, mock_get):
        """Test handling of failed download."""
        # Mock response with error status
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.headers = {'Content-Type': 'application/pdf'}
        mock_get.return_value = mock_response
        
        # Call the function, should raise an exception
        with pytest.raises(PDFDownloadException) as excinfo:
            download_pdf("https://example.com/nonexistent.pdf")
        
        # Verify the exception message
        assert "failed to download" in str(excinfo.value).lower()
    
    @patch('requests.get')
    def test_exception_during_download(self, mock_get):
        """Test handling of exception during download."""
        # Mock get to raise an exception
        mock_get.side_effect = Exception("Connection error")
        
        # Call the function, should raise a PDFDownloadException
        with pytest.raises(PDFDownloadException) as excinfo:
            download_pdf("https://example.com/paper.pdf")
        
        # Verify the exception message
        assert "error downloading" in str(excinfo.value).lower()

@pytest.mark.pdf
class TestExtractTextFromPdf:
    """Tests for the extract_text_from_pdf function."""
    
    @patch('PyPDF2.PdfReader')
    def test_successful_extraction_with_pypdf2(self, mock_pdf_reader):
        """Test successful text extraction with PyPDF2."""
        # Mock PyPDF2 reader
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [MagicMock(), MagicMock()]
        mock_reader_instance.pages[0].extract_text.return_value = "Page 1 content"
        mock_reader_instance.pages[1].extract_text.return_value = "Page 2 content"
        mock_pdf_reader.return_value = mock_reader_instance
        
        # Call the function
        text = extract_text_from_pdf(b'%PDF-1.4 mock PDF content')
        
        # Verify the extracted text
        assert text == "Page 1 content\nPage 2 content"
    
    @patch('PyPDF2.PdfReader')
    @patch('pdfplumber.open')
    def test_fallback_to_pdfplumber(self, mock_pdfplumber_open, mock_pdf_reader):
        """Test fallback to pdfplumber when PyPDF2 fails."""
        # Mock PyPDF2 reader to raise an exception
        mock_pdf_reader.side_effect = Exception("PyPDF2 error")
        
        # Mock pdfplumber
        mock_plumber_instance = MagicMock()
        mock_plumber_instance.pages = [MagicMock(), MagicMock()]
        mock_plumber_instance.pages[0].extract_text.return_value = "Plumber page 1"
        mock_plumber_instance.pages[1].extract_text.return_value = "Plumber page 2"
        mock_pdfplumber_open.return_value = mock_plumber_instance
        
        # Call the function
        text = extract_text_from_pdf(b'%PDF-1.4 mock PDF content')
        
        # Verify the extracted text
        assert text == "Plumber page 1\nPlumber page 2"
    
    @patch('PyPDF2.PdfReader')
    @patch('pdfplumber.open')
    def test_both_extractors_fail(self, mock_pdfplumber_open, mock_pdf_reader):
        """Test handling when both extractors fail."""
        # Mock both extractors to raise exceptions
        mock_pdf_reader.side_effect = Exception("PyPDF2 error")
        mock_pdfplumber_open.side_effect = Exception("pdfplumber error")
        
        # Call the function
        text = extract_text_from_pdf(b'%PDF-1.4 mock PDF content')
        
        # Verify empty string is returned
        assert text == ""

@pytest.mark.browser
class TestBrowserNotifications:
    """Tests for browser notification functions."""
    
    def test_show_search_progress(self):
        """Test showing search progress notification."""
        # Mock browser
        mock_browser = MagicMock()
        
        # Call the function
        show_search_progress(mock_browser, "Searching Google Scholar")
        
        # Verify the browser executed the JavaScript
        mock_browser.execute_script.assert_called_once()
        
        # Check that the script contains the message
        script_arg = mock_browser.execute_script.call_args[0][0]
        assert "Searching Google Scholar" in script_arg
    
    def test_hide_search_progress(self):
        """Test hiding search progress notification."""
        # Mock browser
        mock_browser = MagicMock()
        
        # Call the function
        hide_search_progress(mock_browser)
        
        # Verify the browser executed the JavaScript
        mock_browser.execute_script.assert_called_once()
        
        # Check that the script removes the notification
        script_arg = mock_browser.execute_script.call_args[0][0]
        assert "remove" in script_arg.lower()

@pytest.mark.browser
class TestSiteBlocking:
    """Tests for site blocking detection."""
    
    def test_site_blocking_detected(self):
        """Test detection of site blocking."""
        # Mock browser with blocking indicators
        mock_browser = MagicMock()
        mock_browser.page_source = """
        <html>
            <body>
                <div>Access Denied</div>
                <p>Your IP address has been temporarily blocked</p>
            </body>
        </html>
        """
        
        # Call the function
        is_blocked = check_for_site_blocking(mock_browser)
        
        # Verify blocking was detected
        assert is_blocked is True
    
    def test_no_site_blocking(self):
        """Test when no site blocking is present."""
        # Mock browser with no blocking indicators
        mock_browser = MagicMock()
        mock_browser.page_source = """
        <html>
            <body>
                <div>Welcome to our site</div>
                <p>Here are your search results</p>
            </body>
        </html>
        """
        
        # Call the function
        is_blocked = check_for_site_blocking(mock_browser)
        
        # Verify no blocking was detected
        assert is_blocked is False

@pytest.mark.browser
class TestCookieConsent:
    """Tests for cookie consent handling."""
    
    def test_cookie_consent_found_and_clicked(self):
        """Test finding and clicking cookie consent button."""
        # Mock browser with cookie consent button
        mock_browser = MagicMock()
        mock_button = MagicMock()
        mock_browser.find_elements.return_value = [mock_button]
        
        # Call the function
        result = handle_cookie_consent(mock_browser)
        
        # Verify the button was clicked
        mock_button.click.assert_called_once()
        assert result is True
    
    def test_no_cookie_consent_found(self):
        """Test when no cookie consent button is found."""
        # Mock browser with no cookie consent button
        mock_browser = MagicMock()
        mock_browser.find_elements.return_value = []
        
        # Call the function
        result = handle_cookie_consent(mock_browser)
        
        # Verify no button was clicked
        assert result is True  # Still returns True as it's not an error
    
    def test_cookie_consent_click_fails(self):
        """Test handling when clicking cookie consent button fails."""
        # Mock browser with cookie consent button that raises exception when clicked
        mock_browser = MagicMock()
        mock_button = MagicMock()
        mock_button.click.side_effect = Exception("Click error")
        mock_browser.find_elements.return_value = [mock_button]
        
        # Call the function
        result = handle_cookie_consent(mock_browser)
        
        # Verify the function handled the exception
        assert result is False  # Returns False due to the error 