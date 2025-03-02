#!/usr/bin/env python3
"""
Unit tests for the configuration module.
"""

import pytest
from unittest.mock import MagicMock, patch
import os
import json
import tempfile

from web_scraper.config import get_default_settings, update_settings, load_settings, save_settings

class TestDefaultSettings:
    """Tests for the default settings functionality."""
    
    def test_get_default_settings(self):
        """Test getting default settings."""
        settings = get_default_settings()
        
        # Check that the default settings contain the expected keys
        assert "engines" in settings
        assert "max_results" in settings
        assert "headless" in settings
        assert "timeout" in settings
        assert "pdf_download" in settings
        
        # Check some default values
        assert "google_scholar" in settings["engines"]
        assert settings["max_results"] > 0
        assert isinstance(settings["headless"], bool)
        assert settings["timeout"] > 0
        assert isinstance(settings["pdf_download"], bool)

class TestUpdateSettings:
    """Tests for the settings update functionality."""
    
    def test_update_settings_basic(self):
        """Test basic settings update."""
        # Get default settings
        default_settings = get_default_settings()
        
        # Update with new values
        custom_settings = {
            "engines": ["research_gate"],
            "max_results": 5,
            "headless": not default_settings["headless"]
        }
        
        updated_settings = update_settings(default_settings, custom_settings)
        
        # Check that the settings were updated
        assert updated_settings["engines"] == ["research_gate"]
        assert updated_settings["max_results"] == 5
        assert updated_settings["headless"] != default_settings["headless"]
        
        # Check that other settings remain unchanged
        assert updated_settings["timeout"] == default_settings["timeout"]
        assert updated_settings["pdf_download"] == default_settings["pdf_download"]
    
    def test_update_settings_nested(self):
        """Test updating nested settings."""
        # Get default settings
        default_settings = get_default_settings()
        
        # Ensure there's a nested setting to update
        if "captcha_settings" not in default_settings:
            default_settings["captcha_settings"] = {
                "enable_detection": True,
                "wait_time": 120
            }
        
        # Update with new nested values
        custom_settings = {
            "captcha_settings": {
                "wait_time": 60,
                "screenshot_dir": "custom_screenshots"
            }
        }
        
        updated_settings = update_settings(default_settings, custom_settings)
        
        # Check that the nested settings were updated
        assert updated_settings["captcha_settings"]["wait_time"] == 60
        assert updated_settings["captcha_settings"]["screenshot_dir"] == "custom_screenshots"
        
        # Check that other nested settings remain unchanged
        assert updated_settings["captcha_settings"]["enable_detection"] == default_settings["captcha_settings"]["enable_detection"]
    
    def test_update_settings_new_keys(self):
        """Test adding new keys to settings."""
        # Get default settings
        default_settings = get_default_settings()
        
        # Update with new keys
        custom_settings = {
            "new_setting_1": "value1",
            "new_setting_2": 42
        }
        
        updated_settings = update_settings(default_settings, custom_settings)
        
        # Check that the new keys were added
        assert "new_setting_1" in updated_settings
        assert updated_settings["new_setting_1"] == "value1"
        assert "new_setting_2" in updated_settings
        assert updated_settings["new_setting_2"] == 42

class TestSettingsIO:
    """Tests for settings I/O functionality."""
    
    def test_save_and_load_settings(self):
        """Test saving and loading settings."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            temp_path = temp_file.name
        
        try:
            # Get default settings
            settings = get_default_settings()
            
            # Add a unique value to identify these settings
            settings["test_identifier"] = "test_save_load"
            
            # Save the settings
            save_settings(settings, temp_path)
            
            # Load the settings
            loaded_settings = load_settings(temp_path)
            
            # Check that the loaded settings match the saved settings
            assert loaded_settings["test_identifier"] == "test_save_load"
            assert loaded_settings["engines"] == settings["engines"]
            assert loaded_settings["max_results"] == settings["max_results"]
            assert loaded_settings["headless"] == settings["headless"]
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_load_settings_file_not_found(self):
        """Test loading settings when the file doesn't exist."""
        # Generate a path that doesn't exist
        non_existent_path = "non_existent_settings.json"
        
        # Ensure the file doesn't exist
        if os.path.exists(non_existent_path):
            os.remove(non_existent_path)
        
        # Load settings from the non-existent file
        # Should return default settings
        loaded_settings = load_settings(non_existent_path)
        
        # Check that we got default settings
        default_settings = get_default_settings()
        assert loaded_settings["engines"] == default_settings["engines"]
        assert loaded_settings["max_results"] == default_settings["max_results"]
    
    def test_load_settings_invalid_json(self):
        """Test loading settings from an invalid JSON file."""
        # Create a temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            temp_file.write(b"This is not valid JSON")
            temp_path = temp_file.name
        
        try:
            # Load settings from the invalid file
            # Should return default settings
            loaded_settings = load_settings(temp_path)
            
            # Check that we got default settings
            default_settings = get_default_settings()
            assert loaded_settings["engines"] == default_settings["engines"]
            assert loaded_settings["max_results"] == default_settings["max_results"]
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path) 