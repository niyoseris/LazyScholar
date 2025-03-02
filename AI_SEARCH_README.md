# AI-Powered Web Search Tool

This repository contains a standalone Python script for searching any website using Selenium automation. The script is designed to be flexible and work with a variety of websites, automatically detecting search inputs and extracting results.

## Features

- Search any website with a search functionality
- Support for both Chrome and Firefox browsers
- Automatic detection of search input fields and buttons
- Extraction of search results including titles, links, authors, and snippets
- Screenshot capability for debugging
- Configurable timeouts and wait times
- JSON output option for saving results

## Requirements

- Python 3.7+
- Selenium
- WebDriver Manager
- Chrome or Firefox browser installed

## Installation

1. Clone this repository or download the script:

```bash
git clone https://github.com/yourusername/ai-search-tool.git
cd ai-search-tool
```

2. Create a virtual environment and install the required packages:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install selenium webdriver-manager
```

## Usage

The script can be run from the command line with various options:

```bash
python simple_ai_search.py "your search query" https://website-to-search.com [options]
```

### Command Line Options

- `query`: The search query (required, first positional argument)
- `website`: The website URL to search, including https:// (required, second positional argument)
- `--max-results`: Maximum number of results to retrieve (default: 3)
- `--headless`: Run browser in headless mode (flag, no value needed)
- `--output`: Output file path for saving results as JSON
- `--browser`: Browser to use, either "chrome" or "firefox" (default: chrome)
- `--timeout`: Timeout in seconds for page loading (default: 30)
- `--wait`: Wait time in seconds after page loads (default: 3)
- `--screenshot`: Save screenshots to the specified file path

### Examples

Basic search on Google Scholar:
```bash
python simple_ai_search.py "artificial intelligence" https://scholar.google.com
```

Search with Firefox and save results to JSON:
```bash
python simple_ai_search.py "machine learning" https://www.sciencedirect.com --browser firefox --output results.json
```

Search with screenshots for debugging:
```bash
python simple_ai_search.py "climate change" https://www.nature.com --screenshot debug.png
```

## How It Works

1. The script sets up a browser instance (Chrome or Firefox)
2. It navigates to the specified website
3. It automatically detects the search input field and enters the query
4. It finds and clicks the search button or presses Enter
5. It waits for the results page to load
6. It extracts search results using common selectors
7. It displays the results and optionally saves them to a JSON file

## Troubleshooting

If the script fails to find search elements or extract results:

1. Try increasing the wait time: `--wait 5`
2. Use the screenshot option to see what the browser is seeing: `--screenshot debug.png`
3. Try a different browser: `--browser firefox`
4. Check if the website has anti-bot measures that might be blocking automated access

## Limitations

- Some websites have anti-bot measures that may block automated access
- Complex search interfaces might not be properly detected
- JavaScript-heavy websites might require additional wait times
- CAPTCHAs will prevent the script from working properly

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Selenium WebDriver for browser automation
- WebDriver Manager for simplifying driver installation 