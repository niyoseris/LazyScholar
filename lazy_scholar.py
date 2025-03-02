#!/usr/bin/env python3
"""
LazyScholar - Academic Research Assistant

This application helps users conduct academic research by:
1. Analyzing a problem statement to generate topics and subtopics
2. Searching academic sources for relevant information
3. Extracting information from PDF files
4. Compiling research into a structured academic paper with proper citations
"""

import os
import sys
import json
import time
import logging
import argparse
import tempfile
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import base64
import platform
import requests

# Import required libraries
try:
    import google.generativeai as genai
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from dotenv import load_dotenv
    from PIL import Image
    import PyPDF2
    import pdfplumber
except ImportError as e:
    print(f"Error: Required package not found: {e}")
    print("Please install required packages with: pip install -r requirements.txt")
    sys.exit(1)

# Add the current directory to the Python path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import from web_scraper module
try:
    from web_scraper.browser.browser_factory import create_browser
    from web_scraper.browser import close_browser
    from web_scraper.ai_engines.vision_helper import take_screenshot, find_search_input, find_search_button, analyze_screenshot
    from web_scraper.utils.file_utils import ensure_directory
except ImportError as e:
    print(f"Error importing web_scraper modules: {e}")
    print("Make sure the web_scraper package is properly installed.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("lazy_scholar.log")
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY not found in environment variables. Please set it in .env file.")
    sys.exit(1)

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

def ensure_directory(directory_path: str) -> str:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        The directory path
    """
    os.makedirs(directory_path, exist_ok=True)
    return directory_path

class LazyScholar:
    """Main class for the LazyScholar application."""
    
    def __init__(self, headless: bool = False, output_dir: str = "research_output", timeout: int = 120, search_suffix: str = ""):
        """
        Initialize the LazyScholar application.
        
        Args:
            headless: Whether to run the browser in headless mode
            output_dir: Directory to save research output
            timeout: Timeout in seconds for browser operations
            search_suffix: Suffix to append to every search query (e.g., 'filetype:pdf')
        """
        self.headless = headless
        self.output_dir = ensure_directory(output_dir)
        self.timeout = timeout
        self.search_suffix = search_suffix
        self.browser = None
        self.problem_statement = None
        self.topics = []
        self.research_data = {}
        
        # Initialize the Gemini model
        self.text_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.vision_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        logger.info("LazyScholar initialized")
    
    def start_browser(self):
        """Start the browser session."""
        if self.browser is None:
            logger.info("Starting browser session")
            # Try Chrome first
            self.browser = create_browser(browser_type="chrome", headless=self.headless)
            # If Chrome fails, try Firefox
            if self.browser is None:
                logger.info("Chrome browser failed, trying Firefox")
                self.browser = create_browser(browser_type="firefox", headless=self.headless)
                # If Firefox fails, try Safari (on macOS)
                if self.browser is None and platform.system() == "Darwin":
                    logger.info("Firefox browser failed, trying Safari")
                    self.browser = create_browser(browser_type="safari", headless=self.headless)
    
    def close_browser(self):
        """Close the browser session."""
        if self.browser is not None:
            logger.info("Closing browser session")
            close_browser(self.browser)
            self.browser = None
    
    def analyze_problem_statement(self, problem_statement: str) -> List[Dict[str, Any]]:
        """
        Analyze the problem statement to generate topics and subtopics.
        
        Args:
            problem_statement: The research problem statement
            
        Returns:
            List of topics with subtopics
        """
        logger.info(f"Analyzing problem statement: {problem_statement}")
        self.problem_statement = problem_statement
        
        # Generate topics and subtopics using Gemini
        prompt = f"""
        As a research assistant, analyze this problem statement and suggest 3-5 main topics 
        and 2-3 subtopics for each main topic. Format your response as a JSON array of objects.
        
        Problem statement: {problem_statement}
        
        IMPORTANT GUIDELINES:
        1. Each topic and subtopic MUST be directly related to the problem statement
        2. Avoid generic topics that could apply to any field (like "Socio-economic impacts" without context)
        3. Always include key terms from the problem statement in each topic
        4. Make topics specific enough that they would yield relevant search results
        5. Ensure each topic represents a distinct aspect of the problem statement
        
        Response format:
        [
            {{
                "topic": "Main Topic 1 (must include key terms from problem statement)",
                "subtopics": ["Specific Subtopic 1.1", "Specific Subtopic 1.2", "Specific Subtopic 1.3"]
            }},
            ...
        ]
        """
        
        try:
            response = self.text_model.generate_content(prompt)
            topics_text = response.text
            
            # Extract JSON from the response
            import re
            json_match = re.search(r'```json\n(.*?)\n```', topics_text, re.DOTALL)
            if json_match:
                topics_json = json_match.group(1)
            else:
                topics_json = topics_text
            
            # Clean up the JSON string
            topics_json = topics_json.replace('```json', '').replace('```', '').strip()
            
            # Parse the JSON
            topics = json.loads(topics_json)
            
            # Validate that topics contain key terms from the problem statement
            key_terms = [term.lower() for term in problem_statement.split() 
                        if len(term) > 3 and term.lower() not in ['and', 'the', 'for', 'with', 'that', 'this']]
            
            validated_topics = []
            for topic_data in topics:
                topic = topic_data["topic"]
                
                # Check if the topic contains at least one key term
                has_key_term = any(term in topic.lower() for term in key_terms)
                
                if has_key_term:
                    validated_topics.append(topic_data)
                else:
                    # If topic doesn't contain key terms, add them
                    modified_topic = f"{topic} in {problem_statement}"
                    topic_data["topic"] = modified_topic
                    validated_topics.append(topic_data)
            
            self.topics = validated_topics
            
            logger.info(f"Generated {len(validated_topics)} topics")
            return validated_topics
            
        except Exception as e:
            logger.error(f"Error analyzing problem statement: {e}")
            return []
    
    def search_topic(self, topic: str, search_engine: str = "https://scholar.google.com") -> List[Dict[str, Any]]:
        """
        Search for a topic on the specified search engine.
        
        Args:
            topic: The topic to search for
            search_engine: URL of the search engine to use
            
        Returns:
            List of search results
        """
        # Create a search query that includes the main problem context
        # This ensures that generic topics remain connected to the main research question
        if self.problem_statement and topic not in self.problem_statement:
            # Extract key terms from the problem statement (avoid common words)
            problem_terms = [term.lower() for term in self.problem_statement.split() 
                            if len(term) > 3 and term.lower() not in ['and', 'the', 'for', 'with', 'that', 'this']]
            
            # Add 1-2 key terms from the problem statement to maintain context
            context_terms = []
            for term in problem_terms:
                if term not in topic.lower():
                    context_terms.append(term)
                    if len(context_terms) >= 2:  # Limit to 2 additional terms
                        break
            
            # Build the search query with context
            if context_terms:
                search_query = f"{topic} {' '.join(context_terms)} {self.search_suffix}".strip()
            else:
                search_query = f"{topic} {self.search_suffix}".strip()
        else:
            # If the topic already contains the problem context, just use it directly
            search_query = f"{topic} {self.search_suffix}".strip()
            
        logger.info(f"Searching for topic: {search_query} on {search_engine}")
        
        try:
            # Start the browser if not already started
            self.start_browser()
            
            # Navigate to the search engine
            self.browser.get(search_engine)
            time.sleep(min(3, self.timeout / 10))  # Wait for page to load, but not more than 1/10 of timeout
            
            # Take a screenshot for vision analysis
            screenshot_path = take_screenshot(self.browser, f"search_{topic.replace(' ', '_')}")
            
            # Use vision model to find search input
            search_input = find_search_input(self.browser)
            if search_input:
                # Enter search query
                search_input.clear()
                search_input.send_keys(search_query)
                search_input.send_keys(Keys.RETURN)
                time.sleep(min(5, self.timeout / 5))  # Wait for search results, but not more than 1/5 of timeout
                
                # Take screenshot of results
                results_screenshot = take_screenshot(self.browser, f"results_{topic.replace(' ', '_')}")
                
                # Extract results using vision model
                results = self.extract_search_results(self.browser)
                logger.info(f"Found {len(results)} results for topic: {topic}")
                return results
            else:
                logger.error(f"Could not find search input on {search_engine}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching for topic: {e}")
            return []
    
    def extract_search_results(self, browser: webdriver.Chrome) -> List[Dict[str, str]]:
        """
        Extract search results from the current page.
        
        Args:
            browser: Selenium WebDriver instance
            
        Returns:
            List of dictionaries with search result information
        """
        try:
            # Take a screenshot for vision analysis
            screenshot_path = take_screenshot(browser, "search_results")
            
            # Create a prompt for the vision model
            prompt = """
            Analyze this screenshot of search results from Google Scholar. 
            Extract the following details for each research paper or article:
            1. Title
            2. Authors (if available)
            3. Publication year (if available)
            4. URL or DOI (if available)
            5. Brief description or abstract snippet (if available)
            
            Format the results as a JSON array of objects, with each object containing the fields: 
            title, authors, year, url, and description.
            If no results are visible or if there's a CAPTCHA challenge, indicate that in your response.
            """
            
            # Analyze the screenshot
            vision_result = analyze_screenshot(screenshot_path, prompt)
            
            # Process the results
            results = []
            
            # Check if we have results in the vision response
            if vision_result.get("found", False):
                # Check if results are already in list format
                if "results" in vision_result and isinstance(vision_result["results"], list):
                    results = vision_result["results"]
                # Check if the entire response is a list
                elif isinstance(vision_result, list):
                    results = vision_result
                # If we have raw text but no structured results, create a basic result
                elif "raw_text" in vision_result:
                    results = [{"title": "Result from vision analysis", "description": vision_result["raw_text"]}]
            
            # If no results were found from vision analysis, try to extract links from the page
            if not results:
                logger.info("No results from vision analysis, trying to extract links from page")
                try:
                    # Find all links that might be paper titles
                    links = browser.find_elements(By.CSS_SELECTOR, "h3 a, .gs_rt a")
                    
                    # If no specific paper links found, try any links
                    if not links:
                        links = browser.find_elements(By.TAG_NAME, "a")
                    
                    # Filter out navigation links and other non-paper links
                    for link in links:
                        href = link.get_attribute("href")
                        text = link.text
                        
                        # Skip empty links or navigation links
                        if not href or not text or len(text) < 10:
                            continue
                            
                        # Skip links that are clearly not papers
                        if any(x in href.lower() for x in ["google.com/search", "settings", "preferences", "account"]):
                            continue
                            
                        results.append({
                            "title": text,
                            "url": href,
                            "description": "Link extracted from page"
                        })
                except Exception as e:
                    logger.error(f"Error extracting links from page: {e}")
            
            # Ensure we have at least one result
            if not results:
                results = [{"title": "No results found", "description": "Could not extract search results"}]
                
            logger.info(f"Found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error extracting search results: {e}")
            return [{"title": "Error extracting results", "description": str(e)}]
    
    def download_pdf(self, url: str) -> Optional[str]:
        """
        Download a PDF from a URL.
        
        Args:
            url: URL to download from
            
        Returns:
            Path to the downloaded PDF or None if download failed
        """
        if not url:
            logger.warning("No URL provided for PDF download")
            return None
            
        # Ensure URL has a protocol
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url
            
        logger.info(f"Attempting to download PDF from: {url}")
        
        try:
            # Navigate to the URL
            self.browser.get(url)
            time.sleep(min(2, self.timeout / 15))  # Wait for page to load
            
            # If the URL is already a PDF, download it directly
            if url.lower().endswith('.pdf'):
                return self._save_pdf(url)
                
            # Take a screenshot for vision analysis
            screenshot_path = take_screenshot(self.browser, "pdf_page")
            
            # Create a prompt for the vision model
            prompt = """
            Analyze this webpage screenshot and find links to PDF files. 
            Look for download buttons, PDF icons, or links containing "PDF", "Download", "Full text", etc.
            If you find any, provide the following information:
            1. Text of the link or button
            2. Approximate position on the page (coordinates or description)
            3. Whether it appears to be a direct PDF link
            
            Format your response as a JSON object with fields: found (boolean), 
            pdf_links (array of objects with text, position, and is_direct_pdf fields).
            """
            
            # Analyze the screenshot
            vision_result = analyze_screenshot(screenshot_path, prompt)
            
            # Check if we found PDF links through vision analysis
            if vision_result.get("found", False) and "pdf_links" in vision_result:
                pdf_links = vision_result.get("pdf_links", [])
                
                for pdf_link in pdf_links:
                    try:
                        # Try to find and click the PDF link
                        if "text" in pdf_link and pdf_link["text"]:
                            # Try to find by text
                            elements = self.browser.find_elements(By.XPATH, 
                                f"//*[contains(text(), '{pdf_link['text']}') or contains(@title, '{pdf_link['text']}')]")
                            
                            for element in elements:
                                if element.is_displayed():
                                    logger.info(f"Clicking PDF link with text: {pdf_link['text']}")
                                    element.click()
                                    time.sleep(min(3, self.timeout / 10))  # Wait for navigation
                                    
                                    # Check if we're now on a PDF page
                                    current_url = self.browser.current_url
                                    if current_url.lower().endswith('.pdf'):
                                        return self._save_pdf(current_url)
                    except Exception as e:
                        logger.error(f"Error clicking PDF link from vision analysis: {e}")
            
            # If vision approach didn't work, try traditional approach
            logger.info("Trying traditional approach to find PDF links")
            
            # Try to find PDF links on the page
            pdf_links = self.browser.find_elements(By.XPATH, 
                "//a[contains(@href, '.pdf') or contains(text(), 'PDF') or contains(text(), 'Download') or contains(@title, 'PDF')]")
            
            for link in pdf_links:
                try:
                    if link.is_displayed():
                        href = link.get_attribute('href')
                        logger.info(f"Found potential PDF link: {href}")
                        
                        # If it's a direct PDF link, download it
                        if href and href.lower().endswith('.pdf'):
                            return self._save_pdf(href)
                            
                        # Otherwise, click the link and check if it leads to a PDF
                        link.click()
                        time.sleep(min(3, self.timeout / 10))  # Wait for navigation
                        
                        current_url = self.browser.current_url
                        if current_url.lower().endswith('.pdf'):
                            return self._save_pdf(current_url)
                except Exception as e:
                    logger.error(f"Error processing PDF link: {e}")
            
            logger.warning("No PDF links found on the page")
            return None
            
        except Exception as e:
            logger.error(f"Error downloading PDF: {e}")
            return None
            
    def _save_pdf(self, pdf_url: str) -> Optional[str]:
        """
        Save a PDF from a URL to a file.
        
        Args:
            pdf_url: URL of the PDF
            
        Returns:
            Path to the saved PDF or None if save failed
        """
        try:
            # Ensure URL has a protocol
            if not pdf_url.startswith('http://') and not pdf_url.startswith('https://'):
                pdf_url = 'https://' + pdf_url
                
            # Create output directory if it doesn't exist
            pdf_dir = ensure_directory(os.path.join(self.output_dir, "pdfs"))
            
            # Generate a filename based on the URL
            filename = os.path.join(pdf_dir, f"paper_{int(time.time())}.pdf")
            
            # Download the PDF
            logger.info(f"Downloading PDF from: {pdf_url}")
            response = requests.get(pdf_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Check if the content is actually a PDF
            content_type = response.headers.get('Content-Type', '')
            if 'application/pdf' not in content_type and not pdf_url.lower().endswith('.pdf'):
                logger.warning(f"URL does not point to a PDF: {content_type}")
                return None
                
            # Save the PDF
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            logger.info(f"PDF saved to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving PDF: {e}")
            return None
    
    def extract_pdf_content(self, pdf_path: str, topic: str, subtopic: str) -> Dict[str, Any]:
        """
        Extract relevant content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            topic: The main topic
            subtopic: The subtopic
            
        Returns:
            Dictionary with extracted content
        """
        logger.info(f"Extracting content from PDF: {pdf_path}")
        
        try:
            # Extract text from PDF
            text = ""
            with open(pdf_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
            
            # Use Gemini to extract relevant information
            prompt = f"""
            Analyze this academic paper text and extract information relevant to the problem statement: "{self.problem_statement}",
            focusing on the topic: "{topic}" and subtopic: "{subtopic}".
            
            Extract the following:
            1. Key findings related to the topic/subtopic
            2. Methodologies used
            3. Important data or statistics
            4. Conclusions relevant to the topic
            5. Citation information (authors, title, journal, year, etc.)
            
            IMPORTANT: Only extract information that is directly relevant to the problem statement "{self.problem_statement}".
            If the paper does not contain information relevant to the problem statement, indicate this clearly.
            
            Format your response as a JSON object.
            
            Text from the paper:
            {text[:10000]}  # Limit text length to avoid token limits
            """
            
            response = self.text_model.generate_content(prompt)
            
            # Extract JSON from the response
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response.text, re.DOTALL)
            if json_match:
                content_json = json_match.group(1)
            else:
                content_json = response.text
            
            # Clean up the JSON string
            content_json = content_json.replace('```json', '').replace('```', '').strip()
            
            # Parse the JSON
            try:
                content = json.loads(content_json)
                
                # Check if the content indicates no relevant information was found
                key_findings = content.get("key_findings", "").lower()
                if "not relevant" in key_findings or "no relevant" in key_findings or "not contain" in key_findings:
                    logger.warning(f"PDF does not contain information relevant to the problem statement")
                    return {
                        "key_findings": f"This paper does not contain information directly relevant to {self.problem_statement}.",
                        "methodologies": [],
                        "data": [],
                        "conclusions": "No relevant conclusions found.",
                        "citation": content.get("citation", {})
                    }
                
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON from text model response")
                content = {
                    "key_findings": "Error extracting content",
                    "methodologies": [],
                    "data": [],
                    "conclusions": [],
                    "citation": {}
                }
            
            return content
            
        except Exception as e:
            logger.error(f"Error extracting PDF content: {e}")
            return {
                "key_findings": f"Error: {str(e)}",
                "methodologies": [],
                "data": [],
                "conclusions": [],
                "citation": {}
            }
    
    def write_subtopic_file(self, topic: str, subtopic: str, content: Dict[str, Any]) -> str:
        """
        Write subtopic research to a file.
        
        Args:
            topic: The main topic
            subtopic: The subtopic
            content: The research content
            
        Returns:
            Path to the written file
        """
        logger.info(f"Writing subtopic file for {topic} - {subtopic}")
        
        try:
            # Create directory for topic
            topic_dir = ensure_directory(os.path.join(self.output_dir, topic.replace(" ", "_")))
            
            # Create filename for subtopic
            filename = os.path.join(topic_dir, f"{subtopic.replace(' ', '_')}.md")
            
            # Generate markdown content
            markdown = f"""# {subtopic}
*Part of research on: {topic}*

## Key Findings
{content.get('key_findings', 'No key findings extracted')}

## Methodologies
{', '.join(content.get('methodologies', ['No methodologies extracted']))}

## Important Data
{', '.join(content.get('data', ['No data extracted']))}

## Conclusions
{content.get('conclusions', 'No conclusions extracted')}

## Citation
{content.get('citation', {}).get('authors', 'Unknown authors')}, 
"{content.get('citation', {}).get('title', 'Unknown title')}", 
{content.get('citation', {}).get('journal', 'Unknown journal')}, 
{content.get('citation', {}).get('year', 'Unknown year')}
"""
            
            # Write to file
            with open(filename, "w", encoding="utf-8") as f:
                f.write(markdown)
            
            logger.info(f"Wrote subtopic file: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error writing subtopic file: {e}")
            return ""
    
    def generate_final_paper(self) -> str:
        """
        Generate the final research paper.
        
        Returns:
            Path to the final paper file
        """
        logger.info("Generating final research paper")
        
        try:
            # Collect all subtopic files
            all_content = {}
            for topic in self.topics:
                topic_name = topic["topic"]
                topic_dir = os.path.join(self.output_dir, topic_name.replace(" ", "_"))
                
                if os.path.exists(topic_dir):
                    subtopic_files = [f for f in os.listdir(topic_dir) if f.endswith('.md')]
                    
                    subtopic_content = []
                    for subtopic_file in subtopic_files:
                        with open(os.path.join(topic_dir, subtopic_file), "r", encoding="utf-8") as f:
                            subtopic_content.append(f.read())
                    
                    all_content[topic_name] = subtopic_content
            
            # If no content was found, generate a paper based on the topics alone
            if not all_content:
                logger.warning("No research content found. Generating paper based on topics alone.")
                
                # Create a structured representation of the topics
                topics_json = []
                for topic in self.topics:
                    topic_obj = {
                        "topic_title": topic["topic"],
                        "subtopics": []
                    }
                    
                    for subtopic in topic["subtopics"]:
                        subtopic_obj = {
                            "subtopic_title": subtopic,
                            "content": f"Research on {subtopic} related to {topic['topic']}."
                        }
                        topic_obj["subtopics"].append(subtopic_obj)
                    
                    topics_json.append(topic_obj)
                
                # Generate final paper using Gemini with just the topics
                prompt = f"""
                Generate a comprehensive academic research paper on the following topic:
                
                Problem statement: {self.problem_statement}
                
                Topics to cover:
                {json.dumps(topics_json, indent=2)}
                
                The paper should include:
                1. Title
                2. Abstract
                3. Introduction (including the problem statement)
                4. Literature Review
                5. Methodology
                6. Results and Discussion (organized by topics and subtopics)
                7. Conclusion
                8. References (in proper academic format)
                
                Format the paper in Markdown. Use your knowledge to provide substantive content for each section.
                """
            else:
                # Generate final paper using Gemini with the collected content
                prompt = f"""
                Generate a comprehensive academic research paper based on the following research topics and content.
                
                Problem statement: {self.problem_statement}
                
                Research content:
                {json.dumps(all_content, indent=2)}
                
                The paper should include:
                1. Title
                2. Abstract
                3. Introduction (including the problem statement)
                4. Literature Review
                5. Methodology
                6. Results and Discussion (organized by topics and subtopics)
                7. Conclusion
                8. References (in proper academic format)
                
                Format the paper in Markdown.
                """
            
            response = self.text_model.generate_content(prompt)
            paper_content = response.text
            
            # Write to file
            final_paper_path = os.path.join(self.output_dir, "final_paper.md")
            with open(final_paper_path, "w", encoding="utf-8") as f:
                f.write(paper_content)
            
            logger.info(f"Generated final paper: {final_paper_path}")
            return final_paper_path
            
        except Exception as e:
            logger.error(f"Error generating final paper: {e}")
            return ""
    
    def conduct_research(self, problem_statement: str, search_engine: str = "https://scholar.google.com") -> str:
        """
        Conduct a complete research process.
        
        Args:
            problem_statement: The research problem statement
            search_engine: URL of the search engine to use
            
        Returns:
            Path to the final research paper
        """
        try:
            # Step 1: Analyze problem statement
            topics = self.analyze_problem_statement(problem_statement)
            if not topics:
                logger.error("Failed to generate topics from problem statement")
                return ""
            
            # Step 2: Research each topic and subtopic
            for topic_data in topics:
                topic = topic_data["topic"]
                subtopics = topic_data["subtopics"]
                
                logger.info(f"Researching topic: {topic}")
                
                # Search for the main topic
                search_results = self.search_topic(topic, search_engine)
                
                # Process up to 10 PDFs for each topic
                pdf_count = 0
                for result in search_results:
                    if pdf_count >= 10:
                        break
                    
                    url = result.get("url", "")
                    if url:
                        pdf_path = self.download_pdf(url)
                        if pdf_path:
                            # For each PDF, extract content relevant to each subtopic
                            for subtopic in subtopics:
                                content = self.extract_pdf_content(pdf_path, topic, subtopic)
                                self.write_subtopic_file(topic, subtopic, content)
                            
                            pdf_count += 1
                
                # If no PDFs found for the topic, generate content based on model's knowledge
                if pdf_count == 0:
                    logger.warning(f"No PDFs found for topic: {topic}. Generating content based on model's knowledge.")
                    for subtopic in subtopics:
                        self.generate_subtopic_content(topic, subtopic)
            
            # Step 3: Generate final paper
            final_paper_path = self.generate_final_paper()
            
            return final_paper_path
            
        except Exception as e:
            logger.error(f"Error conducting research: {e}")
            return ""
        finally:
            # Close browser
            self.close_browser()
            
    def generate_subtopic_content(self, topic: str, subtopic: str) -> None:
        """
        Generate content for a subtopic based on the model's knowledge when no PDFs are found.
        
        Args:
            topic: The main topic
            subtopic: The subtopic
        """
        logger.info(f"Generating content for {topic} - {subtopic} based on model's knowledge")
        
        try:
            # Use Gemini to generate content based on its knowledge
            prompt = f"""
            As an academic research assistant, provide information on the topic "{topic}" 
            with a focus on the subtopic "{subtopic}" in the context of the problem statement: "{self.problem_statement}".
            
            Generate the following:
            1. Key findings related to this topic/subtopic from academic literature
            2. Common methodologies used in this field
            3. Important data or statistics relevant to this area
            4. Major conclusions from existing research
            5. Citation information for 2-3 important papers in this field (authors, title, journal, year)
            
            IMPORTANT: Ensure all content is directly related to the problem statement "{self.problem_statement}".
            Do not provide generic information about {topic} or {subtopic} that is not connected to {self.problem_statement}.
            
            Format your response as a JSON object with the following structure:
            {{
                "key_findings": "Detailed paragraph about key findings",
                "methodologies": ["Method 1", "Method 2", "Method 3"],
                "data": ["Data point 1", "Data point 2", "Data point 3"],
                "conclusions": "Detailed paragraph about conclusions",
                "citation": {{
                    "authors": "Author names",
                    "title": "Paper title",
                    "journal": "Journal name",
                    "year": "Publication year"
                }}
            }}
            """
            
            response = self.text_model.generate_content(prompt)
            
            # Extract JSON from the response
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response.text, re.DOTALL)
            if json_match:
                content_json = json_match.group(1)
            else:
                content_json = response.text
            
            # Clean up the JSON string
            content_json = content_json.replace('```json', '').replace('```', '').strip()
            
            # Parse the JSON
            try:
                content = json.loads(content_json)
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON from text model response")
                content = {
                    "key_findings": f"Information on {subtopic} related to {topic} in the context of {self.problem_statement}.",
                    "methodologies": ["Literature review", "Data analysis"],
                    "data": ["Various statistics from the field"],
                    "conclusions": f"Important conclusions about {subtopic} in the context of {topic} and {self.problem_statement}.",
                    "citation": {
                        "authors": "Various authors",
                        "title": f"Research on {subtopic} in {self.problem_statement}",
                        "journal": "Academic journals",
                        "year": "Recent years"
                    }
                }
            
            # Write the generated content to a file
            self.write_subtopic_file(topic, subtopic, content)
            
        except Exception as e:
            logger.error(f"Error generating subtopic content: {e}")
            # Create minimal content in case of error
            content = {
                "key_findings": f"Error generating content: {str(e)}",
                "methodologies": ["Literature review"],
                "data": ["No data available"],
                "conclusions": "No conclusions available",
                "citation": {
                    "authors": "N/A",
                    "title": f"Research on {subtopic} in {self.problem_statement}",
                    "journal": "N/A",
                    "year": "N/A"
                }
            }
            self.write_subtopic_file(topic, subtopic, content)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="LazyScholar - Academic Research Assistant")
    parser.add_argument("problem_statement", help="The research problem statement")
    parser.add_argument("--search-engine", default="https://scholar.google.com", 
                        help="URL of the search engine to use (default: https://scholar.google.com)")
    parser.add_argument("--headless", action="store_true", 
                        help="Run browser in headless mode")
    parser.add_argument("--output-dir", default="research_output", 
                        help="Directory to save research output (default: research_output)")
    parser.add_argument("--timeout", type=int, default=120,
                        help="Timeout in seconds for browser operations (default: 120)")
    parser.add_argument("--suffix", default="", 
                        help="Suffix to append to every search query (e.g., 'filetype:pdf')")
    
    return parser.parse_args()

def main():
    """Main function to run the LazyScholar application."""
    args = parse_arguments()
    
    print("\n" + "="*80)
    print("LazyScholar - Academic Research Assistant".center(80))
    print("="*80)
    
    print(f"\nProblem statement: {args.problem_statement}")
    print(f"Search engine: {args.search_engine}")
    print(f"Output directory: {args.output_dir}")
    print(f"Headless mode: {args.headless}")
    print(f"Timeout: {args.timeout} seconds")
    if args.suffix:
        print(f"Search suffix: {args.suffix}")
    
    # Create LazyScholar instance
    scholar = LazyScholar(
        headless=args.headless, 
        output_dir=args.output_dir, 
        timeout=args.timeout,
        search_suffix=args.suffix
    )
    
    # Conduct research
    print("\nStarting research process...")
    final_paper_path = scholar.conduct_research(args.problem_statement, args.search_engine)
    
    if final_paper_path:
        print(f"\nResearch completed successfully!")
        print(f"Final paper saved to: {final_paper_path}")
    else:
        print("\nResearch process failed. Check logs for details.")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main() 