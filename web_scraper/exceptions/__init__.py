"""
Exceptions Module - Custom exceptions for the web scraper package.
"""

class WebScraperException(Exception):
    """Base exception for all web scraper exceptions."""
    pass

class BlockedSiteException(WebScraperException):
    """Exception raised when a site is blocking access."""
    
    def __init__(self, url, message=None):
        self.url = url
        self.message = message or f"Access to {url} is blocked"
        super().__init__(self.message)

class CaptchaDetectedException(WebScraperException):
    """Exception raised when a CAPTCHA is detected."""
    
    def __init__(self, url, captcha_type=None, message=None):
        self.url = url
        self.captcha_type = captcha_type
        self.message = message or f"CAPTCHA detected on {url}"
        if captcha_type:
            self.message += f" (type: {captcha_type})"
        super().__init__(self.message)

class CaptchaSolveTimeoutException(WebScraperException):
    """Exception raised when CAPTCHA solving times out."""
    
    def __init__(self, url, timeout, message=None):
        self.url = url
        self.timeout = timeout
        self.message = message or f"CAPTCHA solving timed out after {timeout} seconds on {url}"
        super().__init__(self.message)

class BrowserSetupException(WebScraperException):
    """Exception raised when browser setup fails."""
    
    def __init__(self, browser_type, message=None):
        self.browser_type = browser_type
        self.message = message or f"Failed to set up {browser_type} browser"
        super().__init__(self.message)

class PDFDownloadException(WebScraperException):
    """Exception raised when PDF download fails."""
    
    def __init__(self, url, status_code=None, message=None):
        self.url = url
        self.status_code = status_code
        self.message = message or f"Failed to download PDF from {url}"
        if status_code:
            self.message += f" (status code: {status_code})"
        super().__init__(self.message)

class PDFExtractionException(WebScraperException):
    """Exception raised when text extraction from PDF fails."""
    
    def __init__(self, pdf_path, message=None):
        self.pdf_path = pdf_path
        self.message = message or f"Failed to extract text from PDF: {pdf_path}"
        super().__init__(self.message)

class SearchEngineNotSupportedException(WebScraperException):
    """Exception raised when an unsupported search engine is requested."""
    
    def __init__(self, engine_name, message=None):
        self.engine_name = engine_name
        self.message = message or f"Search engine '{engine_name}' is not supported"
        super().__init__(self.message)

class NoResultsFoundException(WebScraperException):
    """Exception raised when no results are found for a search query."""
    
    def __init__(self, search_term, engine=None, message=None):
        self.search_term = search_term
        self.engine = engine
        self.message = message or f"No results found for '{search_term}'"
        if engine:
            self.message += f" on {engine}"
        super().__init__(self.message)
