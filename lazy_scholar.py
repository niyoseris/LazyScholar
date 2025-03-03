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
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
import base64
import platform
import requests
import io
import re
from urllib.parse import urljoin
import hashlib
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from io import BytesIO

# Import required libraries
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import PyPDF2
import pdfplumber
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from PIL import Image
import urllib.parse
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Add the current directory to the Python path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import from web_scraper module
try:
    from web_scraper.browser.browser_factory import create_browser
    from web_scraper.browser import close_browser
    from web_scraper.ai_engines.vision_helper import take_screenshot, find_search_input, find_search_button, analyze_screenshot, analyze_screenshot_for_pdf_links, find_pdf_links
    from web_scraper.utils.file_utils import ensure_directory
except ImportError as e:
    print(f"Error importing web_scraper modules: {e}")
    print("Make sure the web_scraper package is properly installed.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("lazy_scholar.log"),
        logging.StreamHandler()
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
    
    def __init__(self, headless: bool = False, output_dir: str = "research_output", timeout: int = 120, search_suffix: str = "", max_pdfs_per_topic: int = 10, focus: str = "all", academic_format: bool = False):
        """
        Initialize the LazyScholar instance.
        
        Args:
            headless (bool): Whether to run the browser in headless mode
            output_dir (str): Directory to store research output
            timeout (int): Timeout in seconds for browser operations
            search_suffix (str): Suffix to append to search queries
            max_pdfs_per_topic (int): Maximum number of PDFs to process per topic
            focus (str): Type of content to focus on ('pdf', 'html', or 'all')
            academic_format (bool): Whether to format the final paper as an academic paper
        """
        # Import required modules
        import google.generativeai as genai
        from dotenv import load_dotenv
        import os
        import json
        
        self.headless = headless
        self.output_dir = output_dir
        self.timeout = timeout
        self.search_suffix = search_suffix
        self.max_pdfs_per_topic = max_pdfs_per_topic
        self.focus = focus
        self.academic_format = academic_format
        self.browser = None
        self.topics = []
        self.problem_statement = ""
        self.driver = None
        
        # Create output directories
        ensure_directory(output_dir)
        ensure_directory(os.path.join(output_dir, "topics"))
        ensure_directory(os.path.join(output_dir, "pdfs"))
        
        # Load environment variables
        load_dotenv()
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        if not GOOGLE_API_KEY:
            logger.error("GOOGLE_API_KEY not found in environment variables. Please set it in .env file.")
            raise ValueError("GOOGLE_API_KEY not found")
        
        # Configure Google Generative AI
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Initialize the models
        try:
            # Set up generation config
            generation_config = {
                "temperature": 0.2,  # Lower temperature for more consistent output
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
            
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
            
            # Initialize the model for general use
            self.model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-001",
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            logger.info(f"Successfully initialized Gemini model with name: gemini-2.0-flash-001")
            
            # Initialize the vision model
            self.vision_model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-001",
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            logger.info(f"Successfully initialized Vision model with name: gemini-2.0-flash-001")
            
            # Initialize the model for final paper generation
            self.gemini = genai.GenerativeModel(
                model_name="gemini-2.0-flash-001",
                generation_config=generation_config
            )
            
            logger.info("Gemini models initialized successfully")
            logger.info("LazyScholar initialized")
        except Exception as e:
            logger.error(f"Error initializing Gemini models: {str(e)}")
            raise
    
    def _api_call_with_retry(self, api_func, max_retries=3, retry_delay=1):
        """
        Make an API call with retry logic.
        
        Args:
            api_func: Function to call the API
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
            
        Returns:
            API response
        """
        retries = 0
        while retries < max_retries:
            try:
                return api_func()
            except Exception as e:
                retries += 1
                if retries >= max_retries:
                    raise
                logger.warning(f"API call failed: {str(e)}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
    
    def start_browser(self) -> None:
        """Initialize and start the web browser."""
        logger.info("Starting browser...")
        
        try:
            # Set up Chrome options
            chrome_options = webdriver.ChromeOptions()
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Add other Chrome options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            
            # Initialize the browser
            self.browser = webdriver.Chrome(options=chrome_options)
            self.browser.set_page_load_timeout(self.timeout)
            
            # Set window size
            self.browser.set_window_size(1920, 1080)
            
            logger.info("Browser started successfully")
        except Exception as e:
            logger.error(f"Failed to start browser: {str(e)}", exc_info=True)
            if "chromedriver" in str(e).lower():
                logger.error("ChromeDriver error. Make sure Chrome is installed and updated.")
            raise
    
    def close_browser(self) -> None:
        """
        Close the browser session and clean up resources.
        """
        if self.driver:
            try:
                logger.info("Closing browser session")
                
                # First try the standard quit method
                try:
                    self.driver.quit()
                except Exception as e:
                    logger.warning(f"Error during standard browser quit: {e}")
                    
                    # If standard quit fails, try to close all windows
                    try:
                        for window_handle in self.driver.window_handles:
                            self.driver.switch_to.window(window_handle)
                            self.driver.close()
                    except Exception as e2:
                        logger.warning(f"Error closing browser windows: {e2}")
                
                # Set browser to None to indicate it's closed
                self.driver = None
                logger.info("Browser session closed successfully")
                
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
                # Force set to None even if there was an error
                self.driver = None
    
    def analyze_problem_statement(self, problem_statement: str) -> List[Dict[str, Any]]:
        """
        Analyze the problem statement to identify research topics and subtopics.
        
        Args:
            problem_statement (str): The research problem to analyze
            
        Returns:
            List[Dict[str, Any]]: List of topics and their subtopics
        """
        logger.info(f"Analyzing problem statement: {problem_statement}")
        
        try:
            # Prepare the prompt for Gemini
            prompt = f"""Analyze this research problem and break it down into main topics and subtopics:

Problem: {problem_statement}

Please identify 2-3 main research topics and 2-3 specific subtopics for each main topic.
Focus on the key aspects that need to be investigated to thoroughly understand this problem.
Subtopics will be used as search keywords by their own. So it's important to make them short and related with the main topic.

Format your response as JSON with this structure:
{{
    "topics": [
        {{
            "title": "Main Topic 1",
            "subtopics": [
                {{
                    "title": "Subtopic 1.1",
                    "status": "pending"
                }},
                ...
            ]
        }},
        ...
    ]
}}"""

            logger.info("Sending prompt to Gemini model...")
            response = self._api_call_with_retry(
                lambda: self.model.generate_content(prompt).text
            )
            
            try:
                # Parse the JSON response
                logger.info("Parsing Gemini response...")
                # Extract JSON from the response (in case there's additional text)
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    data = json.loads(json_str)
                    
                    # Extract topics from the response
                    if "topics" in data:
                        return data["topics"]
                    else:
                        logger.error("Response JSON does not contain 'topics' key")
                        return self._generate_default_topics(problem_statement)
                else:
                    logger.error("Could not find JSON in response")
                    return self._generate_default_topics(problem_statement)
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.error(f"Raw response: {response}")
                return self._generate_default_topics(problem_statement)
                
        except Exception as e:
            logger.error(f"Error analyzing problem statement: {str(e)}", exc_info=True)
            return self._generate_default_topics(problem_statement)
    
    def _generate_default_topics(self, problem_statement: str) -> List[Dict[str, Any]]:
        """
        Generate default topics and subtopics when the Gemini model is not available.
        
        Args:
            problem_statement: The research problem statement
            
        Returns:
            List of dictionaries containing topics and subtopics
        """
        logger.info("Generating default topics for research")
        
        # Extract keywords from the problem statement
        words = problem_statement.lower().split()
        words = [word.strip('.,?!()[]{}:;"\'') for word in words]
        words = [word for word in words if len(word) > 3 and word not in ['and', 'the', 'that', 'this', 'with', 'from', 'what', 'how', 'why', 'between']]
        
        # Use the most frequent words as topics
        from collections import Counter
        word_counts = Counter(words)
        top_words = [word for word, count in word_counts.most_common(3)]
        
        # If we don't have enough words, add some generic topics
        while len(top_words) < 3:
            generic_topics = ["Background", "Current Research", "Future Directions"]
            for topic in generic_topics:
                if topic.lower() not in [word.lower() for word in top_words]:
                    top_words.append(topic)
                    if len(top_words) >= 3:
                        break
        
        # Create topics with proper structure
        topics = []
        for word in top_words[:3]:
            topic = {
                "title": word.title(),
                        "subtopics": [
                    {
                        "title": f"Definition and Basic Concepts of {word.title()}",
                        "status": "pending"
                    },
                    {
                        "title": f"Current Research in {word.title()}",
                        "status": "pending"
                    },
                    {
                        "title": f"Applications and Future Directions of {word.title()}",
                        "status": "pending"
                    }
                ]
            }
            topics.append(topic)
        
        logger.info(f"Generated {len(topics)} default topics for research")
        return topics
    
    def update_topics_tracking_file(self) -> None:
        """
        Create or update the topics_and_subtopics.md tracking file.
        """
        logger.info("Updating topics and subtopics tracking file")
        
        try:
            # Path to the tracking file
            tracking_file = os.path.join(self.output_dir, "topics_and_subtopics.md")
            
            # Count total subtopics
            total_subtopics = sum(len(topic["subtopics"]) for topic in self.topics)
            
            # Get current date
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Generate markdown content
            markdown = f"""# LazyScholar Research Topics and Subtopics

This file tracks the generated topics and subtopics for your academic research project.

## Current Research Status

### Research Topics
"""
            
            # Add topics
            for topic in self.topics:
                markdown += f"- {topic['title']}\n"
            
            markdown += "\n### Subtopics Status\n"
            
            # Add subtopics with checkboxes
            for topic in self.topics:
                markdown += f"\n#### {topic['title']}\n"
                for subtopic in topic["subtopics"]:
                    markdown += f"- [ ] {subtopic}\n"
            
            markdown += f"""
## Research Progress
- Research initiated: {current_date}
- Topics generated: {len(self.topics)}
- Subtopics generated: {total_subtopics}
- Completed subtopics: 0
- In-progress subtopics: 0
- Remaining subtopics: {total_subtopics}

*Note: This file will be updated as research progresses. Checkboxes will be marked when subtopics are completed.*
"""
            
            # Write to file
            with open(tracking_file, "w", encoding="utf-8") as f:
                f.write(markdown)
            
            logger.info(f"Updated topics and subtopics tracking file: {tracking_file}")
            
        except Exception as e:
            logger.error(f"Error updating topics and subtopics tracking file: {e}")
    
    def extract_web_content(self, html_path: str, topic: str, subtopic: str) -> Dict[str, Any]:
        """
        Extract content from a web page relevant to a topic and subtopic.
        
        Args:
            html_path: Path to the HTML file
            topic: The main topic
            subtopic: The subtopic to extract content for
            
        Returns:
            Dictionary with extracted content
        """
        logger.info(f"Extracting web content for {topic} - {subtopic} from {html_path}")
        
        try:
            # Read the HTML file
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Extract text content
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading and trailing space
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Remove blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit text length to avoid token limits
            max_length = 10000  # Adjust as needed
            if len(text) > max_length:
                text = text[:max_length]
            
            # Create a prompt for the model to extract relevant content
            prompt = f"""
            Extract information from the following web page content that is relevant to the topic "{topic}" 
            and specifically the subtopic "{subtopic}".
            
            Organize your response as a JSON object with the following structure:
            {{
                "introduction": ["paragraph 1", "paragraph 2", ...],
                "key_findings": ["finding 1", "finding 2", ...],
                "analysis": ["paragraph 1", "paragraph 2", ...],
                "examples": ["example 1", "example 2", ...],
                "conclusion": ["paragraph 1", "paragraph 2", ...],
                "citation": "Source: [Title of the page]"
            }}
            
            Web page content:
            {text}
            """
            
            # Define the model call with retry
            def _call_gemini():
                response = self.text_model.generate_content(prompt)
                return response.text
            
            # Call the model with retry
            response_text = self._api_call_with_retry(_call_gemini)
            
            # Extract the JSON part from the response
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # If no JSON code block, try to find object directly
                json_match = re.search(r'\{\s*".*"\s*:.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    # If still no match, use the entire response
                    json_str = response_text
            
            # Clean up the JSON string
            json_str = json_str.replace('```json', '').replace('```', '').strip()
            
            # Parse the JSON
            try:
                content = json.loads(json_str)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a default structure
                logger.warning(f"Failed to parse JSON response for {subtopic}. Using default structure.")
                content = self._generate_default_content(topic, subtopic)
                content["raw_response"] = response_text
            
            return content
            
        except Exception as e:
            logger.error(f"Error extracting web content: {e}")
            return self._generate_default_content(topic, subtopic)

    def generate_final_paper(self, topics: List[Dict[str, Any]]) -> str:
        """
        Generate the final research paper by combining all subtopic content.
        
        Args:
            topics: List of topics and their subtopics
            
        Returns:
            str: Path to the generated paper
        """
        try:
            # Create the final paper path
            paper_path = os.path.join(self.output_dir, "final_paper.md")
            
            # Collect all content and references from subtopics
            all_content = {}
            all_references = []
            
            for topic in topics:
                topic_content = []
                
                for subtopic in topic["subtopics"]:
                    # Get the subtopic file path
                    subtopic_file = os.path.join(
                        self.output_dir,
                        "topics",
                        self._sanitize_filename(topic["title"]),
                        f"{self._sanitize_filename(subtopic['title'])}.md"
                    )
                    
                    if os.path.exists(subtopic_file):
                        with open(subtopic_file, "r", encoding="utf-8") as f:
                            content = f.read()
                            
                            # Extract references from the References section
                            references_match = re.search(r'## References\s*\n(.*?)(?:\n\n|\Z)', content, re.DOTALL)
                            if references_match:
                                references = references_match.group(1).strip()
                                # Add to references with topic and subtopic context
                                ref_entry = f"**{topic['title']} - {subtopic['title']}**:\n{references}"
                                all_references.append(ref_entry)
                                
                                # Remove the References section as we'll collect them at the end
                                content = re.sub(r'## References\s*\n.*?(?:\n\n|\Z)', '', content, flags=re.DOTALL)
                            
                            # Also check for old Source section format for backward compatibility
                            source_match = re.search(r'## Source\s*\n(.*?)(?:\n\n|\Z)', content, re.DOTALL)
                            if source_match:
                                sources = source_match.group(1).strip()
                                # Add to references with topic and subtopic context
                                ref_entry = f"**{topic['title']} - {subtopic['title']}**:\n{sources}"
                                all_references.append(ref_entry)
                                
                                # Remove the Source section as we'll collect them at the end
                                content = re.sub(r'## Source\s*\n.*?(?:\n\n|\Z)', '', content, flags=re.DOTALL)
                            
                            # Remove the title and topic line as we'll add our own
                            content = re.sub(r"^#.*\n.*\n", "", content)
                            subtopic_data = {
                                "title": subtopic["title"],
                                "content": content
                            }
                            topic_content.append(subtopic_data)
                
                all_content[topic["title"]] = topic_content
            
            # Generate a structured outline for the LLM
            topics_structure = []
            for topic in topics:
                topic_data = {
                    "title": topic["title"],
                    "subtopics": [subtopic["title"] for subtopic in topic["subtopics"]]
                }
                topics_structure.append(topic_data)
            
            # Generate the final paper content
            prompt = f"""
            Generate a comprehensive research paper on the following topic:
            
            {self.problem_statement}
            
            Using the following structure:
            
            # Research Paper: {self.problem_statement}
            
            ## Abstract
            [Generate a concise abstract summarizing the research]
            
            ## Introduction
            [Generate an introduction to the topic]
            
            ## Main Content
            [For each topic and subtopic, synthesize the provided content into a cohesive narrative]
            
            ## Conclusion
            [Generate a conclusion summarizing the key findings]
            
            ## References
            [Include all references in proper academic format]
            
            Here is the content to synthesize:
            
            {json.dumps(topics_structure)}
            
            And here is the detailed content for each subtopic:
            
            {json.dumps(all_content)}
            """
            
            # Generate the paper using the Gemini model
            response = self._api_call_with_retry(
                lambda: self.model.generate_content(prompt).text
            )
            
            # Add references section
            if "## References" not in response:
                response += "\n\n## References\n"
            
            # If there are no references in the generated content, add them
            if all_references and "## References" in response:
                # Find the references section
                references_section = response.split("## References")[1]
                
                # Check if the references section is empty or minimal
                if len(references_section.strip()) < 50:  # Arbitrary threshold
                    # Replace the references section with our collected references
                    response = response.split("## References")[0]
                    response += "## References\n\n"
                    
                    # Add each reference
                    for ref in all_references:
                        response += f"{ref}\n\n"
                else:
                    # The model generated a good references section, keep it
                    pass
            
            # Write the paper
            with open(paper_path, "w", encoding="utf-8") as f:
                f.write(response)
            
            logger.info(f"Generated final paper at {paper_path}")
            
            # Check if we should format as academic paper
            if hasattr(self, 'academic_format') and self.academic_format:
                logger.info("Formatting final paper as academic paper...")
                try:
                    # Import the academic_formatter module
                    import academic_formatter
                    
                    # Initialize the model
                    model = academic_formatter.initialize_model()
                    if not model:
                        logger.error("Failed to initialize model for academic formatting")
                        return
                    
                    # Extract references and content
                    pdf_references, content = academic_formatter.extract_references_from_final_paper(paper_path)
                    
                    # Format as academic paper
                    formatted_paper = academic_formatter.format_as_academic_paper(model, content, pdf_references)
                    
                    # Save formatted paper
                    output_path = academic_formatter.save_formatted_paper(paper_path, formatted_paper)
                    
                    if output_path:
                        logger.info(f"Successfully formatted final paper as academic paper at {output_path}")
                    else:
                        logger.error("Failed to save formatted academic paper")
                except Exception as e:
                    logger.error(f"Error formatting final paper: {str(e)}")
            
            return paper_path
        except Exception as e:
            logger.error(f"Error generating final paper: {str(e)}")
            raise
    
    def _enhance_references(self, references: List[Dict[str, Any]]) -> List[str]:
        """
        Enhance references with detailed academic citations.
        
        Args:
            references: List of references to enhance
            
        Returns:
            List of enhanced references
        """
        enhanced_references = []
        
        for ref in references:
            topic = ref.get("topic", "")
            subtopic = ref.get("subtopic", "")
            sources = ref.get("sources", [])
            pdf_files = ref.get("pdf_files", [])
            
            # Create a prompt for the Gemini model
            prompt = f"""
            You are an academic citation expert. Convert the following source references into detailed academic citations in APA format.
            
            Topic: {topic}
            Subtopic: {subtopic}
            Sources: {sources}
            PDF Files: {pdf_files}
            
            For each source, create a proper academic citation. If the source is an arXiv paper, use the arXiv ID to infer the publication year.
            If author names are not available, use placeholder [Author, A. A.] and mark the citation as [inferred].
            If the title is not available, use a placeholder [Title of paper] based on the topic and subtopic, and mark the citation as [inferred].
            """
            
            try:
                response = self.model.generate_content(prompt)
                enhanced_citations = response.text.strip().split('\n')
                enhanced_references.extend(enhanced_citations)
            except Exception as e:
                logger.error(f"Error enhancing references: {str(e)}")
                # Fallback to original format
                enhanced_references.append(f"{topic} - {subtopic}: Multiple sources: {sources}")
        
        return enhanced_references

    def conduct_research(self, problem_statement: str, search_engine: str) -> str:
        """
        Conduct research based on the problem statement using the specified search engine.
        
        Args:
            problem_statement: The research problem statement
            search_engine: The search engine URL to use
            
        Returns:
            Path to the generated final paper
        """
        logger.info(f"Conducting research on: {problem_statement}")
        logger.info(f"Using search engine: {search_engine}")
        
        # Store the problem statement
        self.problem_statement = problem_statement
        
        # Generate topics and subtopics
        self.topics = self.analyze_problem_statement(problem_statement)
        
        # Update the topics tracking file
        self.update_topics_tracking_file()
        
        # Start the browser
        logger.info("Starting browser...")
        self.start_browser()
        logger.info("Browser started successfully")
        
        try:
            # Process each topic and subtopic
            for topic_index, topic_data in enumerate(self.topics):
                topic_title = topic_data["title"]
                subtopics = topic_data["subtopics"]
                
                logger.info(f"Processing topic {topic_index + 1}/{len(self.topics)}: {topic_title}")
                
                # Create topic directory
                topic_dir = os.path.join(self.output_dir, "topics", self._sanitize_filename(topic_title))
                ensure_directory(topic_dir)
                
                # Process each subtopic
                for subtopic_index, subtopic_data in enumerate(subtopics):
                    subtopic_title = subtopic_data["title"]
                    
                    logger.info(f"Processing subtopic {subtopic_index + 1}/{len(subtopics)}: {subtopic_title}")
                    
                    # Set current topic and subtopic
                    self.current_topic = topic_title
                    self.current_subtopic = subtopic_title
                    
                    # Search for PDFs related to the subtopic
                    search_query = f"{subtopic_title} {self.search_suffix}"
                    
                    # Perform the search based on the search engine
                    pdf_urls = self._search_for_pdfs(search_query, search_engine)
                    
                    # Download and process PDFs
                    pdf_contents = []
                    for i, url in enumerate(pdf_urls[:self.max_pdfs_per_topic]):
                        try:
                            logger.info(f"Downloading PDF {i+1}/{min(len(pdf_urls), self.max_pdfs_per_topic)}: {url}")
                            pdf_path = self._download_pdf(url)
                            if pdf_path:
                                content = self._extract_pdf_content(pdf_path, topic_title, subtopic_title)
                                if content:
                                    pdf_contents.append(content)
                        except Exception as e:
                            logger.error(f"Error processing PDF {url}: {str(e)}")
                    
                    # Write subtopic file
                    subtopic_file = os.path.join(topic_dir, f"{self._sanitize_filename(subtopic_title)}.md")
                    self._write_subtopic_file(subtopic_file, topic_title, subtopic_title, pdf_contents)
                    
                    # Update subtopic status
                    subtopic_data["status"] = "completed"
            
            # Generate the final paper
            final_paper_path = self.generate_final_paper(self.topics)
            logger.info(f"Final paper generated at: {final_paper_path}")
            
            # Check if we should format as academic paper
            if self.academic_format:
                logger.info("Formatting final paper as academic paper...")
                try:
                    # Import the academic_formatter module
                    import academic_formatter
                    
                    # Initialize the model
                    model = academic_formatter.initialize_model()
                    if not model:
                        logger.error("Failed to initialize model for academic formatting")
                        return final_paper_path
                    
                    # Extract references and content
                    pdf_references, content = academic_formatter.extract_references_from_final_paper(final_paper_path)
                    
                    # Format as academic paper
                    formatted_paper = academic_formatter.format_as_academic_paper(model, content, pdf_references)
                    
                    # Save formatted paper
                    output_path = academic_formatter.save_formatted_paper(final_paper_path, formatted_paper)
                    
                    if output_path:
                        logger.info(f"Successfully formatted final paper as academic paper at {output_path}")
                    else:
                        logger.error("Failed to save formatted academic paper")
                except Exception as e:
                    logger.error(f"Error formatting final paper: {str(e)}")
            
            return final_paper_path
        finally:
            # Close the browser
            self.close_browser()
    
    def _search_for_pdfs(self, query: str, search_engine: str) -> List[str]:
        """
        Search for PDFs related to the query using the specified search engine.
        
        Args:
            query: The search query
            search_engine: The search engine URL
            
        Returns:
            List of PDF URLs
        """
        try:
            logger.info(f"Searching for PDFs with query: {query}")
            logger.info(f"Using search engine: {search_engine}")
            
            pdf_urls = []
            
            # Different search engines have different search interfaces
            if "arxiv.org" in search_engine:
                # For ArXiv, use a direct search approach
                logger.info("Using ArXiv direct search approach")
                
                # Format the query for ArXiv search
                formatted_query = query.replace(" ", "+")
                search_url = f"https://arxiv.org/search/?query={formatted_query}&searchtype=all"
                
                logger.info(f"Navigating to search URL: {search_url}")
                self.browser.get(search_url)
                
                # Wait for results to load
                time.sleep(5)
                
                # Take a screenshot for debugging
                screenshot_path = os.path.join(self.output_dir, "arxiv_search_results.png")
                self.browser.save_screenshot(screenshot_path)
                logger.info(f"Screenshot saved to {screenshot_path}")
                
                # Try to find result items
                try:
                    # Look for the results list
                    results_container = WebDriverWait(self.browser, self.timeout).until(
                        EC.presence_of_element_located((By.ID, "main-container"))
                    )
                    
                    # Find all paper entries
                    paper_entries = results_container.find_elements(By.CSS_SELECTOR, ".arxiv-result")
                    logger.info(f"Found {len(paper_entries)} paper entries")
                    
                    # Process each paper entry
                    for entry in paper_entries[:self.max_pdfs_per_topic]:
                        try:
                            # Find the title link which contains the paper ID
                            title_link = entry.find_element(By.CSS_SELECTOR, "p.title > a")
                            paper_url = title_link.get_attribute("href")
                            
                            if paper_url and "/abs/" in paper_url:
                                # Extract the paper ID
                                paper_id = paper_url.split("/abs/")[1]
                                
                                # Construct the PDF URL
                                pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
                                logger.info(f"Found paper: {paper_url}, PDF: {pdf_url}")
                                pdf_urls.append(pdf_url)
                        except Exception as e:
                            logger.warning(f"Error processing paper entry: {str(e)}")
                            continue
                    
                except TimeoutException:
                    logger.warning("Timeout waiting for ArXiv results container")
                
                # If no results found with the above method, try a more generic approach
                if not pdf_urls:
                    logger.info("No results found with standard method, trying generic approach")
                    
                    # Look for any links that might be PDF links
                    links = self.browser.find_elements(By.TAG_NAME, "a")
                    
                    for link in links:
                        try:
                            href = link.get_attribute("href")
                            if href and ("/pdf/" in href or href.endswith(".pdf")):
                                logger.info(f"Found PDF link with generic approach: {href}")
                                pdf_urls.append(href)
                        except:
                            continue
                    
                    # If still no results, try to find abstract links and convert them
                    if not pdf_urls:
                        logger.info("Trying to find abstract links")
                        
                        for link in links:
                            try:
                                href = link.get_attribute("href")
                                if href and "/abs/" in href:
                                    # Convert abstract URL to PDF URL
                                    pdf_url = href.replace("/abs/", "/pdf/") + ".pdf"
                                    logger.info(f"Converted abstract to PDF link: {pdf_url}")
                                    pdf_urls.append(pdf_url)
                            except:
                                continue
                
            elif "scholar.google.com" in search_engine:
                # Navigate to Google Scholar
                self.browser.get("https://scholar.google.com/")
                
                # Find the search box
                search_box = WebDriverWait(self.browser, self.timeout).until(
                    EC.presence_of_element_located((By.NAME, "q"))
                )
                
                # Enter the search query
                search_box.clear()
                search_box.send_keys(query)
                search_box.send_keys(Keys.RETURN)
                
                # Wait for results to load
                time.sleep(5)
                
                # Take a screenshot for debugging
                screenshot_path = os.path.join(self.output_dir, "google_scholar_results.png")
                self.browser.save_screenshot(screenshot_path)
                
                # Find PDF links
                pdf_links = self.browser.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                for link in pdf_links:
                    href = link.get_attribute("href")
                    if href and ".pdf" in href:
                        pdf_urls.append(href)
            
            else:
                # Generic search approach
                # Navigate to the search engine
                self.browser.get(search_engine)
                
                # Try to find a search box
                try:
                    search_box = WebDriverWait(self.browser, self.timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
                    )
                    
                    # Enter the search query
                    search_box.clear()
                    search_box.send_keys(query)
                    search_box.send_keys(Keys.RETURN)
                    
                    # Wait for results to load
                    time.sleep(5)
                    
                    # Take a screenshot for debugging
                    screenshot_path = os.path.join(self.output_dir, "generic_search_results.png")
                    self.browser.save_screenshot(screenshot_path)
                    
                    # Find PDF links
                    pdf_links = self.browser.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                    for link in pdf_links:
                        href = link.get_attribute("href")
                        if href and ".pdf" in href:
                            pdf_urls.append(href)
                
                except TimeoutException:
                    logger.error("Timeout waiting for search box on generic search engine")
            
            # Limit the number of PDFs
            pdf_urls = pdf_urls[:self.max_pdfs_per_topic]
            logger.info(f"Found {len(pdf_urls)} PDF links")
            
            return pdf_urls
            
        except Exception as e:
            logger.error(f"Error searching for PDFs: {str(e)}")
            # Take a screenshot for debugging
            try:
                screenshot_path = os.path.join(self.output_dir, "search_error.png")
                self.browser.save_screenshot(screenshot_path)
                logger.info(f"Error screenshot saved to {screenshot_path}")
            except:
                pass
            return []
    
    def _download_pdf(self, url: str) -> Optional[str]:
        """
        Download a PDF from a URL.
        
        Args:
            url: The URL of the PDF to download
            
        Returns:
            Optional[str]: The path to the downloaded PDF, or None if download failed
        """
        try:
            logger.info(f"Attempting to download PDF from: {url}")
            
            # Create a filename from the URL
            filename = self._sanitize_filename(os.path.basename(url))
            if not filename.endswith(".pdf"):
                filename += ".pdf"
            
            # Create the full path
            pdf_dir = os.path.join(self.output_dir, "pdfs")
            ensure_directory(pdf_dir)
            pdf_path = os.path.join(pdf_dir, filename)
            
            # Download the PDF
            logger.info(f"Downloading to: {pdf_path}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            try:
                response = requests.get(url, stream=True, timeout=self.timeout, headers=headers)
                
                # Check if the request was successful
                if response.status_code == 200:
                    # Check if the content is a PDF
                    content_type = response.headers.get('Content-Type', '')
                    if 'application/pdf' in content_type or url.endswith('.pdf'):
                        # Save the PDF
                        with open(pdf_path, "wb") as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                        
                        logger.info(f"PDF downloaded successfully to: {pdf_path}")
                        return pdf_path
                    else:
                        logger.warning(f"URL does not point to a PDF. Content-Type: {content_type}")
                        
                        # Try to download anyway if the URL ends with .pdf
                        if url.endswith('.pdf'):
                            logger.info("URL ends with .pdf, attempting to download anyway")
                            with open(pdf_path, "wb") as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                            
                            logger.info(f"PDF downloaded successfully to: {pdf_path}")
                            return pdf_path
                else:
                    logger.warning(f"Failed to download PDF. Status code: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error while downloading PDF: {str(e)}")
                
                # Try using the browser to download the PDF
                logger.info("Attempting to download using the browser")
                try:
                    # Navigate to the PDF URL
                    self.browser.get(url)
                    
                    # Wait for the PDF to load
                    time.sleep(5)
                    
                    # Save the page source
                    page_source = self.browser.page_source
                    
                    # Check if it's a PDF
                    if "PDF" in page_source or "%PDF" in page_source:
                        # Save the PDF
                        with open(pdf_path, "wb") as f:
                            f.write(page_source.encode('utf-8'))
                        
                        logger.info(f"PDF downloaded using browser to: {pdf_path}")
                        return pdf_path
                    else:
                        logger.warning("Browser download failed: Not a PDF")
                except Exception as browser_e:
                    logger.error(f"Browser download error: {str(browser_e)}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error downloading PDF: {str(e)}")
            return None
    
    def _extract_pdf_content(self, pdf_path: str, topic: str, subtopic: str) -> Optional[Dict[str, Any]]:
        """
        Extract content from a PDF for a specific topic and subtopic.
        
        Args:
            pdf_path: The path to the PDF
            topic: The topic
            subtopic: The subtopic
            
        Returns:
            Optional[Dict[str, Any]]: The extracted content, or None if extraction failed
        """
        try:
            # Read the PDF
            with open(pdf_path, "rb") as f:
                pdf_content = f.read()
            
            # Extract text from the PDF
            text = self._extract_text_from_pdf(pdf_content)
            if not text:
                logger.error(f"Failed to extract text from PDF: {pdf_path}")
                return None
            
            # Create a prompt for the Gemini model
            prompt = f"""
            Extract relevant information from this academic paper for a research on the following topic and subtopic:
            
            Topic: {topic}
            Subtopic: {subtopic}
            
            Please analyze the following text and extract:
            1. Key findings related to the topic and subtopic
            2. Analysis and insights
            3. Examples or case studies
            4. Conclusions
            
            Format your response as a structured markdown document with appropriate headings.
            
            Text from the paper:
            {text[:10000]}  # Limit text to 10,000 characters to avoid token limits
            """
            
            # Generate content using the Gemini model
            response = self._api_call_with_retry(
                lambda: self.model.generate_content(prompt).text
            )
            
            # Create the content dictionary
            content = {
                "source": os.path.basename(pdf_path),
                "content": response
            }
            
            return content
            
        except Exception as e:
            logger.error(f"Error extracting content from PDF: {str(e)}")
            return None
    
    def _extract_text_from_pdf(self, pdf_content: bytes) -> Optional[str]:
        """
        Extract text from a PDF.
        
        Args:
            pdf_content: The PDF content as bytes
            
        Returns:
            Optional[str]: The extracted text, or None if extraction failed
        """
        try:
            # Try to import PyPDF2
            import PyPDF2
            from PyPDF2 import PdfReader
            
            # Create a BytesIO object from the PDF content
            pdf_file = BytesIO(pdf_content)
            
            # Extract text with PyPDF2
            reader = PdfReader(pdf_file)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return None
    
    def _write_subtopic_file(self, file_path: str, topic: str, subtopic: str, contents: List[Dict[str, Any]]) -> None:
        """
        Write a subtopic file with the extracted content.
        
        Args:
            file_path: The path to the subtopic file
            topic: The topic
            subtopic: The subtopic
            contents: The extracted content
        """
        try:
            # Import academic formatter functions
            from academic_formatter import extract_metadata_from_pdf, generate_academic_citations
            
            with open(file_path, "w", encoding="utf-8") as f:
                # Write the header
                f.write(f"# {subtopic}\n\n")
                
                if not contents:
                    f.write(f"No content found for {subtopic} related to {topic}.\n\n")
                    f.write("## References\n\n")
                    f.write("No sources processed yet.\n")
                    return
                
                # Write the content
                for content in contents:
                    f.write(content["content"])
                    f.write("\n\n")
                
                # Write the references section
                f.write("## References\n\n")
                
                # Process each source to create academic citations
                for i, content in enumerate(contents, 1):
                    source_file = content["source"]
                    
                    # Check if it's a PDF file path
                    if source_file.lower().endswith('.pdf'):
                        # Get the full path to the PDF
                        pdf_dir = os.path.join(self.output_dir, "pdfs")
                        pdf_path = os.path.join(pdf_dir, source_file)
                        
                        if os.path.exists(pdf_path):
                            # Extract metadata and create citation
                            try:
                                metadata = extract_metadata_from_pdf(pdf_path)
                                
                                # Format authors
                                authors = metadata.get('authors', 'Unknown')
                                
                                # Format title
                                title = metadata.get('title', source_file.replace('.pdf', ''))
                                
                                # Format year
                                year = metadata.get('year', 'n.d.')
                                
                                # Create citation in APA format
                                citation = f"{i}. {authors} ({year}). {title}."
                                f.write(f"{citation}\n")
                            except Exception as e:
                                logger.warning(f"Error creating academic citation for {source_file}: {str(e)}")
                                f.write(f"{i}. SOURCE: {source_file}\n")
                        else:
                            f.write(f"{i}. SOURCE: {source_file}\n")
                    else:
                        # For non-PDF sources, just use the source name
                        f.write(f"{i}. SOURCE: {source_file}\n")
            
            logger.info(f"Wrote subtopic file: {file_path}")
            
        except Exception as e:
            logger.error(f"Error writing subtopic file: {str(e)}")
            
            # Create a placeholder file if writing fails
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"# {subtopic}\n\n")
                    f.write(f"Error processing content for {subtopic} related to {topic}: {str(e)}\n\n")
                    f.write("## References\n\n")
                    f.write("No sources processed successfully.\n")
            except:
                pass

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a string to be used as a filename.
        
        Args:
            filename: The string to sanitize
            
        Returns:
            A sanitized string that can be used as a filename
        """
        # Replace invalid characters with underscores
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '_', filename)
        
        # Trim whitespace and limit length
        sanitized = sanitized.strip()
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
            
        return sanitized

    def load_topics_from_md(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load topics and subtopics from a markdown file.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            List of topics with their subtopics
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the markdown content to extract topics and subtopics
            topics = []
            current_topic = None
            
            for line in content.split('\n'):
                if line.startswith('## '):
                    # This is a topic
                    if current_topic:
                        topics.append(current_topic)
                    
                    topic_title = line[3:].strip()
                    current_topic = {
                        "title": topic_title,
                        "subtopics": []
                    }
                elif line.startswith('- ') and current_topic:
                    # This is a subtopic
                    subtopic_title = line[2:].strip()
                    current_topic["subtopics"].append({
                        "title": subtopic_title,
                        "status": "completed"
                    })
            
            # Add the last topic
            if current_topic:
                topics.append(current_topic)
            
            return topics
        except Exception as e:
            logger.error(f"Error loading topics from markdown file: {str(e)}")
            return []

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="LazyScholar - Academic Research Assistant")
    parser.add_argument("problem_statement", type=str, help="The research problem statement")
    parser.add_argument("--search-engine", type=str, default="https://scholar.google.com",
                        help="Search engine URL (default: https://scholar.google.com)")
    parser.add_argument("--output-dir", type=str, default="research_output",
                        help="Directory to store research output (default: research_output)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--timeout", type=int, default=120,
                        help="Timeout in seconds for browser operations (default: 120)")
    parser.add_argument("--max-pdfs", type=int, default=10,
                        help="Maximum number of PDFs to process per topic (default: 10)")
    parser.add_argument("--search-suffix", type=str, default="",
                        help="Suffix to append to search queries (e.g., 'filetype:pdf')")
    parser.add_argument("--focus", type=str, default="all", choices=["pdf", "html", "all"],
                        help="Type of content to focus on (default: all)")
    parser.add_argument("--regenerate-final-paper", action="store_true",
                        help="Regenerate the final paper from existing subtopic files")
    
    parser.add_argument(
        "--academic-format",
        action="store_true",
        help="Format the final paper as an academic paper with proper citations and references"
    )
    
    args = parser.parse_args()
    
    return args

def main():
    """Main entry point for the LazyScholar application."""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Configure logging
        logger.info("Parsing command line arguments...")
        
        # Print banner
        print("\n" + "=" * 80)
        print(" " * 19 + "LazyScholar - Academic Research Assistant")
        print("=" * 80 + "\n")
        
        # Log configuration
        logger.info("Configuration:")
        logger.info(f"Problem statement: {args.problem_statement}")
        logger.info(f"Search engine: {args.search_engine}")
        logger.info(f"Output directory: {args.output_dir}")
        logger.info(f"Headless mode: {args.headless}")
        logger.info(f"Timeout: {args.timeout} seconds")
        logger.info(f"Max PDFs per topic: {args.max_pdfs}")
        logger.info(f"Focus mode: {args.focus}")
        
        # Initialize LazyScholar
        logger.info("Initializing LazyScholar...")
        scholar = LazyScholar(
            headless=args.headless,
            output_dir=args.output_dir,
            timeout=args.timeout,
            search_suffix=args.search_suffix,
            max_pdfs_per_topic=args.max_pdfs,
            focus=args.focus,
            academic_format=args.academic_format
        )
        
        # Log academic format setting
        logger.info(f"Academic format: {args.academic_format}")
        
        # Check if we should just regenerate the final paper
        if hasattr(args, 'regenerate_final_paper') and args.regenerate_final_paper:
            logger.info("Regenerating final paper from existing subtopic files...")
            
            # Load topics from tracking file
            topics_file = os.path.join(args.output_dir, "topics_and_subtopics.md")
            if os.path.exists(topics_file):
                topics = scholar.load_topics_from_md(topics_file)
                
                # Generate final paper
                logger.info("Generating final paper using LLM...")
                final_paper_path = scholar.generate_final_paper(topics)
                logger.info(f"Generated final paper at {final_paper_path}")
                
                # Format as academic paper if requested
                if hasattr(args, 'academic_format') and args.academic_format:
                    logger.info("Formatting final paper as academic paper...")
                    try:
                        import academic_formatter
                        
                        # Initialize model
                        model = academic_formatter.initialize_model()
                        if not model:
                            logger.error("Failed to initialize model for academic formatting")
                            return
                        
                        # Extract references and content
                        pdf_references, content = academic_formatter.extract_references_from_final_paper(final_paper_path)
                        
                        # Format paper
                        formatted_paper = academic_formatter.format_as_academic_paper(model, content, pdf_references)
                        
                        # Save formatted paper
                        output_path = academic_formatter.save_formatted_paper(final_paper_path, formatted_paper)
                        logger.info(f"Successfully formatted final paper as academic paper at {output_path}")
                    except Exception as e:
                        logger.error(f"Error formatting final paper: {str(e)}")
            else:
                logger.error(f"Topics file not found at {topics_file}")
                return
        
        # Start research process
        logger.info("Starting research process...")
        final_paper_path = scholar.conduct_research(args.problem_statement, args.search_engine)
        
        logger.info("Research completed successfully!")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()