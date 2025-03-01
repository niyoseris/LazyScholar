"""
Topic Generator Module - Generates topics and subtopics from a problem statement.
"""

import os
import logging
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

logger = logging.getLogger(__name__)

# Configure the Gemini API
def setup_gemini_api():
    """Set up and configure the Gemini API with the API key."""
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    
    # Configure safety settings
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
    
    return safety_settings

def generate_topics_subtopics(problem_statement):
    """
    Generate topics and subtopics based on the problem statement using Gemini.
    
    Args:
        problem_statement (str): The research problem statement.
        
    Returns:
        list: A list of dictionaries, each containing a 'topic' and 'subtopics' key.
    """
    logger.info("Generating topics and subtopics for: %s", problem_statement)
    
    safety_settings = setup_gemini_api()
    
    # Create a model instance
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        safety_settings=safety_settings,
        generation_config={"temperature": 0.2}
    )
    
    # Craft the prompt for topic generation
    prompt = f"""
    You are an academic research assistant. Based on the following research problem statement,
    extract specific research topics and subtopics directly related to this area of research.
    Avoid generic academic paper sections (like "Introduction", "Literature Review", "Methodology").
    Instead, focus on the ACTUAL SUBJECT MATTER topics that need to be researched.
    
    Problem Statement: "{problem_statement}"
    
    For each main subject-specific topic, provide 2-4 relevant subtopics. All topics should be 
    directly related to the research domain and represent areas that need academic investigation.
    
    Format your response as a JSON-compatible list of dictionaries,
    where each dictionary has two keys: 'topic' and 'subtopics', and 'subtopics' is a list of strings.
    
    Example format for climate change research:
    [
        {{"topic": "Rising Sea Levels in Mediterranean Basin", "subtopics": ["Impact on Cyprus Coastal Areas", "Adaptation Strategies in Cyprus", "Historical Sea Level Changes"]}},
        {{"topic": "Temperature Changes in Cyprus", "subtopics": ["Urban Heat Island Effects", "Agricultural Impacts", "Public Health Implications"]}}
    ]
    
    Only provide the list with no additional text.
    """
    
    try:
        # Generate the response
        response = model.generate_content(prompt)
        
        # Extract and parse the response text
        response_text = response.text
        
        # Parse the JSON response
        import json
        try:
            # Try to directly parse the response
            topics_subtopics = json.loads(response_text)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from text
            logger.warning("Failed to parse JSON directly. Attempting to extract JSON from text.")
            # Look for content within square brackets which should contain the JSON array
            import re
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response_text, re.DOTALL)
            if json_match:
                try:
                    topics_subtopics = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    # If extraction still fails, use a more robust approach
                    logger.error("Failed to parse extracted JSON content.")
                    # Fall back to a simple format conversion approach
                    # This is a basic fallback that converts the text to a simple list of topics
                    topics_subtopics = [
                        {"topic": problem_statement, "subtopics": ["Research Background", "Current Status", "Future Implications"]}
                    ]
            else:
                logger.error("Could not find JSON content in the response.")
                topics_subtopics = [
                    {"topic": problem_statement, "subtopics": ["Research Background", "Current Status", "Future Implications"]}
                ]
        
        logger.info(f"Generated {len(topics_subtopics)} topics with their subtopics")
        
        # Log the topics in a more descriptive and readable format
        for idx, topic in enumerate(topics_subtopics, 1):
            topic_name = topic.get('topic', 'Unknown Topic')
            subtopics = topic.get('subtopics', [])
            
            # Format the topic index and name without truncation
            formatted_topic = f"{idx}. {topic_name}"
            logger.info(f"Topic {formatted_topic}")
            
            # Log each subtopic
            for sub_idx, subtopic in enumerate(subtopics, 1):
                logger.info(f"   {sub_idx}. {subtopic}")
                
        return topics_subtopics
        
    except Exception as e:
        logger.error(f"Error generating topics: {str(e)}", exc_info=True)
        # Return a default structure in case of error
        return [
            {"topic": problem_statement, "subtopics": ["Research Background", "Current Status", "Future Implications"]}
        ]
