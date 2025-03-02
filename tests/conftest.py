#!/usr/bin/env python3
"""
Pytest configuration and fixtures.
"""

import pytest
from unittest.mock import MagicMock
import logging
import os
import tempfile
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@pytest.fixture
def mock_browser():
    """
    Fixture that provides a mock browser instance.
    """
    browser = MagicMock()
    browser.page_source = "<html><body>Mock page content</body></html>"
    browser.current_url = "https://example.com/search"
    browser.title = "Mock Browser Title"
    
    # Mock common browser methods
    browser.get.return_value = None
    browser.find_element.return_value = MagicMock()
    browser.find_elements.return_value = []
    browser.execute_script.return_value = None
    browser.save_screenshot.return_value = True
    
    return browser

@pytest.fixture
def mock_settings():
    """
    Fixture that provides mock settings.
    """
    return {
        "engines": ["google_scholar", "research_gate"],
        "max_results": 10,
        "headless": True,
        "timeout": 30,
        "pdf_download": False,
        "save_to_file": False,
        "output_file": None,
        "browser_type": "chrome",
        "browser_count": 1,
        "captcha_settings": {
            "enable_detection": True,
            "enable_auto_solve": False,
            "wait_time": 120,
            "screenshot_dir": "captcha_screenshots"
        }
    }

@pytest.fixture
def mock_pdf_content():
    """
    Fixture that provides mock PDF content.
    """
    return b"%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>>>>>/Parent 2 0 R>>\nendobj\n4 0 obj\n<</Length 44>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Mock PDF Content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\n0000000111 00000 n\n0000000254 00000 n\ntrailer\n<</Size 5/Root 1 0 R>>\nstartxref\n345\n%%EOF"

@pytest.fixture
def mock_search_results():
    """
    Fixture that provides mock search results.
    """
    return [
        {
            "title": "Mock Research Paper 1",
            "authors": ["Author One", "Author Two"],
            "year": "2022",
            "link": "https://example.com/paper1",
            "snippet": "This is a mock snippet for the first paper about machine learning.",
            "source": "Google Scholar"
        },
        {
            "title": "Mock Research Paper 2",
            "authors": ["Author Three", "Author Four"],
            "year": "2021",
            "link": "https://example.com/paper2",
            "snippet": "This is a mock snippet for the second paper about artificial intelligence.",
            "source": "ResearchGate"
        },
        {
            "title": "Mock Research Paper 3",
            "authors": ["Author Five", "Author Six"],
            "year": "2020",
            "link": "https://example.com/paper3",
            "snippet": "This is a mock snippet for the third paper about deep learning.",
            "source": "Google Scholar"
        }
    ]

@pytest.fixture
def temp_config_file():
    """
    Fixture that provides a temporary configuration file.
    """
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        # Create sample settings
        settings = {
            "engines": ["google_scholar"],
            "max_results": 5,
            "headless": True,
            "timeout": 30,
            "pdf_download": False
        }
        
        # Write settings to the file
        json.dump(settings, temp_file)
        temp_path = temp_file.name
    
    # Return the path to the temporary file
    yield temp_path
    
    # Clean up the temporary file
    if os.path.exists(temp_path):
        os.remove(temp_path)

@pytest.fixture
def temp_output_file():
    """
    Fixture that provides a temporary output file.
    """
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        temp_path = temp_file.name
    
    # Return the path to the temporary file
    yield temp_path
    
    # Clean up the temporary file
    if os.path.exists(temp_path):
        os.remove(temp_path) 