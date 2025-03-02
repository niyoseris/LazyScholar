#!/usr/bin/env python3
"""
Migration script to help transition from the monolithic web_scraper.py to the new modular structure.
"""

import os
import sys
import shutil
import logging
import importlib.util
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_old_file_exists():
    """Check if the old web_scraper.py file exists."""
    return os.path.exists("web_scraper.py")

def check_new_package_exists():
    """Check if the new web_scraper package exists."""
    return os.path.exists("web_scraper") and os.path.isdir("web_scraper")

def backup_old_file():
    """Create a backup of the old web_scraper.py file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"web_scraper_{timestamp}.py.bak"
    
    try:
        shutil.copy2("web_scraper.py", backup_filename)
        logger.info(f"Created backup of original file: {backup_filename}")
        return backup_filename
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        return None

def create_deprecation_wrapper():
    """Create a deprecation wrapper for the old web_scraper.py file."""
    backup_filename = backup_old_file()
    if not backup_filename:
        return False
    
    try:
        with open("web_scraper.py", "w") as f:
            f.write("""#!/usr/bin/env python3
\"\"\"
DEPRECATED: This monolithic web_scraper.py file is deprecated.
Please use the new modular web_scraper package instead.

This file now serves as a compatibility wrapper that imports from the new modular package.
\"\"\"

import os
import sys
import warnings
import logging

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Issue deprecation warning
warnings.warn(
    "The monolithic web_scraper.py file is deprecated. "
    "Please use the new modular web_scraper package instead. "
    "See migrate_to_modular.py for migration instructions.",
    DeprecationWarning, 
    stacklevel=2
)

# Check if the new package exists
if not os.path.exists("web_scraper") or not os.path.isdir("web_scraper"):
    logger.error(
        "The new modular web_scraper package is not found. "
        "Please run migrate_to_modular.py to set up the new package structure."
    )
    sys.exit(1)

# Import from the new package
try:
    from web_scraper import search_academic_databases
    
    # Re-export the main functions for backward compatibility
    __all__ = ['search_academic_databases']
    
    logger.info(
        "Successfully imported from the new modular package. "
        "Please update your imports to use the new package directly."
    )
except ImportError as e:
    logger.error(f"Failed to import from the new package: {e}")
    logger.error(
        "Please run migrate_to_modular.py to set up the new package structure."
    )
    sys.exit(1)
""")
        logger.info("Created deprecation wrapper for web_scraper.py")
        return True
    except Exception as e:
        logger.error(f"Failed to create deprecation wrapper: {e}")
        # Restore from backup
        if backup_filename and os.path.exists(backup_filename):
            shutil.copy2(backup_filename, "web_scraper.py")
            logger.info("Restored original file from backup")
        return False

def main():
    """Main migration function."""
    print("\n" + "="*80)
    print("Web Scraper Migration Tool".center(80))
    print("="*80 + "\n")
    
    print("This script will help you migrate from the monolithic web_scraper.py")
    print("to the new modular web_scraper package structure.\n")
    
    # Check if old file exists
    if not check_old_file_exists():
        print("The old web_scraper.py file was not found.")
        print("If you've already migrated or are starting with the new structure, no action is needed.")
        return
    
    # Check if new package exists
    if not check_new_package_exists():
        print("The new web_scraper package structure was not found.")
        print("Please ensure you've set up the new package structure before migrating.")
        return
    
    # Ask for confirmation
    print("\nMigration will perform the following actions:")
    print("1. Create a backup of your original web_scraper.py file")
    print("2. Replace web_scraper.py with a compatibility wrapper that imports from the new package")
    print("\nThis ensures your existing code will continue to work while you transition to the new structure.")
    
    confirm = input("\nDo you want to proceed with the migration? (y/n): ")
    if confirm.lower() != 'y':
        print("Migration cancelled.")
        return
    
    # Create deprecation wrapper
    if create_deprecation_wrapper():
        print("\nMigration completed successfully!")
        print("\nYour original file has been backed up, and web_scraper.py is now a compatibility wrapper.")
        print("You can now update your imports to use the new modular package directly:")
        print("\nOld import:")
        print("    from web_scraper import search_academic_databases")
        print("\nNew import:")
        print("    from web_scraper import search_academic_databases")
        print("\nThe imports look the same, but now they're using the modular package structure.")
        print("This wrapper ensures backward compatibility while you transition your codebase.")
    else:
        print("\nMigration failed. Please check the logs for details.")

if __name__ == "__main__":
    main() 