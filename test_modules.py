"""
Test Script - Simple tests for each module of the academic research assistant.
"""

import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

from topic_generator import generate_topics_subtopics
from web_scraper import setup_browser, search_academic_database
from content_analyzer import extract_paper_information, identify_new_topics
from text_compiler import extract_citations, generate_section_content

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_topic_generator():
    """Test the topic generator module."""
    print("\n===== Testing Topic Generator =====")
    problem_statement = "What are the effects of climate change on marine biodiversity?"
    
    print(f"Problem statement: {problem_statement}")
    topics = generate_topics_subtopics(problem_statement)
    
    print("\nGenerated topics and subtopics:")
    for topic in topics:
        print(f"Topic: {topic['topic']}")
        for subtopic in topic['subtopics']:
            print(f"  - {subtopic}")
    
    return topics

def test_web_scraper():
    """Test the web scraper module."""
    print("\n===== Testing Web Scraper =====")
    try:
        browser = setup_browser()
        print("Browser setup successful")
        
        # Test with a simple search
        search_results = search_academic_database(
            browser, 
            "https://scholar.google.com", 
            ["climate change marine biodiversity"]
        )
        
        print(f"\nFound {len(search_results)} results")
        for i, result in enumerate(search_results[:3], 1):
            print(f"{i}. {result.get('title', 'Unknown Title')}")
        
        browser.quit()
        return search_results
        
    except Exception as e:
        logger.error(f"Web scraper test failed: {str(e)}", exc_info=True)
        print(f"Test failed: {str(e)}")
        return []

def test_content_analyzer(search_results):
    """Test the content analyzer module."""
    print("\n===== Testing Content Analyzer =====")
    
    if not search_results:
        # Create mock result for testing
        mock_result = {
            'title': 'Impact of Climate Change on Marine Ecosystems',
            'snippet': 'This study examines how rising temperatures and ocean acidification affect marine biodiversity, with particular focus on coral reef ecosystems.',
            'database': 'mock_database'
        }
        search_results = [mock_result]
    
    # Test paper information extraction
    print("Testing paper information extraction:")
    paper_info = extract_paper_information(search_results[0])
    
    print(f"Title: {paper_info.get('title', '')}")
    print(f"Summary: {paper_info.get('summary', '')[:100]}...")
    
    # Test new topic identification
    original_topics = [
        {
            "topic": "Climate Change", 
            "subtopics": ["Temperature Rise", "Ocean Acidification"]
        }
    ]
    
    new_topics = identify_new_topics([paper_info], original_topics)
    
    print("\nIdentified new topics:")
    for topic in new_topics:
        print(f"Topic: {topic['topic']}")
        for subtopic in topic['subtopics']:
            print(f"  - {subtopic}")
    
    return paper_info

def test_text_compiler(paper_info):
    """Test the text compiler module."""
    print("\n===== Testing Text Compiler =====")
    
    # Create mock analyzed content
    analyzed_content = {
        "climate change": [paper_info]
    }
    
    # Test citation extraction
    citations = extract_citations(analyzed_content)
    print("Generated citations:")
    for citation in citations:
        print(f"- {citation}")
    
    # Test section content generation
    print("\nGenerating sample section content:")
    section = {"name": "Climate Change Impact"}
    content = generate_section_content(section, analyzed_content)
    
    # Print a preview of the content
    preview_length = 200
    content_preview = content[:preview_length] + "..." if len(content) > preview_length else content
    print(f"\nSection content preview:\n{content_preview}")

def main():
    """Run tests for all modules."""
    # Load API key
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("Error: Google API key not found. Please set GOOGLE_API_KEY in .env file")
        print("Copy .env.template to .env and add your API key")
        return
    
    # Configure Gemini API
    genai.configure(api_key=api_key)
    
    try:
        # Test topic generator
        topics = test_topic_generator()
        
        # Test web scraper
        search_results = test_web_scraper()
        
        # Test content analyzer
        paper_info = test_content_analyzer(search_results)
        
        # Test text compiler
        test_text_compiler(paper_info)
        
        print("\n===== All tests completed =====")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        print(f"Test failed: {str(e)}")

if __name__ == "__main__":
    main()
