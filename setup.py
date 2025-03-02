#!/usr/bin/env python3
"""
Setup script for the web_scraper package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="web_scraper",
    version="0.1.0",
    author="Academic Web Scraper Team",
    author_email="example@example.com",
    description="A modular web scraper for academic research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/web_scraper",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.7",
    install_requires=[
        "selenium>=4.0.0",
        "webdriver-manager>=3.5.0",
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "PyPDF2>=2.0.0",
        "pdfplumber>=0.7.0",
        "tqdm>=4.60.0",
        "fake-useragent>=0.1.11",
    ],
    entry_points={
        "console_scripts": [
            "web-scraper=web_scraper.cli:main",
        ],
    },
) 