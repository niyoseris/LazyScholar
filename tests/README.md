# Web Scraper Tests

This directory contains tests for the web scraper package.

## Test Structure

- `unit/`: Unit tests for individual modules
- `integration/`: Integration tests for module interactions
- `conftest.py`: Pytest fixtures and configuration

## Running Tests

### Running All Tests

```bash
pytest
```

### Running Unit Tests Only

```bash
pytest tests/unit
```

### Running Integration Tests Only

```bash
pytest tests/integration
```

### Running Tests with Coverage

```bash
pytest --cov=web_scraper
```

### Running Tests by Marker

```bash
# Run browser tests
pytest -m browser

# Run CAPTCHA tests
pytest -m captcha

# Run PDF tests
pytest -m pdf

# Run slow tests
pytest -m slow
```

## Test Markers

The following markers are available:

- `unit`: Unit tests
- `integration`: Integration tests
- `slow`: Tests that may take longer to run
- `browser`: Tests that involve browser functionality
- `captcha`: Tests that involve CAPTCHA handling
- `pdf`: Tests that involve PDF processing

## Writing Tests

When writing new tests, please follow these guidelines:

1. Use appropriate markers to categorize your tests
2. Use fixtures from `conftest.py` when possible
3. Mock external dependencies
4. Keep unit tests focused on a single function or class
5. Use descriptive test names that explain what is being tested
6. Add docstrings to test classes and methods

## Test Dependencies

The tests require the following dependencies:

- pytest
- pytest-cov
- unittest.mock (part of the Python standard library)

These dependencies are included in the `requirements.txt` file. 