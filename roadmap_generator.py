"""
Roadmap Generator Module - Creates a research roadmap before starting the research process.
"""

import os
import logging
import datetime
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

logger = logging.getLogger(__name__)

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

def get_topic_name(topic_dict):
    """
    Get the topic name from a topic dictionary, handling different formats.
    
    Args:
        topic_dict (dict): A dictionary containing topic information
        
    Returns:
        str: The name/title of the topic
    """
    # Handle both old format ('name' key) and new format ('topic' key)
    return topic_dict.get('name', topic_dict.get('topic', 'Unknown Topic'))

def get_subtopics(topic_dict):
    """
    Get the subtopics from a topic dictionary, handling different formats.
    
    Args:
        topic_dict (dict): A dictionary containing topic information
        
    Returns:
        list: A list of subtopics
    """
    return topic_dict.get('subtopics', [])

def generate_research_roadmap(problem_statement, topics_subtopics=None):
    """
    Generate a research roadmap based on the problem statement and initial topics/subtopics.
    This simplified version only lists the topics and subtopics, without using the AI model.
    
    Args:
        problem_statement (str): The research problem statement
        topics_subtopics (list, optional): List of initial topics and subtopics
        
    Returns:
        str: The generated research roadmap in Markdown format
    """
    logger.info("Generating research roadmap...")
    
    # Current date and time
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create basic roadmap with just topics and subtopics
    roadmap_content = f"""# Research Topics and Subtopics For: {problem_statement}

## Topics and Subtopics to Research
"""
    
    # Check if topics_subtopics is provided
    if not topics_subtopics:
        roadmap_content += "\nNo topics have been generated yet."
    else:
        # Add each topic and its subtopics
        for i, topic_item in enumerate(topics_subtopics, 1):
            topic_name = get_topic_name(topic_item)
            subtopics = get_subtopics(topic_item)
            
            roadmap_content += f"\n### {i}. {topic_name}\n"
            
            # Add subtopics as bullet points
            for subtopic in subtopics:
                roadmap_content += f"- {subtopic}\n"
            
            # Add a blank line between topics
            roadmap_content += "\n"
    
    # Add generation timestamp
    roadmap_content += f"---\n*Generated on: {current_time}*"
    
    # Save the roadmap to a file in the main directory, not in research_results
    filename = 'roadmap.md'
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(roadmap_content)
    
    logger.info(f"Roadmap saved to {filename}")
    
    return roadmap_content

def create_basic_roadmap_template(problem_statement, topics_subtopics, error=None):
    """
    Create a basic roadmap template directly from the topics and subtopics.
    This function serves as a fallback when API calls fail.
    
    Args:
        problem_statement (str): The research problem statement
        topics_subtopics (list): List of topics and subtopics
        error (Exception, optional): Error that occurred during API call
        
    Returns:
        str: Basic roadmap template in Markdown format
    """
    # Current date and time
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Extract topics and construct research objectives
    research_objectives = []
    formatted_topics_sections = []
    
    for i, topic_item in enumerate(topics_subtopics, 1):
        topic_name = get_topic_name(topic_item)
        subtopics = get_subtopics(topic_item)
        
        # Skip generic topics like "Introduction", "Literature Review", etc.
        if any(generic in topic_name.lower() for generic in ["introduction", "literature review", "methodology", "findings", "discussion", "conclusion"]):
            continue
            
        # Add a research objective based on the topic
        research_objectives.append(f"- Investigate {topic_name.lower()}")
        
        # Format topic section
        topic_section = f"### {i}. {topic_name}\n"
        for subtopic in subtopics:
            topic_section += f"- {subtopic}\n"
        
        topic_section += "\n"
        formatted_topics_sections.append(topic_section)
    
    # If we filtered out all topics or have no specific topics, create generic objectives
    if not research_objectives:
        research_objectives = [
            f"- Investigate {problem_statement} comprehensively",
            "- Analyze existing research and identify gaps",
            "- Develop evidence-based conclusions and recommendations",
            "- Contribute new knowledge to the field"
        ]
    
    # Create a basic timeline
    start_date = datetime.datetime.now()
    month_1 = (start_date + datetime.timedelta(days=30)).strftime("%B %Y")
    month_2 = (start_date + datetime.timedelta(days=60)).strftime("%B %Y")
    month_3 = (start_date + datetime.timedelta(days=90)).strftime("%B %Y")
    
    # Build the roadmap content
    roadmap_content = f"""# Research Roadmap: {problem_statement}

## Problem Statement
> {problem_statement}

## Research Objectives
{chr(10).join(research_objectives)}

## Topics and Subtopics
{chr(10).join(formatted_topics_sections)}

## Methodology and Approach
### Research Design
- Mixed-methods approach combining quantitative and qualitative research
- Comparative analysis of existing literature and case studies
- Systematic review of relevant academic publications
- Development of a conceptual framework for analysis

### Data Collection Methods
- Academic database searches (Google Scholar, ResearchGate, etc.)
- Review of peer-reviewed journals and conference proceedings
- Analysis of relevant case studies and reports
- Expert interviews and consultations when possible

## Timeline and Milestones
### {month_1}
- Complete comprehensive literature review
- Finalize research methodology
- Identify key research questions and hypotheses

### {month_2}
- Complete data collection from academic sources
- Begin data analysis and synthesis
- Identify preliminary patterns and findings

### {month_3}
- Complete analysis and interpretation
- Draft research paper with findings
- Prepare conclusions and recommendations

## Potential Challenges and Mitigation Strategies
- Limited available research: Expand search criteria and consult experts
- Conflicting data: Carefully analyze methodologies and account for differences
- Time constraints: Establish clear priorities and milestones
- Complexity of the topic: Develop a structured analysis framework

## Expected Outcomes
- Comprehensive understanding of {problem_statement}
- Identification of key insights and patterns
- Evidence-based recommendations for future research or action
- Contribution to the academic knowledge base

---
*Generated on: {current_time}*
"""
    
    # If there was an error, add a note about it
    if error:
        roadmap_content += f"\n\n*Note: This is a template roadmap created without API assistance. Error: {str(error)}*"
    
    return roadmap_content

def format_topics_for_roadmap(topics_subtopics):
    """
    Format topics and subtopics for the roadmap.
    
    Args:
        topics_subtopics (list): List of topics and subtopics
        
    Returns:
        list: Formatted topics and subtopics as markdown bullet points
    """
    formatted_list = []
    
    if not topics_subtopics:
        return ["- No topics available yet"]
    
    for i, topic_item in enumerate(topics_subtopics, 1):
        topic_name = get_topic_name(topic_item)
        subtopics = get_subtopics(topic_item)
        
        formatted_topic = f"### {i}. {topic_name}"
        formatted_list.append(formatted_topic)
        
        for subtopic in subtopics:
            formatted_list.append(f"- {subtopic}")
        
        # Add a blank line between topics
        formatted_list.append("")
    
    return formatted_list

def generate_fallback_roadmap(problem_statement, topics_subtopics=None):
    """
    Generate a simple roadmap template as a fallback when the API fails.
    
    Args:
        problem_statement (str): The research problem statement
        topics_subtopics (list, optional): List of initial topics and subtopics
        
    Returns:
        str: A simple roadmap template in Markdown format
    """
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    roadmap = f"# Research Roadmap: {problem_statement.strip()}\n\n"
    roadmap += f"Generated: {current_time}\n\n"
    roadmap += "## Research Overview\n\n"
    roadmap += f"This roadmap outlines the research approach for investigating: {problem_statement}\n\n"
    
    roadmap += "## Research Objectives\n\n"
    roadmap += "- To conduct a comprehensive literature review\n"
    roadmap += "- To identify key themes and patterns in the literature\n"
    roadmap += "- To develop insights and recommendations based on findings\n\n"
    
    if topics_subtopics:
        roadmap += "## Research Topics\n\n"
        for topic in topics_subtopics:
            topic_name = get_topic_name(topic)
            subtopics = get_subtopics(topic)
            
            roadmap += f"### {topic_name}\n\n"
            for subtopic in subtopics:
                roadmap += f"- {subtopic}\n"
            roadmap += "\n"
    else:
        roadmap += "## Proposed Research Topics\n\n"
        roadmap += "### Topic 1\n\n"
        roadmap += "- Subtopic 1.1\n"
        roadmap += "- Subtopic 1.2\n\n"
        roadmap += "### Topic 2\n\n"
        roadmap += "- Subtopic 2.1\n"
        roadmap += "- Subtopic 2.2\n\n"
    
    roadmap += "## Methodology\n\n"
    roadmap += "1. Literature search and review\n"
    roadmap += "2. Content analysis and synthesis\n"
    roadmap += "3. Findings compilation and integration\n\n"
    
    roadmap += "## Timeline\n\n"
    roadmap += "- Literature Review: 2 weeks\n"
    roadmap += "- Analysis: 1 week\n"
    roadmap += "- Compilation: 1 week\n\n"
    
    roadmap += "## Challenges and Mitigation\n\n"
    roadmap += "- Challenge: Limited access to academic databases\n"
    roadmap += "  - Mitigation: Utilize open access repositories\n\n"
    
    roadmap += "## Expected Outcomes\n\n"
    roadmap += "- Comprehensive research paper\n"
    roadmap += "- Identification of research gaps\n"
    roadmap += "- Recommendations for future research\n"
    
    return roadmap

def save_roadmap(roadmap, problem_statement):
    """
    Save the generated roadmap to a markdown file in the research_results directory.
    
    Args:
        roadmap (str): The generated roadmap content
        problem_statement (str): The research problem statement
        
    Returns:
        str: Path to the saved roadmap file
    """
    try:
        # Create the research_results directory if it doesn't exist
        results_dir = os.path.join(os.getcwd(), "research_results")
        os.makedirs(results_dir, exist_ok=True)
        
        # Create a filename based on the problem statement
        filename = "roadmap.md"
        filepath = os.path.join(results_dir, filename)
        
        # Save the roadmap to the file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(roadmap)
        
        logger.info(f"Roadmap saved to {filepath}")
        return filepath
    
    except Exception as e:
        logger.error(f"Error saving roadmap: {str(e)}")
        return None
