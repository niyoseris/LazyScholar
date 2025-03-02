#!/usr/bin/env python3
"""
Unit tests for the CLI module.
"""

import pytest
import argparse
import json
import logging
import sys
import io
from unittest.mock import MagicMock, patch, mock_open

from web_scraper.cli import (
    parse_args, 
    setup_logging, 
    save_results, 
    display_results, 
    main
)

class TestParseArgs:
    """Tests for the parse_args function."""
    
    def test_parse_args_basic(self):
        """Test basic argument parsing."""
        # Mock sys.argv
        with patch('sys.argv', ['web_scraper', 'test query']):
            args = parse_args()
            
            # Check that the arguments were parsed correctly
            assert args.query == 'test query'
            assert args.engines == ['google_scholar']
            assert args.max_results == 10
            assert args.headless is False
            assert args.timeout == 60
            assert args.pdf_download is False
            assert args.output is None
            assert args.mock is False
            assert args.verbose is False
    
    def test_parse_args_with_options(self):
        """Test argument parsing with various options."""
        # Mock sys.argv with various options
        with patch('sys.argv', [
            'web_scraper',
            'advanced query',
            '--engines', 'google_scholar', 'research_gate',
            '--max-results', '5',
            '--headless',
            '--timeout', '30',
            '--pdf-download',
            '--output', 'results.json',
            '--mock',
            '--verbose'
        ]):
            args = parse_args()
            
            # Check that the arguments were parsed correctly
            assert args.query == 'advanced query'
            assert args.engines == ['google_scholar', 'research_gate']
            assert args.max_results == 5
            assert args.headless is True
            assert args.timeout == 30
            assert args.pdf_download is True
            assert args.output == 'results.json'
            assert args.mock is True
            assert args.verbose is True
    
    def test_parse_args_invalid_engine(self):
        """Test argument parsing with an invalid engine."""
        # Mock sys.argv with an invalid engine
        with patch('sys.argv', ['web_scraper', 'query', '--engines', 'invalid_engine']):
            # Should raise SystemExit because argparse will detect the invalid choice
            with pytest.raises(SystemExit):
                parse_args()

class TestSetupLogging:
    """Tests for the setup_logging function."""
    
    @patch('logging.getLogger')
    def test_setup_logging_verbose(self, mock_get_logger):
        """Test setting up logging in verbose mode."""
        # Mock root logger
        mock_root_logger = MagicMock()
        mock_get_logger.return_value = mock_root_logger
        
        # Call setup_logging with verbose=True
        setup_logging(True)
        
        # Check that the log level was set to DEBUG
        mock_root_logger.setLevel.assert_called_with(logging.DEBUG)
        
        # Check that a handler was added
        mock_root_logger.addHandler.assert_called()
    
    @patch('logging.getLogger')
    def test_setup_logging_non_verbose(self, mock_get_logger):
        """Test setting up logging in non-verbose mode."""
        # Mock root logger
        mock_root_logger = MagicMock()
        mock_get_logger.return_value = mock_root_logger
        
        # Call setup_logging with verbose=False
        setup_logging(False)
        
        # Check that the log level was set to INFO
        mock_root_logger.setLevel.assert_called_with(logging.INFO)
        
        # Check that a handler was added
        mock_root_logger.addHandler.assert_called()

class TestSaveResults:
    """Tests for the save_results function."""
    
    def test_save_results(self):
        """Test saving results to a file."""
        # Mock results
        results = [
            {
                "title": "Test Paper 1",
                "authors": ["Author 1", "Author 2"],
                "year": "2022",
                "link": "https://example.com/paper1",
                "snippet": "This is a test snippet.",
                "source": "Google Scholar"
            },
            {
                "title": "Test Paper 2",
                "authors": ["Author 3", "Author 4"],
                "year": "2021",
                "link": "https://example.com/paper2",
                "snippet": "This is another test snippet.",
                "source": "ResearchGate"
            }
        ]
        
        # Mock open function
        mock_file = mock_open()
        
        # Call save_results with the mock open
        with patch('builtins.open', mock_file):
            save_results(results, 'test_output.json')
        
        # Check that the file was opened correctly
        mock_file.assert_called_once_with('test_output.json', 'w', encoding='utf-8')
        
        # Check that json.dump was called with the results
        # We can't directly check the call to json.dump since it's inside the context manager,
        # but we can check that write was called on the file handle
        handle = mock_file()
        handle.write.assert_called()
    
    @patch('logging.getLogger')
    def test_save_results_error(self, mock_get_logger):
        """Test error handling when saving results."""
        # Mock logger
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Mock results
        results = [{"title": "Test Paper"}]
        
        # Mock open function to raise an exception
        with patch('builtins.open', side_effect=Exception("Test error")):
            save_results(results, 'test_output.json')
        
        # Check that the error was logged
        mock_logger.error.assert_called()

class TestDisplayResults:
    """Tests for the display_results function."""
    
    def test_display_results(self):
        """Test displaying results."""
        # Mock results
        results = [
            {
                "title": "Test Paper 1",
                "authors": ["Author 1", "Author 2"],
                "year": "2022",
                "link": "https://example.com/paper1",
                "snippet": "This is a test snippet.",
                "source": "Google Scholar"
            },
            {
                "title": "Test Paper 2",
                "authors": ["Author 3", "Author 4"],
                "year": "2021",
                "link": "https://example.com/paper2",
                "snippet": "This is another test snippet.",
                "source": "ResearchGate"
            }
        ]
        
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            # Call display_results
            display_results(results)
            
            # Get the captured output
            output = captured_output.getvalue()
            
            # Check that the output contains the expected information
            assert "Found 2 results" in output
            assert "Test Paper 1" in output
            assert "Author 1, Author 2" in output
            assert "2022" in output
            assert "Google Scholar" in output
            assert "https://example.com/paper1" in output
            assert "This is a test snippet" in output
            assert "Test Paper 2" in output
            assert "Author 3, Author 4" in output
            assert "2021" in output
            assert "ResearchGate" in output
            assert "https://example.com/paper2" in output
        finally:
            # Reset stdout
            sys.stdout = sys.__stdout__
    
    def test_display_empty_results(self):
        """Test displaying empty results."""
        # Mock empty results
        results = []
        
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            # Call display_results
            display_results(results)
            
            # Get the captured output
            output = captured_output.getvalue()
            
            # Check that the output contains the expected message
            assert "No results found" in output
        finally:
            # Reset stdout
            sys.stdout = sys.__stdout__

class TestMain:
    """Tests for the main function."""
    
    @patch('web_scraper.cli.parse_args')
    @patch('web_scraper.cli.setup_logging')
    @patch('web_scraper.cli.get_default_settings')
    @patch('web_scraper.cli.update_settings')
    @patch('web_scraper.cli.generate_mock_results')
    @patch('web_scraper.cli.search_academic_databases')
    @patch('web_scraper.cli.display_results')
    @patch('web_scraper.cli.save_results')
    def test_main_with_mock(self, mock_save, mock_display, mock_search, mock_generate, 
                           mock_update, mock_get_default, mock_setup_logging, mock_parse_args):
        """Test main function with mock results."""
        # Mock args
        mock_args = MagicMock()
        mock_args.query = "test query"
        mock_args.engines = ["google_scholar"]
        mock_args.max_results = 5
        mock_args.headless = True
        mock_args.timeout = 30
        mock_args.pdf_download = False
        mock_args.output = "test_output.json"
        mock_args.mock = True
        mock_args.verbose = False
        mock_parse_args.return_value = mock_args
        
        # Mock settings
        mock_settings = {
            "engines": ["google_scholar"],
            "max_results": 5,
            "headless": True,
            "timeout": 30,
            "pdf_download": False,
            "save_to_file": True
        }
        mock_get_default.return_value = {}
        mock_update.return_value = mock_settings
        
        # Mock results
        mock_results = [{"title": "Test Paper"}]
        mock_generate.return_value = mock_results
        
        # Call main
        result = main()
        
        # Check that the function returned success
        assert result == 0
        
        # Check that the mock functions were called correctly
        mock_parse_args.assert_called_once()
        mock_setup_logging.assert_called_once_with(False)
        mock_get_default.assert_called_once()
        mock_update.assert_called_once()
        mock_generate.assert_called_once_with("test query", count=5)
        mock_search.assert_not_called()  # Should not be called when mock=True
        mock_display.assert_called_once_with(mock_results)
        mock_save.assert_called_once_with(mock_results, "test_output.json")
    
    @patch('web_scraper.cli.parse_args')
    @patch('web_scraper.cli.setup_logging')
    @patch('web_scraper.cli.get_default_settings')
    @patch('web_scraper.cli.update_settings')
    @patch('web_scraper.cli.generate_mock_results')
    @patch('web_scraper.cli.search_academic_databases')
    @patch('web_scraper.cli.display_results')
    @patch('web_scraper.cli.save_results')
    def test_main_with_real_search(self, mock_save, mock_display, mock_search, mock_generate, 
                                  mock_update, mock_get_default, mock_setup_logging, mock_parse_args):
        """Test main function with real search."""
        # Mock args
        mock_args = MagicMock()
        mock_args.query = "test query"
        mock_args.engines = ["google_scholar", "research_gate"]
        mock_args.max_results = 10
        mock_args.headless = False
        mock_args.timeout = 60
        mock_args.pdf_download = True
        mock_args.output = None
        mock_args.mock = False
        mock_args.verbose = True
        mock_parse_args.return_value = mock_args
        
        # Mock settings
        mock_settings = {
            "engines": ["google_scholar", "research_gate"],
            "max_results": 10,
            "headless": False,
            "timeout": 60,
            "pdf_download": True,
            "save_to_file": False
        }
        mock_get_default.return_value = {}
        mock_update.return_value = mock_settings
        
        # Mock results
        mock_results = [{"title": "Real Paper"}]
        mock_search.return_value = mock_results
        
        # Call main
        result = main()
        
        # Check that the function returned success
        assert result == 0
        
        # Check that the mock functions were called correctly
        mock_parse_args.assert_called_once()
        mock_setup_logging.assert_called_once_with(True)
        mock_get_default.assert_called_once()
        mock_update.assert_called_once()
        mock_generate.assert_not_called()  # Should not be called when mock=False
        mock_search.assert_called_once_with("test query", mock_settings)
        mock_display.assert_called_once_with(mock_results)
        mock_save.assert_not_called()  # Should not be called when output=None
    
    @patch('web_scraper.cli.parse_args')
    @patch('web_scraper.cli.setup_logging')
    @patch('web_scraper.cli.get_default_settings')
    @patch('web_scraper.cli.update_settings')
    @patch('web_scraper.cli.search_academic_databases')
    def test_main_with_error(self, mock_search, mock_update, mock_get_default, 
                            mock_setup_logging, mock_parse_args):
        """Test main function with an error during search."""
        # Mock args
        mock_args = MagicMock()
        mock_args.query = "test query"
        mock_args.engines = ["google_scholar"]
        mock_args.max_results = 10
        mock_args.headless = True
        mock_args.timeout = 60
        mock_args.pdf_download = False
        mock_args.output = None
        mock_args.mock = False
        mock_args.verbose = True
        mock_parse_args.return_value = mock_args
        
        # Mock settings
        mock_settings = {
            "engines": ["google_scholar"],
            "max_results": 10,
            "headless": True,
            "timeout": 60,
            "pdf_download": False,
            "save_to_file": False
        }
        mock_get_default.return_value = {}
        mock_update.return_value = mock_settings
        
        # Mock search to raise an exception
        mock_search.side_effect = Exception("Test error")
        
        # Call main
        result = main()
        
        # Check that the function returned an error code
        assert result == 1
        
        # Check that the mock functions were called correctly
        mock_parse_args.assert_called_once()
        mock_setup_logging.assert_called_once_with(True)
        mock_get_default.assert_called_once()
        mock_update.assert_called_once()
        mock_search.assert_called_once_with("test query", mock_settings) 