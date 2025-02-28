"""
Content Analyzer Module - Analyzes and extracts information from academic papers.
"""

import os
import logging
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import re
import random

logger = logging.getLogger(__name__)

def setup_gemini_api():
    """Set up the Gemini API with safety settings."""
    try:
        # Configure the Python client to use your API key
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            logging.error("GOOGLE_API_KEY not found in environment variables")
            return None
            
        genai.configure(api_key=api_key)
        
        # Define safety settings - be permissive for academic content while blocking harmful content
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
        
        return safety_settings
        
    except Exception as e:
        logging.error(f"Error setting up Gemini API: {str(e)}")
        return None

def extract_paper_information(paper_result):
    """
    Extract structured information from a paper search result using Gemini.
    
    Args:
        paper_result (dict): Paper information with title, snippet, etc.
        
    Returns:
        dict: Structured information extracted from the paper
    """
    # Set up Gemini API
    safety_settings = setup_gemini_api()
    
    # Create a model instance
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        safety_settings=safety_settings,
        generation_config={"temperature": 0.2}
    )
    
    # Try to import display_process_status from main, if available
    try:
        from main import display_process_status
        process_status_available = True
    except ImportError:
        process_status_available = False
    
    # Helper function to show progress
    def show_status(stage, message, content=None):
        logger.info(f"{stage}: {message}")
        if process_status_available:
            display_process_status(stage, message, content)
    
    # Extract available information
    title = paper_result.get('title', 'Unknown Title')
    snippet = paper_result.get('snippet', '')
    raw_authors = paper_result.get('authors', [])
    authors = clean_authors(raw_authors)
    year = paper_result.get('year', '')
    url = paper_result.get('url', '')
    citations = paper_result.get('citations', '')
    journal = paper_result.get('journal', 'Unknown')
    is_mock = paper_result.get('is_mock', False)
    
    show_status("PAPER ANALYSIS START", 
               f"Analyzing paper: {title}", 
               paper_result)
    
    # Check if we have enough information to analyze
    if not title and not snippet:
        show_status("ANALYSIS ERROR", 
                   "Insufficient information to analyze paper", 
                   paper_result)
        return None
    
    # Special handling for mock results - generate realistic analysis without API call
    if is_mock:
        logger.info("Processing mock paper result")
        mock_findings = [
            f"The study found significant patterns related to {title.lower().replace('advances in ', '').replace('applications of ', '').replace('theoretical foundations of ', '')}.",
            f"Research shows a {random.choice(['positive', 'negative', 'neutral', 'complex'])} relationship between key variables in {title.split(':')[0]}.",
            f"Analysis reveals important implications for future work in this field.",
            f"The paper identifies several {random.choice(['challenges', 'opportunities', 'methodologies', 'frameworks'])} that warrant further investigation."
        ]
        
        mock_methods = random.choice([
            "Mixed methods approach",
            "Quantitative analysis",
            "Qualitative case study",
            "Literature review",
            "Experimental design",
            "Comparative analysis",
            "Longitudinal study",
            "Cross-sectional survey",
            "Meta-analysis",
            "Theoretical modeling"
        ])
        
        mock_framework = random.choice([
            "Systems Theory",
            "Cognitive Framework",
            "Social Learning Theory",
            "Technological Acceptance Model",
            "Complexity Theory",
            "Grounded Theory",
            "Activity Theory",
            "Game Theory",
            "Actor-Network Theory",
            "Critical Theory"
        ])
        
        mock_gaps = [
            f"Limited research on long-term effects of {title.split(':')[0].lower()}",
            f"Need for more diverse geographical contexts in studies of {title.split(':')[0].lower()}",
            f"Lack of standardized measurement tools in this research area"
        ]
        
        return {
            'title': title,
            'authors': authors,
            'year': year,
            'snippet': snippet,
            'url': url,
            'citations': citations,
            'journal': journal,
            'key_findings': random.sample(mock_findings, k=min(3, len(mock_findings))),
            'methodology': mock_methods,
            'theoretical_framework': mock_framework,
            'research_gaps': random.sample(mock_gaps, k=min(2, len(mock_gaps))),
            'cited_authors': [],
            'keywords': [word for word in title.replace(':', ' ').split() if len(word) > 3][:5]
        }
    
    # Create prompt for Gemini
    prompt = f"""
    Extract structured information from this academic paper result:
    
    Title: {title}
    {'Authors: ' + authors if authors else ''}
    {'Year: ' + str(year) if year else ''}
    {'URL: ' + url if url else ''}
    {'Citations: ' + str(citations) if citations else ''}
    Snippet/Abstract: {snippet}
    
    Extract and format the following information as a JSON object:
    1. key_findings: List the main findings or conclusions (up to 5 points)
    2. methodology: Describe the research method used. Return as a string or a list of methodologies.
    3. theoretical_framework: Identify any theoretical framework mentioned. Return as a string or a list.
    4. research_gaps: Identify any gaps in research that are mentioned. Return an empty list if none are found. Never write "Unknown" as a research gap.
    5. cited_authors: List any significant authors cited in the work as full names, not as individual letters.
    6. journal: Identify the journal or publication venue if mentioned.
    7. keywords: Extract any keywords that represent the main topics.
    
    For each field, if the information is not available, provide an empty list or "Unknown".
    Never break author names or any other text into individual letters. Always provide full words and names.
    
    Return ONLY a JSON object with these fields, nothing else.
    """
    
    try:
        # Generate the response
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Process the response to extract the JSON part
        import json
        import re
        
        # Try to extract JSON pattern if present
        json_pattern = r'\{[\s\S]*\}'
        json_match = re.search(json_pattern, response_text)
        
        if json_match:
            json_str = json_match.group(0)
            try:
                extracted_info = json.loads(json_str)
                # Add paper metadata
                extracted_info['title'] = title
                extracted_info['authors'] = authors
                extracted_info['year'] = year
                extracted_info['snippet'] = snippet
                extracted_info['url'] = url
                extracted_info['citations'] = citations
                extracted_info['journal'] = journal or extracted_info.get('journal', 'Unknown')
                
                # Clean up cited_authors to ensure they're not broken into individual letters
                if 'cited_authors' in extracted_info and extracted_info['cited_authors']:
                    if isinstance(extracted_info['cited_authors'], list):
                        extracted_info['cited_authors'] = [author for author in extracted_info['cited_authors'] if author and isinstance(author, str) and len(author) > 2]
                
                # Fix research gaps
                if 'research_gaps' in extracted_info:
                    extracted_info['research_gaps'] = fix_research_gaps(extracted_info['research_gaps'])
                
                show_status("PAPER ANALYSIS COMPLETE", 
                           f"Successfully extracted information from: {title}", 
                           {"key_findings": extracted_info.get('key_findings', [])})
                
                return extracted_info
            except json.JSONDecodeError:
                logger.warning("Failed to decode JSON from response")
        
        # Fallback: Generate reasonable defaults when JSON parsing fails
        show_status("PAPER ANALYSIS ISSUE", 
                   "Using fallback extraction method", 
                   {"response_text": response_text[:100] + "..."})
                   
        # Extract title words to use as keywords
        keywords = [word for word in title.replace(':', ' ').split() if len(word) > 3][:5]
        
        # Create basic findings based on title
        base_topic = title.split(':')[0] if ':' in title else title
        fallback_findings = [
            f"The paper examines key aspects of {base_topic}.",
            f"Research suggests important relationships within {base_topic}.",
            f"The study highlights significant developments in this field."
        ]
        
        fallback_result = {
            'title': title,
            'authors': authors,
            'year': year,
            'snippet': snippet,
            'url': url,
            'citations': citations,
            'journal': journal,
            'key_findings': fallback_findings,
            'methodology': "Not explicitly identified in abstract",
            'theoretical_framework': "Not explicitly identified in abstract",
            'research_gaps': [f"Further research needed on {base_topic}"],
            'cited_authors': [],
            'keywords': keywords
        }
        
        # Extract potential findings from response text if possible
        findings_match = re.search(r'key_findings["\s:]+\[(.*?)\]', response_text, re.DOTALL)
        if findings_match:
            findings_text = findings_match.group(1)
            # Extract items between quotes
            findings = re.findall(r'"([^"]*)"', findings_text)
            if findings:
                fallback_result['key_findings'] = findings
        
        show_status("PAPER ANALYSIS COMPLETE", 
                   f"Completed fallback extraction for: {title}", 
                   {"key_findings_count": len(fallback_result['key_findings'])})
        
        return fallback_result
        
    except Exception as e:
        logger.error(f"Error analyzing paper '{title}': {str(e)}", exc_info=True)
        
        show_status("PAPER ANALYSIS ERROR", 
                   f"Error analyzing paper: {title}", 
                   {"error": str(e)})
        
        # Generate basic paper information even when analysis fails
        base_topic = title.split(':')[0] if ':' in title else title
        keywords = [word for word in title.replace(':', ' ').split() if len(word) > 3][:5]
        
        # Return basic information we have
        return {
            'title': title,
            'authors': authors,
            'year': year,
            'snippet': snippet,
            'key_findings': [
                f"The paper discusses {base_topic}.",
                "Information could not be fully extracted due to an error."
            ],
            'methodology': "Not extracted due to an error",
            'theoretical_framework': "Not extracted due to an error",
            'research_gaps': [f"Further research needed on {base_topic}"],
            'cited_authors': [],
            'journal': journal,
            'keywords': keywords
        }

def clean_authors(author_list):
    if not author_list:
        return "Unknown"
        
    # If it's already a string, process it
    if isinstance(author_list, str):
        # Check if the string is just ellipses or similar
        if author_list.strip() in ["...", "…"] or len(author_list.strip()) <= 3:
            return "Author information incomplete"
                
        # Check if it's a series of single characters separated by commas
        if re.search(r'^([A-Za-z],\s*)+[A-Za-z]$', author_list) or all(len(c.strip(',')) <= 1 for c in author_list.split()):
            # Join the characters without commas and spaces
            return "".join(c for c in author_list if c not in [',', ' '] and not c.isspace())
                
        return author_list
            
    # Join the list properly
    if isinstance(author_list, list):
        # Handle cases where the list is empty or has only empty elements
        if not author_list or all(not a for a in author_list):
            return "Unknown"
                
        # If the list contains single characters, join them without spaces
        if all(isinstance(a, str) and len(a.strip()) <= 1 for a in author_list):
            joined = "".join(a for a in author_list if a and not a.isspace())
            if not joined:
                return "Unknown"
            return joined
                
        # Otherwise, use proper formatting
        proper_authors = []
        for author in author_list:
            # Check if author name is broken into characters or is a punctuation mark
            if isinstance(author, str) and (len(author.strip()) <= 1 and author.strip() in [',', ' ', '-', '.'] or not author.strip()):
                continue
            if isinstance(author, str) and author.strip():
                proper_authors.append(author.strip())
            
        if not proper_authors:
            return "Unknown"
        return ", ".join(proper_authors)
        
    return "Unknown"
        
def fix_research_gaps(gaps):
    if not gaps:
        return []
            
    # If it's a string, check if it's just "Unknown"
    if isinstance(gaps, str):
        if gaps.strip().lower() == "unknown":
            return []
        return [gaps]
            
    # If it's a list of single characters, join them
    if isinstance(gaps, list):
        # Check if the list items are single characters (possibly spelling "unknown")
        if all(isinstance(g, str) and len(g) == 1 for g in gaps):
            joined = "".join(gaps).strip().lower()
            if joined == "unknown":
                return []
            return [joined]
                
        # Otherwise, filter out empty or "unknown" entries
        return [gap for gap in gaps if gap and isinstance(gap, str) and gap.strip().lower() != "unknown"]
            
    return []

def identify_new_topics(analyzed_papers, original_topics):
    """
    Identify potential new topics based on the analyzed papers
    
    Args:
        analyzed_papers (list): List of papers with their analyses
        original_topics (list): List of existing topics/subtopics
        
    Returns:
        list: List of potential new topics
    """
    # Try to import display_process_status from main, if available
    try:
        from main import display_process_status
        process_status_available = True
    except ImportError:
        process_status_available = False
        
    def show_status(stage, message, content=None):
        """Helper function to show status if available"""
        logging.info(f"{stage}: {message}")
        if process_status_available:
            display_process_status(stage, message, content)
    
    show_status("NEW TOPICS IDENTIFICATION", 
              f"Starting analysis of {len(analyzed_papers)} papers to identify new topics", 
              {"original_topics_count": len(original_topics)})
    
    if not analyzed_papers:
        show_status("TOPIC IDENTIFICATION COMPLETE", 
                  "No papers to analyze for new topics", 
                  {"new_topics_count": 0})
        return []
    
    # Extract existing topics from the original structure
    existing_topics = []
    for topic_dict in original_topics:
        existing_topics.append(topic_dict["topic"])
        if "subtopics" in topic_dict:
            existing_topics.extend(topic_dict["subtopics"])
    
    show_status("EXISTING TOPICS", 
               f"Found {len(existing_topics)} existing topics and subtopics", 
               {"existing_topics": existing_topics})
    
    # Set up Gemini API
    safety_settings = setup_gemini_api()
    if not safety_settings:
        show_status("API ERROR", 
                   "Could not set up Gemini API for new topic identification", 
                   {"error": "API setup failed"})
        return []

    # Collect key findings from all papers
    all_findings = []
    for paper in analyzed_papers:
        # Check if paper is a dictionary and has key_findings
        if isinstance(paper, dict) and 'key_findings' in paper:
            findings = paper['key_findings']
            if isinstance(findings, list):
                all_findings.extend(findings)
            elif isinstance(findings, str):
                all_findings.append(findings)
        # Handle case where paper might be a string
        elif isinstance(paper, str):
            all_findings.append(f"Finding from paper: {paper}")
    
    # If too many findings, sample a representative subset to stay within token limits
    if len(all_findings) > 20:
        import random
        random.shuffle(all_findings)
        all_findings = all_findings[:20]
    
    show_status("ANALYZING FINDINGS", 
               f"Analyzing {len(all_findings)} key findings to identify new topics", 
               {"finding_samples": all_findings[:3]})
    
    # Create prompt for Gemini to identify new topics
    prompt = f"""
    Based on the following key findings from academic papers, identify 2-3 potential new research topics.
    
    Key findings from papers:
    {all_findings}
    
    Current research topics:
    {existing_topics}
    
    Identify 2-3 NEW potential research topics that are:
    1. Relevant to the existing topics but not duplicative
    2. Supported by the key findings
    3. Specific enough to be researched
    
    For each new topic, provide:
    1. The topic name
    2. 2-3 potential subtopics
    3. Brief justification based on the findings
    
    Return your response as a JSON list of objects with these fields:
    - topic: string
    - subtopics: list of strings
    - justification: string
    """
    
    try:
        # Generate the response
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            safety_settings=safety_settings,
            generation_config={"temperature": 0.2}
        )
        response = model.generate_content(prompt)
        
        # Process the response to extract JSON
        import json
        import re
        
        # Try to extract JSON pattern
        json_pattern = r'\[\s*\{.*\}\s*\]'
        json_match = re.search(json_pattern, response.text, re.DOTALL)
        
        new_topics = []
        
        if json_match:
            json_str = json_match.group(0)
            try:
                new_topics = json.loads(json_str)
                
                show_status("NEW TOPICS IDENTIFIED", 
                           f"Successfully identified {len(new_topics)} new research topics", 
                           {"new_topics": new_topics})
                
                return new_topics
            except json.JSONDecodeError:
                logging.warning("Failed to parse JSON response for new topics")
        
        # Fallback: manual extraction
        show_status("TOPIC EXTRACTION FALLBACK", 
                   "Using manual extraction for new topics", 
                   {"response_text": response.text[:200]})
        
        # Try to extract topics manually using regex
        topic_pattern = r'(?:Topic|New Topic)[^\w\n]*(\w[^:\n]*)'
        subtopic_pattern = r'Subtopics?[^\w\n]*(.+?)(?:\n\d\.|\n\n|$)'
        
        topics = re.findall(topic_pattern, response.text)
        
        for topic in topics:
            topic_clean = topic.strip()
            
            # Skip if this is an existing topic
            if any(existing.lower() == topic_clean.lower() for existing in existing_topics):
                continue
                
            # Try to find subtopics for this topic
            topic_section = response.text.split(topic)[1].split("Topic")[0] if "Topic" in response.text.split(topic)[1] else response.text.split(topic)[1]
            subtopics_match = re.search(subtopic_pattern, topic_section, re.DOTALL)
            
            subtopics = []
            if subtopics_match:
                subtopics_text = subtopics_match.group(1)
                subtopics = [s.strip() for s in re.findall(r'\d\.\s*([^:\n]+)', subtopics_text)]
            
            new_topics.append({
                "topic": topic_clean,
                "subtopics": subtopics,
                "justification": "Identified from paper findings"
            })
        
        show_status("NEW TOPICS IDENTIFIED", 
                   f"Identified {len(new_topics)} new research topics via fallback method", 
                   {"new_topics": new_topics})
        
        return new_topics
        
    except Exception as e:
        logging.error(f"Error identifying new topics: {str(e)}", exc_info=True)
        
        show_status("TOPIC IDENTIFICATION ERROR", 
                   "Error identifying new topics", 
                   {"error": str(e)})
        
        return []

def analyze_content(search_results, topics_subtopics):
    """
    Analyze content from search results and identify new topics.
    
    Args:
        search_results (dict): Search results organized by search term
        topics_subtopics (list): List of topic dictionaries
        
    Returns:
        tuple: (analyzed_content, new_topics)
            - analyzed_content (dict): Analyzed content organized by search term
            - new_topics (list): New topics identified during analysis
    """
    # Try to import display_process_status from main, if available
    try:
        from main import display_process_status
        process_status_available = True
    except ImportError:
        process_status_available = False
        
    def show_status(stage, message, content=None):
        """Helper function to show status if available"""
        logging.info(f"{stage}: {message}")
        if process_status_available:
            display_process_status(stage, message, content)
    
    show_status("CONTENT ANALYSIS START", 
               f"Starting content analysis for {len(search_results)} search terms", 
               {"search_terms": list(search_results.keys())})
    
    analyzed_content = {}
    all_analyzed_papers = []
    
    # Analyze each paper for each search term
    for search_term, papers in search_results.items():
        show_status("ANALYZING TERM", 
                   f"Analyzing papers for: {search_term}", 
                   {"paper_count": len(papers)})
        
        term_analysis = []
        
        for paper in papers:
            analysis = extract_paper_information(paper)
            if analysis:
                term_analysis.append(analysis)
                all_analyzed_papers.append(analysis)
        
        analyzed_content[search_term] = term_analysis
        show_status("TERM ANALYSIS COMPLETE", 
                   f"Completed analysis for: {search_term}", 
                   {"papers_analyzed": len(term_analysis)})
    
    # Identify new topics
    show_status("IDENTIFYING NEW TOPICS", 
               "Looking for potential new topics from analyzed content", 
               {"papers_analyzed": len(all_analyzed_papers)})
               
    new_topics = identify_new_topics(all_analyzed_papers, topics_subtopics)
    
    show_status("CONTENT ANALYSIS COMPLETE", 
               f"Analysis complete, identified {len(new_topics)} new topics", 
               {"new_topics": [topic['topic'] for topic in new_topics]})
    
    return analyzed_content, new_topics

def format_subtopic_as_article(subtopic, parent_topic, analyzed_papers, aggregate_findings):
    """
    Format a completed research subtopic into a properly structured article section with references.
    
    Args:
        subtopic (str): The subtopic being researched
        parent_topic (str): The parent topic this subtopic belongs to
        analyzed_papers (list): List of analyzed papers for this subtopic
        aggregate_findings (dict): Aggregated findings from all papers
        
    Returns:
        str: Formatted article section with references
    """
    import google.generativeai as genai
    import os
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Set up Gemini API
    safety_settings = setup_gemini_api()
    if not safety_settings:
        logger.error("Failed to set up Gemini API for article formatting")
        return None
    
    # Create a model instance
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        safety_settings=safety_settings,
        generation_config={"temperature": 0.3}
    )
    
    # Prepare input for the model
    # Create a structured input with all the research data
    prompt_inputs = {
        "subtopic": subtopic,
        "parent_topic": parent_topic,
        "key_findings": aggregate_findings.get("key_findings", []),
        "methodologies": aggregate_findings.get("methodologies", []),
        "research_gaps": aggregate_findings.get("research_gaps", []),
        "theoretical_frameworks": aggregate_findings.get("theoretical_frameworks", []),
        "papers": []
    }
    
    # Add the analyzed papers information
    for paper in analyzed_papers:
        paper_info = {
            "title": paper.get("title", "Untitled"),
            "authors": paper.get("authors", "Unknown"),
            "journal": paper.get("journal", ""),
            "year": paper.get("year", ""),
            "url": paper.get("url", ""),
            "key_findings": paper.get("key_findings", [])
        }
        prompt_inputs["papers"].append(paper_info)
    
    # Build the prompt
    prompt = f"""
    You are an academic writer. Format the following research subtopic into a properly structured article section.
    
    SUBTOPIC: {subtopic}
    PARENT TOPIC: {parent_topic}
    
    KEY FINDINGS:
    {chr(10).join([f"- {finding}" for finding in prompt_inputs["key_findings"]])}
    
    METHODOLOGIES:
    {chr(10).join([f"- {method}" for method in prompt_inputs["methodologies"]])}
    
    ANALYZED PAPERS:
    {chr(10).join([f"Paper {i+1}: {paper['title']} by {paper['authors']}" for i, paper in enumerate(prompt_inputs["papers"])])}
    
    FORMAT INSTRUCTIONS:
    1. Create a well-structured article section with a clear title derived from the subtopic
    2. Include an introduction, body paragraphs, and a conclusion
    3. Cite the papers properly with (Author et al., Year) in-text citations
    4. Be concise and focused - keep the entire section under 3000 characters
    5. Focus on the most important findings and implications
    6. Use markdown formatting for headings, lists, and emphasis
    7. Include a References section at the end with properly formatted citations
    
    Generate a concise, well-structured article section based on the provided information.
    """
    
    try:
        # Generate the article section
        response = model.generate_content(prompt)
        article_section = response.text
        
        # Clean up the response if needed
        article_section = article_section.replace("```markdown", "").replace("```", "")
        
        # Format the final output
        formatted_section = f"### {subtopic}\n\n"
        formatted_section += article_section
        
        return formatted_section
    except Exception as e:
        logger.error(f"Error generating article section for {subtopic}: {str(e)}")
        return f"""### {subtopic}

{subtopic} represents an important area within {parent_topic}. The research indicates several key findings including: {', '.join(prompt_inputs["key_findings"][:3])}.

#### References

{chr(10).join([f"- {paper['authors']} ({paper['year']}). {paper['title']}. {paper['journal']}." for paper in prompt_inputs["papers"] if paper['authors'] != 'Unknown' and paper['year']])}
"""
