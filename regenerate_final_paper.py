#!/usr/bin/env python3
"""
Script to regenerate the final paper from existing research output.
"""

import os
import sys
import time
import logging
from typing import List, Dict, Any, Callable, Optional
from lazy_scholar import LazyScholar, ensure_directory

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FastRetryLazyScholar(LazyScholar):
    """
    A subclass of LazyScholar that uses shorter retry delays for testing.
    """
    
    def _api_call_with_retry(self, api_func: Callable, max_retries: int = 5, retry_delay: int = 2) -> Any:
        """
        Call an API function with retry logic, using shorter delays.
        
        Args:
            api_func: The API function to call
            max_retries: Maximum number of retries
            retry_delay: Initial delay between retries in seconds
            
        Returns:
            The result of the API call
        """
        retries = 0
        last_exception = None
        
        while retries <= max_retries:
            try:
                return api_func()
            except Exception as e:
                last_exception = e
                retries += 1
                
                # Check if it's a quota exhaustion error
                if "429" in str(e) or "Resource has been exhausted" in str(e):
                    # Use shorter delays: 2, 4, 8, 16, 32 seconds
                    wait_time = 2 * (2 ** (retries - 1))  # 2, 4, 8, 16, 32 seconds
                    logger.warning(f"API quota exhausted (429). Waiting for {wait_time} seconds before retry {retries}/{max_retries}")
                    
                    # Wait with progress updates
                    start_time = time.time()
                    end_time = start_time + wait_time
                    
                    while time.time() < end_time:
                        remaining = int(end_time - time.time())
                        if remaining > 0 and remaining % 5 == 0:  # Update every 5 seconds
                            logger.info(f"Still waiting... {remaining} seconds left before retry")
                        time.sleep(1)
                else:
                    # For other errors, use a fixed delay
                    logger.warning(f"API call failed with error: {str(e)}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                
                if retries > max_retries:
                    logger.error(f"Maximum retries ({max_retries}) exceeded. Last error: {str(last_exception)}")
                    # Return a fallback value instead of raising an exception
                    return "API call failed after maximum retries"
        
        # This should not be reached, but just in case
        return "API call failed"

def get_topics_from_directory(research_dir: str) -> List[Dict[str, Any]]:
    """
    Extract topics and subtopics from the directory structure.
    
    Args:
        research_dir: Path to the research output directory
        
    Returns:
        List of topics and subtopics
    """
    topics = []
    topics_dir = os.path.join(research_dir, "topics")
    
    if not os.path.exists(topics_dir):
        logger.error(f"Topics directory not found: {topics_dir}")
        return topics
    
    # Get all topic directories
    topic_dirs = [d for d in os.listdir(topics_dir) if os.path.isdir(os.path.join(topics_dir, d))]
    
    for topic_dir in topic_dirs:
        topic_path = os.path.join(topics_dir, topic_dir)
        topic_title = topic_dir.replace("_", " ")
        
        # Get all subtopic files
        subtopic_files = [f for f in os.listdir(topic_path) if f.endswith(".md")]
        
        subtopics = []
        for subtopic_file in subtopic_files:
            subtopic_path = os.path.join(topic_path, subtopic_file)
            subtopic_title = subtopic_file.replace(".md", "").replace("_", " ")
            
            subtopics.append({
                "title": subtopic_title,
                "file": subtopic_path
            })
        
        topics.append({
            "title": topic_title,
            "subtopics": subtopics
        })
    
    return topics

def generate_final_paper_without_api(research_dir: str, topics: List[Dict[str, Any]]) -> str:
    """
    Generate the final paper without using API calls for reference enhancement.
    
    Args:
        research_dir: Path to the research output directory
        topics: List of topics and subtopics
        
    Returns:
        Path to the generated final paper
    """
    logger.info("Generating final paper without API calls...")
    
    # Path to the final paper
    final_paper_path = os.path.join(research_dir, "final_paper.md")
    
    # Collect all the content
    all_content = []
    references = []
    
    # Process each topic
    for topic in topics:
        topic_title = topic.get("title", "")
        subtopics = topic.get("subtopics", [])
        
        # Add the topic to the content
        all_content.append(f"# {topic_title}\n")
        
        # Process each subtopic
        for subtopic in subtopics:
            subtopic_title = subtopic.get("title", "")
            subtopic_file = subtopic.get("file", "")
            
            # Add the subtopic to the content
            all_content.append(f"## {subtopic_title}\n")
            
            # Read the subtopic file
            if subtopic_file and os.path.exists(subtopic_file):
                try:
                    with open(subtopic_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                        # Extract the content (skip the title and references)
                        content_parts = content.split("## References")
                        
                        if len(content_parts) > 1:
                            # Get the main content part
                            main_content = content_parts[0]
                            
                            # Remove the title if it exists
                            if main_content.startswith("# "):
                                main_content_lines = main_content.split("\n")
                                if len(main_content_lines) > 1:
                                    main_content = "\n".join(main_content_lines[1:])
                            
                            # Add the cleaned content
                            all_content.append(f"{main_content.strip()}\n\n")
                            
                            # Extract the references
                            refs_part = content_parts[1].strip()
                            refs_lines = refs_part.split("\n")
                            for line in refs_lines:
                                if line.strip() and (line.strip().startswith("1.") or line.strip().startswith("-")):
                                    references.append(f"{topic_title} - {subtopic_title}: {line.strip()}")
                        else:
                            # If no references section, just add the content
                            # Remove the title if it exists
                            if content.startswith("# "):
                                content_lines = content.split("\n")
                                if len(content_lines) > 1:
                                    content = "\n".join(content_lines[1:])
                            
                            all_content.append(f"{content.strip()}\n\n")
                except Exception as e:
                    logger.error(f"Error reading subtopic file {subtopic_file}: {str(e)}")
                    all_content.append(f"Error reading content for {subtopic_title}.\n\n")
        
        # Add a separator between topics
        all_content.append("\n---\n\n")
    
    # Add the references section
    all_content.append("# References\n\n")
    for ref in references:
        all_content.append(f"- {ref}\n")
    
    # Write the final paper
    try:
        with open(final_paper_path, "w", encoding="utf-8") as f:
            f.write("\n".join(all_content))
        
        logger.info(f"Final paper generated at: {final_paper_path}")
        return final_paper_path
    except Exception as e:
        logger.error(f"Error writing final paper: {str(e)}")
        return ""

def main():
    """Main function to regenerate the final paper."""
    if len(sys.argv) < 2:
        print("Usage: python regenerate_final_paper.py <research_dir>")
        print("Example: python regenerate_final_paper.py /Users/niyoseris/Desktop/Python/Akademik/research_output/1/5")
        sys.exit(1)
    
    research_dir = sys.argv[1]
    
    if not os.path.exists(research_dir):
        logger.error(f"Research directory not found: {research_dir}")
        sys.exit(1)
    
    # Get topics from directory structure
    topics = get_topics_from_directory(research_dir)
    
    if not topics:
        logger.error("No topics found in the research directory")
        sys.exit(1)
    
    logger.info(f"Found {len(topics)} topics with {sum(len(t['subtopics']) for t in topics)} subtopics")
    
    # Check if we should use API calls or not
    use_api = False
    if len(sys.argv) > 2 and sys.argv[2].lower() == "use_api":
        use_api = True
    
    if use_api:
        # Initialize LazyScholar with faster retry
        scholar = FastRetryLazyScholar(output_dir=research_dir)
        
        # Generate the final paper with API calls
        final_paper_path = scholar.generate_final_paper(topics)
    else:
        # Generate the final paper without API calls
        final_paper_path = generate_final_paper_without_api(research_dir, topics)
    
    if final_paper_path:
        logger.info(f"Final paper regenerated successfully: {final_paper_path}")
    else:
        logger.error("Failed to regenerate final paper")
        sys.exit(1)

if __name__ == "__main__":
    main() 