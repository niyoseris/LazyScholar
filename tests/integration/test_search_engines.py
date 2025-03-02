#!/usr/bin/env python3
"""
Integration tests for the search engines module.
"""

import pytest
from unittest.mock import MagicMock, patch
import logging

from web_scraper.search_engines import (
    get_search_engine_function,
    search_google_scholar,
    search_research_gate
)
from web_scraper.exceptions import SearchEngineException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@pytest.mark.integration
class TestSearchEngineRegistry:
    """Tests for the search engine registry functionality."""
    
    def test_get_search_engine_function(self):
        """Test getting search engine functions from the registry."""
        # Get the Google Scholar search function
        google_func = get_search_engine_function("google_scholar")
        assert google_func == search_google_scholar
        
        # Get the ResearchGate search function
        research_gate_func = get_search_engine_function("research_gate")
        assert research_gate_func == search_research_gate
        
        # Try to get a non-existent search engine function
        with pytest.raises(SearchEngineException) as excinfo:
            get_search_engine_function("non_existent_engine")
        assert "not supported" in str(excinfo.value).lower()

@pytest.mark.integration
@pytest.mark.slow
class TestGoogleScholarSearch:
    """Tests for the Google Scholar search functionality."""
    
    @patch('web_scraper.utils.sanitize_search_term')
    @patch('web_scraper.captcha.detect_captcha')
    @patch('web_scraper.utils.check_for_site_blocking')
    @patch('web_scraper.utils.handle_cookie_consent')
    def test_search_google_scholar_mock(self, mock_handle_cookie, mock_check_blocking, 
                                        mock_detect_captcha, mock_sanitize):
        """Test Google Scholar search with mocked browser interactions."""
        # Mock sanitize_search_term
        mock_sanitize.return_value = "machine learning"
        
        # Mock detect_captcha to return no CAPTCHA
        mock_detect_captcha.return_value = (False, None)
        
        # Mock check_for_site_blocking to return False
        mock_check_blocking.return_value = False
        
        # Mock handle_cookie_consent
        mock_handle_cookie.return_value = True
        
        # Create a mock browser
        mock_browser = MagicMock()
        
        # Mock the page source to contain search results
        mock_browser.page_source = """
        <html>
            <body>
                <div class="gs_r gs_or gs_scl">
                    <h3 class="gs_rt"><a href="https://example.com/paper1">Machine Learning Paper 1</a></h3>
                    <div class="gs_a">Author One, Author Two - Journal of ML, 2022</div>
                    <div class="gs_rs">This is a snippet about machine learning research.</div>
                </div>
                <div class="gs_r gs_or gs_scl">
                    <h3 class="gs_rt"><a href="https://example.com/paper2">Machine Learning Paper 2</a></h3>
                    <div class="gs_a">Author Three, Author Four - Conference on AI, 2021</div>
                    <div class="gs_rs">Another snippet about machine learning applications.</div>
                </div>
            </body>
        </html>
        """
        
        # Mock find_elements to return result elements
        mock_result_elements = [MagicMock(), MagicMock()]
        mock_browser.find_elements.return_value = mock_result_elements
        
        # Mock find_element for title, authors, etc.
        mock_title_element = MagicMock()
        mock_title_element.text = "Machine Learning Paper"
        mock_title_element.get_attribute.return_value = "https://example.com/paper"
        
        mock_authors_element = MagicMock()
        mock_authors_element.text = "Author One, Author Two - Journal, 2022"
        
        mock_snippet_element = MagicMock()
        mock_snippet_element.text = "This is a snippet about machine learning."
        
        # Set up the mock elements to be found
        mock_result_elements[0].find_element.side_effect = lambda by, value: {
            "h3": mock_title_element,
            "gs_a": mock_authors_element,
            "gs_rs": mock_snippet_element
        }.get(value, MagicMock())
        
        # Call the search function
        results = search_google_scholar(mock_browser, "machine learning")
        
        # Check that the results are as expected
        assert len(results) > 0
        assert "title" in results[0]
        assert "authors" in results[0]
        assert "year" in results[0]
        assert "link" in results[0]
        assert "snippet" in results[0]
        assert "source" in results[0]
        assert results[0]["source"] == "Google Scholar"

@pytest.mark.integration
@pytest.mark.slow
class TestResearchGateSearch:
    """Tests for the ResearchGate search functionality."""
    
    @patch('web_scraper.utils.sanitize_search_term')
    @patch('web_scraper.captcha.detect_captcha')
    @patch('web_scraper.utils.check_for_site_blocking')
    @patch('web_scraper.utils.handle_cookie_consent')
    def test_search_research_gate_mock(self, mock_handle_cookie, mock_check_blocking, 
                                      mock_detect_captcha, mock_sanitize):
        """Test ResearchGate search with mocked browser interactions."""
        # Mock sanitize_search_term
        mock_sanitize.return_value = "quantum computing"
        
        # Mock detect_captcha to return no CAPTCHA
        mock_detect_captcha.return_value = (False, None)
        
        # Mock check_for_site_blocking to return False
        mock_check_blocking.return_value = False
        
        # Mock handle_cookie_consent
        mock_handle_cookie.return_value = True
        
        # Create a mock browser
        mock_browser = MagicMock()
        
        # Mock the page source to contain search results
        mock_browser.page_source = """
        <html>
            <body>
                <div class="research-item">
                    <h3><a href="https://example.com/paper1">Quantum Computing Paper 1</a></h3>
                    <div class="authors">Author One, Author Two</div>
                    <div class="publication-info">Journal of QC, 2022</div>
                    <div class="abstract">This is an abstract about quantum computing research.</div>
                </div>
                <div class="research-item">
                    <h3><a href="https://example.com/paper2">Quantum Computing Paper 2</a></h3>
                    <div class="authors">Author Three, Author Four</div>
                    <div class="publication-info">Conference on QC, 2021</div>
                    <div class="abstract">Another abstract about quantum computing applications.</div>
                </div>
            </body>
        </html>
        """
        
        # Mock find_elements to return result elements
        mock_result_elements = [MagicMock(), MagicMock()]
        mock_browser.find_elements.return_value = mock_result_elements
        
        # Mock find_element for title, authors, etc.
        mock_title_element = MagicMock()
        mock_title_element.text = "Quantum Computing Paper"
        mock_title_element.get_attribute.return_value = "https://example.com/paper"
        
        mock_authors_element = MagicMock()
        mock_authors_element.text = "Author One, Author Two"
        
        mock_year_element = MagicMock()
        mock_year_element.text = "Journal of QC, 2022"
        
        mock_abstract_element = MagicMock()
        mock_abstract_element.text = "This is an abstract about quantum computing."
        
        # Set up the mock elements to be found
        mock_result_elements[0].find_element.side_effect = lambda by, value: {
            "h3": mock_title_element,
            "authors": mock_authors_element,
            "publication-info": mock_year_element,
            "abstract": mock_abstract_element
        }.get(value, MagicMock())
        
        # Call the search function
        results = search_research_gate(mock_browser, "quantum computing")
        
        # Check that the results are as expected
        assert len(results) > 0
        assert "title" in results[0]
        assert "authors" in results[0]
        assert "year" in results[0]
        assert "link" in results[0]
        assert "snippet" in results[0]
        assert "source" in results[0]
        assert results[0]["source"] == "ResearchGate"

@pytest.mark.integration
@pytest.mark.slow
class TestSearchEngineErrors:
    """Tests for error handling in search engines."""
    
    @patch('web_scraper.utils.sanitize_search_term')
    @patch('web_scraper.captcha.detect_captcha')
    def test_google_scholar_captcha_handling(self, mock_detect_captcha, mock_sanitize):
        """Test handling of CAPTCHA in Google Scholar search."""
        # Mock sanitize_search_term
        mock_sanitize.return_value = "machine learning"
        
        # Mock detect_captcha to return CAPTCHA detected
        mock_detect_captcha.return_value = (True, "recaptcha")
        
        # Create a mock browser
        mock_browser = MagicMock()
        
        # Call the search function
        results = search_google_scholar(mock_browser, "machine learning")
        
        # Check that the results are empty due to CAPTCHA
        assert len(results) == 0
    
    @patch('web_scraper.utils.sanitize_search_term')
    @patch('web_scraper.utils.check_for_site_blocking')
    def test_research_gate_site_blocking(self, mock_check_blocking, mock_sanitize):
        """Test handling of site blocking in ResearchGate search."""
        # Mock sanitize_search_term
        mock_sanitize.return_value = "quantum computing"
        
        # Mock check_for_site_blocking to return True (site is blocking)
        mock_check_blocking.return_value = True
        
        # Create a mock browser
        mock_browser = MagicMock()
        
        # Call the search function
        results = search_research_gate(mock_browser, "quantum computing")
        
        # Check that the results are empty due to site blocking
        assert len(results) == 0 