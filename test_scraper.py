#!/usr/bin/env python3
"""
Test script for Trendlyne scraper
"""

import sys
import subprocess

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        from playwright.sync_api import sync_playwright
        print("✅ playwright imported successfully")
    except ImportError as e:
        print(f"❌ playwright import failed: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✅ beautifulsoup4 imported successfully")
    except ImportError as e:
        print(f"❌ beautifulsoup4 import failed: {e}")
        return False
    
    return True

def install_playwright_browsers():
    """Install Playwright browsers"""
    print("\nInstalling Playwright browsers...")
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        print("✅ Playwright browsers installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Playwright browsers: {e}")
        return False

def main():
    print("Trendlyne Scraper - Installation Test")
    print("=" * 40)
    
    if not test_imports():
        print("\n❌ Some imports failed. Please install requirements:")
        print("pip install -r requirements.txt")
        return False
    
    if not install_playwright_browsers():
        print("\n❌ Failed to install Playwright browsers")
        return False
    
    print("\n✅ All tests passed! The scraper should work now.")
    print("\nTo run the scraper:")
    print("python trendlyne_scraper.py")
    
    return True

if __name__ == "__main__":
    main()