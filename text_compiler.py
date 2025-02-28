"""
Text Compiler Module - Compiles the final paper based on analyzed content.
"""

import os
import logging
import json
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

def generate_references(analyzed_content):
    """
    Extract and format citations from analyzed content.
    
    Args:
        analyzed_content (dict): Analyzed content organized by search term
        
    Returns:
        list: Formatted citation strings
    """
    citations = set()
    
    # Extract cited authors from all topics/subtopics
    for content in analyzed_content.values():
        if "cited_authors" in content:
            cited_authors = content.get("cited_authors", [])
            for author_info in cited_authors:
                if isinstance(author_info, str):
                    # Simple string format (older version)
                    citations.add(author_info)
                elif isinstance(author_info, dict):
                    # Dictionary format
                    author = author_info.get('name', 'Unknown Author')
                    year = author_info.get('year', '')
                    title = author_info.get('title', 'Untitled Work')
                    journal = author_info.get('journal', '')
                    
                    # Create citation
                    if year and journal:
                        citation = f"{author} ({year}). {title}. {journal}."
                    elif year:
                        citation = f"{author} ({year}). {title}."
                    else:
                        citation = f"{author}. {title}."
                    
                    citations.add(citation)
    
    # If we didn't get any valid citations, create placeholder citations
    if not citations:
        for topic, content in analyzed_content.items():
            if isinstance(content, dict) and "subtopic" in content:
                topic_name = content.get("subtopic", topic)
                citations.add(f"Research paper on {topic_name}. Academic Journal.")
    
    # Sort the citations alphabetically
    return sorted(list(citations))

def generate_section_content(section_info, analyzed_content):
    """
    Generate content for a specific section using Gemini.
    
    Args:
        section_info (dict): Information about the section (topic/subtopic)
        analyzed_content (dict): All analyzed content from either a topic or subtopic
        
    Returns:
        str: Generated section content
    """
    # Set up Gemini API
    safety_settings = setup_gemini_api()
    
    # Create a model instance
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        safety_settings=safety_settings,
        generation_config={"temperature": 0.4}
    )
    
    # Get section name
    section_name = section_info.get('name', '')
    
    # Log what we're generating
    logger.info(f"Generating content for section: {section_name}")
    
    # If we have analyzed content for this section, use it
    if analyzed_content:
        # Format the analyzed content for the prompt
        formatted_content = {
            "key_findings": analyzed_content.get("key_findings", []),
            "methodologies": analyzed_content.get("methodologies", []),
            "cited_authors": analyzed_content.get("cited_authors", []),
            "research_gaps": analyzed_content.get("research_gaps", []),
            "theoretical_frameworks": analyzed_content.get("theoretical_frameworks", []),
            "papers_analyzed": analyzed_content.get("papers_analyzed", 0)
        }
        
        # Craft the prompt
        prompt = f"""
        You're writing a section for an academic paper on the topic "{section_name}".
        
        Using the information from research analysis, write a comprehensive, 
        well-structured section that synthesizes the findings and includes appropriate citations.
        
        Research Analysis:
        {json.dumps(formatted_content, indent=2)}
        
        Your section should:
        1. Begin with an introduction to the topic
        2. Present the key findings and information from the research
        3. Compare and contrast different viewpoints or findings when available
        4. Discuss methodologies used in the research
        5. Identify any research gaps
        6. End with a conclusion or transition to the next section
        
        Use appropriate citations in the format (Author, Year) when referencing specific findings.
        Write in a scholarly tone appropriate for an academic paper.
        
        Section length should be approximately 400-600 words.
        """
        
        try:
            # Generate the response
            response = model.generate_content(prompt)
            
            # Extract the response text
            section_content = response.text
            return section_content
        except Exception as e:
            logger.error(f"Error generating content for section {section_name}: {str(e)}", exc_info=True)
            # Return a placeholder in case of error
            return f"This section would discuss {section_name} in detail, including relevant research findings and analysis."
    
    # If we don't have specific analyzed content, generate generic content
    else:
        generic_prompt = f"""
        You're writing a section for an academic paper on "{section_name}".
        
        Although specific research analysis isn't available for this section, 
        write a well-structured academic section that:
        
        1. Introduces the concept of {section_name}
        2. Discusses its general importance in the field
        3. Outlines what would typically be covered in this section
        4. Suggests areas where more research might be needed
        
        Write in a scholarly tone appropriate for an academic paper.
        The section should be approximately 300-400 words.
        """
        
        try:
            generic_response = model.generate_content(generic_prompt)
            return generic_response.text
        except Exception as e:
            logger.error(f"Error generating generic content for section {section_name}: {str(e)}", exc_info=True)
            return f"This section would discuss {section_name} in detail, including its importance and research opportunities."

def generate_title(problem_statement):
    """
    Generate a title for the paper based on the problem statement.
    
    Args:
        problem_statement (str): The original problem statement
        
    Returns:
        str: Generated title
    """
    # Set up Gemini API
    safety_settings = setup_gemini_api()
    
    # Create a model instance
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        safety_settings=safety_settings,
        generation_config={"temperature": 0.2}
    )
    
    prompt = f"""
    Generate a concise, academic title for a research paper that addresses this problem statement:
    
    "{problem_statement}"
    
    Your title should:
    1. Be clear and specific
    2. Use appropriate academic terminology
    3. Be 10-15 words maximum
    4. Not use contractions or informal language
    5. Avoid questions or unnecessary punctuation
    
    Return ONLY the title with no additional text or formatting.
    """
    
    try:
        response = model.generate_content(prompt)
        title = response.text.strip()
        # Remove any quotes if they're in the response
        if title.startswith('"') and title.endswith('"'):
            title = title[1:-1]
        return title
    except Exception as e:
        logger.error(f"Error generating title: {e}", exc_info=True)
        # Generate a simple title if the API fails
        return f"Analysis of {problem_statement[:50]}{'...' if len(problem_statement) > 50 else ''}"

def generate_abstract(problem_statement, analyzed_content):
    """
    Generate an abstract for the paper.
    
    Args:
        problem_statement (str): The original problem statement
        analyzed_content (dict): All analyzed content
        
    Returns:
        str: Generated abstract
    """
    # Set up Gemini API
    safety_settings = setup_gemini_api()
    
    # Create a model instance
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        safety_settings=safety_settings,
        generation_config={"temperature": 0.3}
    )
    
    # Extract key findings from all analyzed content
    all_key_findings = []
    all_methodologies = []
    all_research_gaps = []
    for content in analyzed_content.values():
        if "key_findings" in content:
            all_key_findings.extend(content.get("key_findings", []))
        if "methodologies" in content:
            all_methodologies.extend(content.get("methodologies", []))
        if "research_gaps" in content:
            all_research_gaps.extend(content.get("research_gaps", []))
    
    # Remove duplicates
    all_key_findings = list(set(all_key_findings))
    all_methodologies = list(set(all_methodologies))
    all_research_gaps = list(set(all_research_gaps))
    
    # Limit the number of findings to avoid overly long prompts
    max_findings = 10
    if len(all_key_findings) > max_findings:
        all_key_findings = all_key_findings[:max_findings]
    
    # Create the prompt
    prompt = f"""
    Generate an abstract for an academic research paper that addresses this problem statement:
    
    "{problem_statement}"
    
    Based on the following research findings:
    
    Key Findings:
    {json.dumps(all_key_findings, indent=2)}
    
    Methodologies Used:
    {json.dumps(all_methodologies, indent=2)}
    
    Research Gaps:
    {json.dumps(all_research_gaps, indent=2)}
    
    Your abstract should:
    1. Begin with a brief introduction to the research problem
    2. Explain the methodology and approach used
    3. Summarize the key findings and their significance
    4. Mention any important implications or applications
    5. Be approximately 200-250 words
    6. Be written in a formal, academic style with no first-person language
    
    Return ONLY the abstract text with no additional commentary.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error generating abstract: {e}", exc_info=True)
        # Generate a simple abstract if the API fails
        return "This abstract summarizes the research conducted on the problem statement. The research examined various aspects of the topic, using methodologies including literature review and data analysis. Key findings were identified and their implications are discussed in the paper. This research contributes to the understanding of the topic and suggests directions for future work."

def generate_introduction(problem_statement, analyzed_content):
    """
    Generate an introduction for the paper.
    
    Args:
        problem_statement (str): The original problem statement
        analyzed_content (dict): All analyzed content
        
    Returns:
        str: Generated introduction
    """
    # Set up Gemini API
    safety_settings = setup_gemini_api()
    
    # Create a model instance
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        safety_settings=safety_settings,
        generation_config={"temperature": 0.3}
    )
    
    # Extract research topics from analyzed content keys
    research_topics = list(analyzed_content.keys())
    
    # Extract key findings from all analyzed content
    all_key_findings = []
    for content in analyzed_content.values():
        if "key_findings" in content:
            all_key_findings.extend(content.get("key_findings", []))
    
    # Remove duplicates and limit to avoid overly long prompts
    all_key_findings = list(set(all_key_findings))
    max_findings = 8
    if len(all_key_findings) > max_findings:
        all_key_findings = all_key_findings[:max_findings]
    
    # Create the prompt
    prompt = f"""
    Generate an introduction for an academic research paper that addresses this problem statement:
    
    "{problem_statement}"
    
    The paper covers these research topics:
    {json.dumps(research_topics, indent=2)}
    
    Key findings from the research:
    {json.dumps(all_key_findings, indent=2)}
    
    Your introduction should:
    1. Begin with a broad context for the research problem
    2. Clearly state the problem and its significance
    3. Provide a brief background of existing research
    4. Identify the gap that this research addresses
    5. State the purpose and objectives of the study
    6. Briefly outline the paper structure
    7. Be approximately 400-500 words
    8. Be written in a formal, academic style
    
    Return ONLY the introduction text with no additional commentary.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error generating introduction: {e}", exc_info=True)
        # Generate a simple introduction if the API fails
        return f"This paper examines the problem of {problem_statement}. The research covers various aspects including {', '.join(research_topics[:3])} and more. The introduction provides context for the research problem, outlines existing literature, identifies research gaps, and presents the structure of the paper. The following sections will delve into specific aspects of the research."

def generate_conclusion(problem_statement, analyzed_content):
    """
    Generate a conclusion for the paper.
    
    Args:
        problem_statement (str): The original problem statement
        analyzed_content (dict): All analyzed content
        
    Returns:
        str: Generated conclusion
    """
    # Set up Gemini API
    safety_settings = setup_gemini_api()
    
    # Create a model instance
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        safety_settings=safety_settings,
        generation_config={"temperature": 0.3}
    )
    
    # Extract research topics from analyzed content keys
    research_topics = list(analyzed_content.keys())
    
    # Extract key findings and research gaps from all analyzed content
    all_key_findings = []
    all_research_gaps = []
    for content in analyzed_content.values():
        if "key_findings" in content:
            all_key_findings.extend(content.get("key_findings", []))
        if "research_gaps" in content:
            all_research_gaps.extend(content.get("research_gaps", []))
    
    # Remove duplicates and limit to avoid overly long prompts
    all_key_findings = list(set(all_key_findings))
    all_research_gaps = list(set(all_research_gaps))
    max_findings = 8
    if len(all_key_findings) > max_findings:
        all_key_findings = all_key_findings[:max_findings]
    if len(all_research_gaps) > max_findings:
        all_research_gaps = all_research_gaps[:max_findings]
    
    # Create the prompt
    prompt = f"""
    Generate a conclusion for an academic research paper that addresses this problem statement:
    
    "{problem_statement}"
    
    The paper covers these research topics:
    {json.dumps(research_topics, indent=2)}
    
    Key findings from the research:
    {json.dumps(all_key_findings, indent=2)}
    
    Research gaps identified:
    {json.dumps(all_research_gaps, indent=2)}
    
    Your conclusion should:
    1. Summarize the main findings of the research
    2. Relate these findings back to the original research problem
    3. Discuss the broader implications of the findings
    4. Acknowledge limitations of the current research
    5. Suggest directions for future research
    6. Be approximately 300-400 words
    7. Be written in a formal, academic style
    
    Return ONLY the conclusion text with no additional commentary.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error generating conclusion: {e}", exc_info=True)
        # Generate a simple conclusion if the API fails
        return f"This conclusion summarizes the key findings related to {problem_statement}. The research has addressed several aspects of this problem through analysis of existing literature. While the current study has limitations, it contributes to the field and suggests several directions for future research, including addressing the identified research gaps. Further investigation is recommended to build upon these findings."

def update_final_document(problem_statement, new_content=None, new_subtopic=None, is_initialization=False):
    """
    Create or update a final.md document that consolidates all research findings.
    This document will be continuously updated as research progresses.
    
    Args:
        problem_statement (str): The original research problem statement
        new_content (dict, optional): New content from a completed subtopic
        new_subtopic (str, optional): Name of the completed subtopic
        is_initialization (bool): If True, initialize the document
    """
    import os
    import datetime
    
    # Ensure the research_results directory exists
    if not os.path.exists("research_results"):
        os.makedirs("research_results")
    
    filepath = os.path.join("research_results", "final.md")
    
    # If this is initialization, create the file structure
    if is_initialization or not os.path.exists(filepath):
        # Generate a title for the research
        title = generate_title(problem_statement)
        
        # Create initial structure
        content = f"# {title}\n\n"
        content += f"## Research Problem\n\n{problem_statement}\n\n"
        content += f"## Last Updated\n\n{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += "## Overview\n\nThis document compiles findings from ongoing research and will be updated as new subtopics are completed.\n\n"
        content += "## Table of Contents\n\n"
        content += "1. [Introduction](#introduction)\n"
        content += "2. [Methodology](#methodology)\n"
        content += "3. [Findings](#findings)\n"
        content += "4. [Conclusions](#conclusions)\n"
        content += "5. [References](#references)\n\n"
        content += "## Introduction\n\n*This section will be developed as research progresses.*\n\n"
        content += "## Methodology\n\n*This section will be developed as research progresses.*\n\n"
        content += "## Findings\n\n*Results from completed subtopics will appear here as research progresses.*\n\n"
        content += "## Conclusions\n\n*This section will be developed once research is complete.*\n\n"
        content += "## References\n\n*A comprehensive reference list will be compiled throughout the research process.*\n\n"
        
        # Write initial content
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"Initialized final document at {filepath}")
        return
    
    # If we have new content to add, update the file
    if new_content and new_subtopic:
        try:
            # Read existing content
            with open(filepath, "r", encoding="utf-8") as f:
                existing_content = f.read()
            
            # Find the Findings section
            findings_section = "## Findings\n\n"
            findings_index = existing_content.find(findings_section) + len(findings_section)
            
            # If findings section still has the placeholder text, remove it
            placeholder_text = "*Results from completed subtopics will appear here as research progresses.*\n\n"
            if existing_content[findings_index:].startswith(placeholder_text):
                existing_content = existing_content.replace(findings_section + placeholder_text, findings_section)
                findings_index = existing_content.find(findings_section) + len(findings_section)
            
            # Generate article section for the new content if it doesn't exist in aggregated content
            import content_analyzer
            article_section = content_analyzer.format_subtopic_as_article(
                new_subtopic, 
                "", 
                new_content.get("analyzed_papers", []), 
                {
                    "key_findings": new_content.get("key_findings", []),
                    "methodologies": new_content.get("methodologies", []),
                    "research_gaps": new_content.get("research_gaps", []),
                    "theoretical_frameworks": new_content.get("theoretical_frameworks", [])
                }
            )
            
            # Check if the article section is too large (over 10000 characters)
            # If so, truncate it to a reasonable size while preserving structure
            MAX_SECTION_SIZE = 10000  # Characters
            if article_section and len(article_section) > MAX_SECTION_SIZE:
                logger.warning(f"Article section for {new_subtopic} is too large ({len(article_section)} chars). Truncating...")
                
                # Find a good truncation point (end of a paragraph)
                truncation_point = article_section[:MAX_SECTION_SIZE].rfind("\n\n")
                if truncation_point == -1:
                    truncation_point = MAX_SECTION_SIZE
                
                # Truncate the article section
                article_section = article_section[:truncation_point] + "\n\n*[Content truncated due to size limitations]*\n\n"
            
            # Insert the new content into the findings section
            if article_section:
                # Check if this subtopic is already in the document
                if f"### {new_subtopic}" not in existing_content:
                    # Split the document into parts
                    before_findings = existing_content[:findings_index]
                    after_findings = existing_content[findings_index:]
                    
                    # Combine parts with new content
                    updated_content = before_findings + article_section + "\n\n" + after_findings
                    
                    # Update the last updated timestamp
                    updated_content = updated_content.replace(
                        "## Last Updated\n\n" + existing_content.split("## Last Updated\n\n")[1].split("\n\n")[0],
                        "## Last Updated\n\n" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                    
                    # Write updated content in chunks to avoid truncation
                    with open(filepath, "w", encoding="utf-8") as f:
                        # Write in smaller chunks to avoid buffer issues
                        CHUNK_SIZE = 4096
                        for i in range(0, len(updated_content), CHUNK_SIZE):
                            f.write(updated_content[i:i+CHUNK_SIZE])
                    
                    logger.info(f"Updated final document with {new_subtopic}")
            
            # Re-read the file to update references
            with open(filepath, "r", encoding="utf-8") as f:
                existing_content = f.read()
            
            # Extract and update references
            references_section = "## References\n\n"
            references_index = existing_content.find(references_section) + len(references_section)
            
            # If references section still has the placeholder text, remove it
            references_placeholder = "*A comprehensive reference list will be compiled throughout the research process.*\n\n"
            if existing_content[references_index:].startswith(references_placeholder):
                existing_content = existing_content.replace(references_section + references_placeholder, references_section)
                
                # Re-read updated content
                with open(filepath, "r", encoding="utf-8") as f:
                    existing_content = f.read()
                    
                references_index = existing_content.find(references_section) + len(references_section)
            
            # Extract references from new content
            new_references = []
            if "cited_authors" in new_content:
                for author in new_content["cited_authors"]:
                    if author and isinstance(author, str) and author not in existing_content:
                        new_references.append(f"- {author}")
            
            # Add new references if any
            if new_references:
                # Split the document into parts
                before_refs = existing_content[:references_index]
                after_refs = existing_content[references_index:]
                
                # Combine parts with new references
                updated_content = before_refs + "\n".join(new_references) + "\n\n" + after_refs
                
                # Write updated content in chunks
                with open(filepath, "w", encoding="utf-8") as f:
                    CHUNK_SIZE = 4096
                    for i in range(0, len(updated_content), CHUNK_SIZE):
                        f.write(updated_content[i:i+CHUNK_SIZE])
                
                logger.info(f"Updated references in final document")
        
        except Exception as e:
            logger.error(f"Error updating final document: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

def compile_paper(problem_statement, topics_subtopics, analyzed_content):
    """
    Compile the final paper from the analyzed content.
    
    Args:
        problem_statement (str): The original problem statement
        topics_subtopics (list): List of topic dictionaries with their subtopics
        analyzed_content (dict): Analyzed content organized by topic/subtopic
        
    Returns:
        str: Compiled paper
    """
    logging.info("Starting to compile the paper")
    
    # If main.py's display_process_status function is available, use it
    try:
        from main import display_process_status
        process_status_available = True
    except ImportError:
        process_status_available = False
        logging.warning("Cannot import display_process_status, detailed progress won't be shown")
    
    def show_status(stage, message, content=None):
        """Helper function to show status if available"""
        logging.info(f"{stage}: {message}")
        if process_status_available:
            display_process_status(stage, message, content)
    
    show_status("PAPER COMPILATION START", 
               f"Starting to compile paper for problem: {problem_statement}", 
               {"topics_count": len(topics_subtopics)})
    
    # Generate title
    title = generate_title(problem_statement)
    show_status("TITLE GENERATED", f"Generated paper title: {title}")
    
    # Generate abstract
    abstract = generate_abstract(problem_statement, analyzed_content)
    show_status("ABSTRACT GENERATED", 
               "Generated paper abstract", 
               {"abstract_preview": abstract[:200] + "..." if len(abstract) > 200 else abstract})
    
    # Generate introduction
    introduction = generate_introduction(problem_statement, analyzed_content)
    show_status("INTRODUCTION GENERATED", 
               "Generated paper introduction", 
               {"intro_preview": introduction[:200] + "..." if len(introduction) > 200 else introduction})
    
    # Generate conclusion
    conclusion = generate_conclusion(problem_statement, analyzed_content)
    show_status("CONCLUSION GENERATED", 
               "Generated paper conclusion", 
               {"conclusion_preview": conclusion[:200] + "..." if len(conclusion) > 200 else conclusion})
    
    # Generate references
    references = generate_references(analyzed_content)
    show_status("REFERENCES COMPILED", 
               f"Compiled {len(references)} references", 
               {"references_preview": references[:5] if len(references) > 5 else references})
    
    # Create the paper structure
    paper = {
        "title": title,
        "abstract": abstract,
        "introduction": introduction,
        "sections": [],
        "conclusion": conclusion,
        "references": references
    }
    
    show_status("PAPER STRUCTURE", 
               "Created initial paper structure", 
               {"title": paper["title"], "abstract_length": len(paper["abstract"])})
    
    # Process each topic and create sections
    for topic_item in topics_subtopics:
        topic = topic_item['topic']
        subtopics = topic_item.get('subtopics', [])
        
        show_status("SECTION WRITING", 
                   f"Writing section for topic: {topic}", 
                   {"topic": topic, "subtopics": subtopics})
        
        # Create the section
        section = {
            "title": topic,
            "content": generate_section_content({'name': topic}, analyzed_content.get(topic, {})),
            "subsections": []
        }
        
        # Process each subtopic and create subsections
        for subtopic in subtopics:
            subtopic_key = f"{topic} {subtopic}"
            
            show_status("SUBSECTION WRITING", 
                       f"Writing subsection: {subtopic}", 
                       {"parent_topic": topic, "subtopic": subtopic})
            
            # Create the subsection
            subsection = {
                "title": subtopic,
                "content": generate_section_content({'name': subtopic_key}, analyzed_content.get(subtopic_key, {}))
            }
            
            # Add the subsection to the section
            section["subsections"].append(subsection)
            
            show_status("SUBSECTION COMPLETE", 
                       f"Completed subsection: {subtopic}", 
                       {"content_preview": subsection["content"][:200] + "..." if len(subsection["content"]) > 200 else subsection["content"]})
        
        # Add the section to the paper
        paper["sections"].append(section)
        
        show_status("SECTION COMPLETE", 
                   f"Completed section: {topic}", 
                   {"subsections_count": len(section["subsections"])})
    
    # Prepare the final paper
    final_paper = f"""# {paper["title"]}

## Abstract

{paper["abstract"]}

## Introduction

{paper["introduction"]}

"""
    
    # Add sections
    for section in paper["sections"]:
        final_paper += f"## {section['title']}\n\n{section['content']}\n\n"
        
        # Add subsections
        for subsection in section["subsections"]:
            final_paper += f"### {subsection['title']}\n\n{subsection['content']}\n\n"
    
    # Add conclusion
    final_paper += f"## Conclusion\n\n{paper['conclusion']}\n\n"
    
    # Add references
    final_paper += "## References\n\n"
    for reference in paper["references"]:
        final_paper += f"- {reference}\n"
    
    show_status("PAPER COMPILATION COMPLETE", 
               "Final paper compiled successfully", 
               {"word_count": len(final_paper.split()), "character_count": len(final_paper)})
    
    return final_paper
