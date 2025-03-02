#!/usr/bin/env python3
"""
Unit tests for the main module.
"""

import pytest
from unittest.mock import MagicMock, patch
import logging

from web_scraper import search_academic_databases, generate_mock_results

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestGenerateMockResults:
    """Tests for the generate_mock_results function."""
    
    def test_generate_mock_results_basic(self):
        """Test basic mock results generation."""
        results = generate_mock_results("machine learning", count=3)
        
        # Check that we got the right number of results
        assert len(results) == 3
        
        # Check that each result has the required fields
        for result in results:
            assert "title" in result
            assert "authors" in result
            assert "year" in result
            assert "link" in result
            assert "snippet" in result
            assert "source" in result
            
            # Check that the search term is included in the title or snippet
            assert "machine learning" in result["title"].lower() or "machine learning" in result["snippet"].lower()
    
    def test_generate_mock_results_count(self):
        """Test mock results with different counts."""
        # Test with count=0
        results = generate_mock_results("test", count=0)
        assert len(results) == 0
        
        # Test with count=1
        results = generate_mock_results("test", count=1)
        assert len(results) == 1
        
        # Test with count=10
        results = generate_mock_results("test", count=10)
        assert len(results) == 10
    
    def test_generate_mock_results_source(self):
        """Test mock results with specific source."""
        results = generate_mock_results("test", count=5, source="Custom Source")
        
        # Check that all results have the specified source
        for result in results:
            assert result["source"] == "Custom Source"

@pytest.mark.slow
class TestSearchAcademicDatabases:
    """Tests for the search_academic_databases function."""
    
    @patch('web_scraper.browser.setup_browser')
    @patch('web_scraper.search_engines.get_search_engine_function')
    @patch('web_scraper.browser.close_browser')
    def test_search_academic_databases_basic(self, mock_close_browser, mock_get_engine, mock_setup_browser, mock_settings):
        """Test basic search functionality."""
        # Mock browser setup
        mock_browser = MagicMock()
        mock_setup_browser.return_value = mock_browser
        
        # Mock search engine function
        mock_search_func = MagicMock()
        mock_search_func.return_value = [
            {
                "title": "Test Paper 1",
                "authors": ["Author 1", "Author 2"],
                "year": "2022",
                "link": "https://example.com/paper1",
                "snippet": "This is a test snippet.",
                "source": "Google Scholar"
            }
        ]
        mock_get_engine.return_value = mock_search_func
        
        # Call the function
        results = search_academic_databases("test query", mock_settings)
        
        # Verify the results
        assert len(results) == 1
        assert results[0]["title"] == "Test Paper 1"
        
        # Verify that the browser was set up and closed
        mock_setup_browser.assert_called_once()
        mock_close_browser.assert_called_once_with(mock_browser)
        
        # Verify that the search engine function was called
        mock_get_engine.assert_called()
        mock_search_func.assert_called()
    
    @patch('web_scraper.browser.setup_browser')
    @patch('web_scraper.search_engines.get_search_engine_function')
    @patch('web_scraper.browser.close_browser')
    def test_search_academic_databases_multiple_engines(self, mock_close_browser, mock_get_engine, mock_setup_browser, mock_settings):
        """Test search with multiple engines."""
        # Mock browser setup
        mock_browser = MagicMock()
        mock_setup_browser.return_value = mock_browser
        
        # Mock search engine functions
        mock_google_func = MagicMock()
        mock_google_func.return_value = [
            {
                "title": "Google Paper 1",
                "authors": ["Author 1", "Author 2"],
                "year": "2022",
                "link": "https://example.com/google1",
                "snippet": "This is a Google Scholar snippet.",
                "source": "Google Scholar"
            }
        ]
        
        mock_research_func = MagicMock()
        mock_research_func.return_value = [
            {
                "title": "ResearchGate Paper 1",
                "authors": ["Author 3", "Author 4"],
                "year": "2021",
                "link": "https://example.com/research1",
                "snippet": "This is a ResearchGate snippet.",
                "source": "ResearchGate"
            }
        ]
        
        # Set up the mock to return different functions based on the engine name
        mock_get_engine.side_effect = lambda engine: {
            "google_scholar": mock_google_func,
            "research_gate": mock_research_func
        }.get(engine)
        
        # Call the function
        results = search_academic_databases("test query", mock_settings)
        
        # Verify the results
        assert len(results) == 2
        assert results[0]["source"] == "Google Scholar"
        assert results[1]["source"] == "ResearchGate"
        
        # Verify that the search engine functions were called
        assert mock_get_engine.call_count == 2
        mock_google_func.assert_called_once()
        mock_research_func.assert_called_once()
    
    @patch('web_scraper.browser.setup_browser')
    @patch('web_scraper.search_engines.get_search_engine_function')
    @patch('web_scraper.browser.close_browser')
    def test_search_academic_databases_error_handling(self, mock_close_browser, mock_get_engine, mock_setup_browser, mock_settings):
        """Test error handling during search."""
        # Mock browser setup
        mock_browser = MagicMock()
        mock_setup_browser.return_value = mock_browser
        
        # Mock search engine function that raises an exception
        mock_search_func = MagicMock()
        mock_search_func.side_effect = Exception("Search error")
        mock_get_engine.return_value = mock_search_func
        
        # Call the function
        results = search_academic_databases("test query", mock_settings)
        
        # Verify that we got empty results due to the error
        assert len(results) == 0
        
        # Verify that the browser was still closed despite the error
        mock_close_browser.assert_called_once_with(mock_browser) 