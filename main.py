#!/usr/bin/env python3
"""
Academic Research Assistant - Main Module
This application automates academic literature review and paper writing.
"""

import os
import time
import logging
import argparse
from dotenv import load_dotenv

from ui_module import get_problem_statement, display_final_paper
from topic_generator import generate_topics_subtopics
import web_scraper
import content_analyzer
from text_compiler import compile_paper, update_final_document
from roadmap_generator import generate_research_roadmap, save_roadmap
from reference_manager import ReferenceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("research_assistant.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def display_process_status(stage, message, content=None):
    """
    Display detailed process status to the user, showing the current stage, message,
    and relevant content.
    
    Args:
        stage (str): The current processing stage (e.g., "RESEARCH", "ANALYSIS")
        message (str): A message describing the current process
        content (any, optional): Content being processed, can be dictionary, list, or string
    """
    # Format the stage heading
    stage_display = f"[{stage}]"
    
    # Calculate the terminal width (default to 80 if can't determine)
    try:
        terminal_width = os.get_terminal_size().columns
    except:
        terminal_width = 80
    
    # Create separator lines
    separator = "-" * terminal_width
    
    # Print the stage and message
    print(f"\n{separator}")
    print(f"{stage_display} {message}")
    
    # If there's content to display, format it appropriately
    if content is not None:
        # Process dictionary content
        if isinstance(content, dict):
            # Determine if this is a paper/article
            if 'title' in content:
                print(f"  Title: {content.get('title', 'Untitled')}")
                if 'authors' in content:
                    authors = content.get('authors', [])
                    if isinstance(authors, list):
                        print(f"  Authors: {', '.join(authors)}")
                    else:
                        print(f"  Author: {authors}")
                if 'year' in content:
                    print(f"  Year: {content.get('year', '')}")
                if 'snippet' in content:
                    snippet = content.get('snippet', '')
                    if len(snippet) > 100:
                        snippet = snippet[:100] + "..."
                    print(f"  Snippet: {snippet}")
            # Topic with subtopics
            elif 'topic' in content and 'subtopics' in content:
                print(f"  Topic: {content['topic']}")
                subtopics = content.get('subtopics', [])
                if subtopics:
                    print(f"  Subtopics: {', '.join(subtopics)}")
            # Key findings
            elif 'key_findings' in content:
                findings = content.get('key_findings', [])
                if findings:
                    print("  Key Findings:")
                    for i, finding in enumerate(findings[:3], 1):  # Show first 3 findings
                        print(f"    {i}. {finding}")
                    if len(findings) > 3:
                        print(f"    ... and {len(findings) - 3} more findings")
            # Process other dictionary content by showing key-value pairs
            else:
                for key, value in content.items():
                    # Format list values
                    if isinstance(value, list):
                        if len(value) > 0:
                            if len(value) > 3:
                                preview = value[:3]
                                print(f"  {key}: {preview} (and {len(value) - 3} more)")
                            else:
                                print(f"  {key}: {value}")
                        else:
                            print(f"  {key}: None")
                    # Format string values (truncate if too long)
                    elif isinstance(value, str) and len(value) > 100:
                        print(f"  {key}: {value[:100]}...")
                    # Other values
                    else:
                        print(f"  {key}: {value}")
        
        # Process list content
        elif isinstance(content, list):
            # Limit display to first few items if list is long
            max_display = 5
            display_items = content[:max_display]
            remaining = len(content) - max_display
            
            # Show list items
            for i, item in enumerate(display_items, 1):
                if isinstance(item, dict) and 'title' in item:
                    print(f"  {i}. {item.get('title', 'Untitled')}")
                elif isinstance(item, dict):
                    print(f"  {i}. {str(item)[:100]}...")
                elif isinstance(item, str) and len(item) > 80:
                    print(f"  {i}. {item[:80]}...")
                else:
                    print(f"  {i}. {item}")
            
            # Indicate if there are more items
            if remaining > 0:
                print(f"  ... and {remaining} more items")
        
        # Process string content (truncate if too long)
        elif isinstance(content, str):
            max_length = terminal_width - 4  # Account for indent
            if len(content) > max_length:
                print(f"  {content[:max_length]}...")
            else:
                print(f"  {content}")
    
    # Close with another separator
    print(separator)

def generate_demo_topics(problem_statement):
    """Generate demo topics when API is unavailable."""
    logger.info("Generating demo topics for: %s", problem_statement)
    
    return [
        {
            "topic": "Introduction to " + problem_statement.split()[0],
            "subtopics": ["Background", "Problem Statement", "Research Questions"]
        },
        {
            "topic": "Literature Review",
            "subtopics": ["Current Research", "Gaps in Knowledge", "Theoretical Framework"]
        },
        {
            "topic": "Methodology",
            "subtopics": ["Research Design", "Data Collection", "Analysis Approach"]
        },
        {
            "topic": "Findings and Analysis",
            "subtopics": ["Key Results", "Patterns and Trends", "Comparative Analysis"]
        },
        {
            "topic": "Discussion",
            "subtopics": ["Interpretation of Results", "Implications", "Limitations"]
        },
        {
            "topic": "Conclusion",
            "subtopics": ["Summary of Findings", "Contributions to the Field", "Future Research Directions"]
        }
    ]

def generate_demo_search_results(topics_subtopics):
    """Generate demo search results when web scraping isn't possible."""
    logger.info("Generating demo search results")
    
    search_results = {}
    
    for topic_item in topics_subtopics:
        topic = topic_item['topic']
        search_results[topic] = []
        
        # Add some demo papers for each topic
        for i in range(2):
            search_results[topic].append({
                'title': f"Research on {topic} - Example {i+1}",
                'snippet': f"This paper explores {topic.lower()} with focus on various aspects including methodology and findings.",
                'database': 'Demo Database'
            })
        
        # Add papers for subtopics
        for subtopic in topic_item['subtopics']:
            search_term = f"{topic} {subtopic}"
            search_results[search_term] = []
            
            for i in range(2):
                search_results[search_term].append({
                    'title': f"{subtopic} in relation to {topic} - Study {i+1}",
                    'snippet': f"An in-depth analysis of {subtopic.lower()} within the context of {topic.lower()}, highlighting key insights.",
                    'database': 'Demo Database'
                })
    
    return search_results

def generate_demo_analyzed_content(search_results):
    """Generate demo analyzed content when API is unavailable."""
    logger.info("Generating demo analyzed content")
    
    analyzed_content = {}
    
    for search_term, results in search_results.items():
        analyzed_content[search_term] = []
        
        for paper in results:
            analyzed_content[search_term].append({
                'title': paper['title'],
                'summary': f"Summary of {paper['title']}: {paper['snippet']}",
                'key_findings': f"The key findings of this research include important insights into {search_term.lower()}.",
                'methodology': "The methodology employed in this study includes surveys, interviews, and data analysis.",
                'relevance': "This paper is highly relevant to the research topic.",
                'new_concepts': f"New concepts introduced include specialized approaches to {search_term.lower()}.",
                'source': paper['database']
            })
    
    return analyzed_content, [
        {
            "topic": "Additional Considerations", 
            "subtopics": ["Ethical Implications", "Practical Applications"]
        }
    ]

def generate_demo_paper(problem_statement, topics_subtopics, analyzed_content):
    """Generate a demo paper with placeholder content when API is unavailable."""
    logger.info("Generating demo paper")
    
    paper_content = f"""# Research Paper: {problem_statement}

## Abstract

This research paper investigates {problem_statement}. It examines various aspects of the topic through a comprehensive literature review and analysis of existing research. The paper is structured around key themes identified in the literature, providing insights into current understanding and suggesting directions for future research.

## Introduction

{problem_statement} represents an important area of academic inquiry. This paper seeks to provide a comprehensive overview of this topic, drawing on existing literature and synthesizing findings to present a cohesive understanding of the current state of knowledge.

The research is organized around the following key topics: {', '.join([topic['topic'] for topic in topics_subtopics])}.

"""
    
    # Generate content for each topic and subtopic
    for topic_item in topics_subtopics:
        topic = topic_item['topic']
        subtopics = topic_item['subtopics']
        
        # Add topic heading
        paper_content += f"## {topic}\n\n"
        paper_content += f"This section explores {topic.lower()}, which is a crucial aspect of {problem_statement}. Recent research has highlighted the significance of understanding {topic.lower()} in the broader context of this field.\n\n"
        
        # Generate content for each subtopic
        for subtopic in subtopics:
            paper_content += f"### {subtopic}\n\n"
            paper_content += f"{subtopic} is an important component of {topic.lower()}. Studies have shown various approaches to understanding and addressing this aspect, with significant implications for the broader research area.\n\n"
            
            # Add some references to the content if we have any for this topic
            search_term = f"{topic} {subtopic}"
            if search_term in analyzed_content:
                papers = analyzed_content[search_term]
                if papers:
                    paper_content += "Research in this area includes:\n\n"
                    for paper in papers[:2]:  # Limit to 2 papers
                        paper_content += f"- {paper['title']}: {paper.get('summary', 'No summary available')}\n"
                    paper_content += "\n"
    
    # Add conclusion
    paper_content += f"""## Conclusion

This paper has provided a comprehensive overview of {problem_statement}. Through the exploration of various topics including {', '.join([topic['topic'] for topic in topics_subtopics])}, we have gained insights into the current state of knowledge in this field. The research highlights the importance of continued investigation into these areas, particularly with regard to addressing gaps in current understanding and exploring new directions.

Future research should focus on extending the work presented here, with particular attention to emerging trends and methodological innovations.
"""
    
    # Generate references
    references = []
    for search_term, papers in analyzed_content.items():
        for paper in papers:
            ref = f"Author(s) (Year). {paper['title']}. Journal of {search_term}, Volume(Issue), pp-pp."
            references.append(ref)
    
    return paper_content, list(set(references))  # Remove duplicates

def research_subtopic(browser, subtopic, parent_topic="", settings=None):
    """
    Research a specific subtopic by searching academic databases and extracting relevant information.
    
    Args:
        browser: Browser instance for web interactions
        subtopic: The subtopic to research
        parent_topic: The parent topic this subtopic belongs to
        settings: Dictionary of settings to pass to web_scraper
        
    Returns:
        dict: Aggregated findings from the research
    """
    display_process_status("RESEARCHING", 
                           f"Researching subtopic: '{subtopic}' under topic '{parent_topic}'", 
                           {"search_term": subtopic, "parent": parent_topic})
    
    # Prepare search term - if parent topic and subtopic are different, combine them
    search_term = subtopic
    if parent_topic and parent_topic.lower() not in subtopic.lower():
        search_term = f"{parent_topic} {subtopic}"
    
    logger.info("Researching subtopic: '%s' under topic '%s'", subtopic, parent_topic)
    
    if settings is None:
        settings = {}
    
    # Perform search with all available search engines
    search_results = []
    failed_engines = []
    search_attempts = 0
    
    # Define search engines to try, in order of priority
    search_engines = [
        {"name": "Google Scholar", "tried": False},
        {"name": "Semantic Scholar", "tried": False},
        {"name": "arXiv", "tried": False},
        {"name": "PubMed", "tried": False},
        {"name": "IEEE Xplore", "tried": False},
        {"name": "ResearchGate", "tried": False},
        {"name": "DuckDuckGo", "tried": False}
    ]
    
    # Filter search engines based on settings
    if 'search_engines' in settings:
        filtered_engines = []
        for engine in search_engines:
            if engine['name'] in settings['search_engines']:
                filtered_engines.append(engine)
        search_engines = filtered_engines
    
    # Try search engines until we have enough results or tried them all
    while len(search_results) < 10 and search_attempts < len(search_engines):
        # Find the next untried engine
        current_engine = None
        for engine in search_engines:
            if not engine["tried"]:
                current_engine = engine
                break
        
        if not current_engine:
            break  # All engines tried
        
        # Mark this engine as tried
        current_engine["tried"] = True
        search_attempts += 1
        
        # Calculate progress percentage
        progress_percent = int((search_attempts / len(search_engines)) * 100)
        
        try:
            logger.info(f"Searching {current_engine['name']} for: {search_term}")
            display_process_status("SEARCHING", 
                                  f"Searching {current_engine['name']} for '{search_term}'")
            
            # Show progress in browser
            web_scraper.show_search_progress(
                browser, 
                f"Researching: {search_term}", 
                engine=current_engine['name'], 
                progress=progress_percent
            )
            
            # Sanitize search term
            sanitized_search_term = web_scraper.sanitize_search_term(search_term)
            
            # Call the search function
            try:
                engine_results = web_scraper.get_search_engine_function(current_engine["name"])(
                    browser, sanitized_search_term, settings=settings
                )
                
                if engine_results:
                    logger.info(f"Found {len(engine_results)} results from {current_engine['name']}")
                    search_results.extend(engine_results)
                    display_process_status("RESULTS FOUND", 
                                          f"Found {len(engine_results)} results from {current_engine['name']}")
                else:
                    logger.warning(f"No results found from {current_engine['name']}")
                    failed_engines.append(current_engine["name"])
                    display_process_status("NO RESULTS", 
                                          f"No results found from {current_engine['name']}")
            except web_scraper.BlockedSiteException as e:
                logger.warning(f"{current_engine['name']} is blocked: {str(e)}")
                failed_engines.append(f"{current_engine['name']} (Blocked)")
                display_process_status("SITE BLOCKED", 
                                      f"{current_engine['name']} is blocked", 
                                      {"error": str(e)})
            except Exception as e:
                logger.error(f"Error searching {current_engine['name']}: {str(e)}")
                failed_engines.append(f"{current_engine['name']} (Error: {str(e)})")
                display_process_status("SEARCH ERROR", 
                                      f"Error searching {current_engine['name']}", 
                                      {"error": str(e)})
        except Exception as e:
            logger.error(f"Error searching {current_engine['name']}: {str(e)}")
            failed_engines.append(f"{current_engine['name']} (Error: {str(e)})")
            display_process_status("SEARCH ERROR", 
                                  f"Error searching {current_engine['name']}", 
                                  {"error": str(e)})
    
    # Hide progress indicator when done
    web_scraper.hide_search_progress(browser)
    
    # Display overall results
    if search_results:
        logger.info(f"Found a total of {len(search_results)} results for subtopic: {subtopic}")
        display_process_status("SEARCH COMPLETE", 
                              f"Found {len(search_results)} total results for '{subtopic}'", 
                              {"result_count": len(search_results), 
                               "engines_used": [e["name"] for e in search_engines if e["tried"] and e["name"] not in failed_engines]})
    else:
        logger.warning(f"No results found for '{search_term}' across any search engines")
        display_process_status("NO RESULTS", 
                              f"No search results found for '{subtopic}' - check for CAPTCHA challenges in the browser window",
                              {"failed_engines": failed_engines})
        return {
            "key_findings": ["No results found. This could be due to CAPTCHA challenges or access restrictions."],
            "methodologies": [],
            "cited_authors": [],
            "research_gaps": ["Research restricted due to access limitations."],
            "theoretical_frameworks": []
        }
    
    # Analyze the search results using content analyzer
    analyzed_papers = []
    
    if not search_results:
        display_process_status("NO RESULTS", 
                              f"No search results found for '{subtopic}' - check for CAPTCHA challenges in the browser window")
        return {
            "key_findings": ["No results found. This could be due to CAPTCHA challenges or access restrictions."],
            "methodologies": [],
            "cited_authors": [],
            "research_gaps": ["Research restricted due to access limitations."],
            "theoretical_frameworks": []
        }
        
    # Continue with research paper analysis for any results we found
    display_process_status("ANALYZING", 
                         f"Analyzing {len(search_results)} papers for '{subtopic}'")
    
    for i, paper_result in enumerate(search_results[:5]):  # Process top 5 papers
        logger.info("Analyzing paper %d/%d: %s", i+1, min(5, len(search_results)), paper_result.get('title', 'Untitled'))
        try:
            analysis = content_analyzer.extract_paper_information(paper_result)
            if analysis:
                # Make sure the analysis has the expected structure
                for key in ['key_findings', 'methodology', 'cited_authors', 'research_gaps', 'theoretical_framework']:
                    if key not in analysis:
                        analysis[key] = [] if key in ['key_findings', 'cited_authors', 'research_gaps'] else "Unknown"
                
                analyzed_papers.append(analysis)
                display_process_status("PAPER ANALYSIS", 
                                       f"Analyzed paper: {paper_result.get('title', 'Untitled')}", 
                                       analysis)
        except Exception as e:
            logger.error(f"Error analyzing paper: {str(e)}", exc_info=True)
    
    # Combine the findings from individual papers into an aggregate result
    aggregate_findings = {
        "key_findings": [],
        "methodologies": [],
        "cited_authors": [],
        "research_gaps": [],
        "theoretical_frameworks": []
    }
    
    for paper in analyzed_papers:
        # Safely add key findings (ensure it's a list)
        if "key_findings" in paper:
            findings = paper.get("key_findings", [])
            if isinstance(findings, list):
                aggregate_findings["key_findings"].extend(findings)
            elif isinstance(findings, str):
                aggregate_findings["key_findings"].append(findings)
        
        # Safely add methodology
        if "methodology" in paper:
            method = paper.get("methodology", "Unknown")
            if method and method != "Unknown":
                aggregate_findings["methodologies"].append(method)
        
        # Safely add cited authors
        if "cited_authors" in paper:
            authors = paper.get("cited_authors", [])
            if isinstance(authors, list):
                aggregate_findings["cited_authors"].extend(authors)
            elif isinstance(authors, str) and authors:
                aggregate_findings["cited_authors"].append(authors)
        
        # Safely add research gaps
        if "research_gaps" in paper:
            gaps = paper.get("research_gaps", [])
            if isinstance(gaps, list):
                aggregate_findings["research_gaps"].extend(gaps)
            elif isinstance(gaps, str) and gaps:
                aggregate_findings["research_gaps"].append(gaps)
        
        # Safely add theoretical framework
        if "theoretical_framework" in paper:
            framework = paper.get("theoretical_framework", "Unknown")
            if framework and framework != "Unknown":
                aggregate_findings["theoretical_frameworks"].append(framework)
    
    # Remove duplicates (safely)
    for key in ["key_findings", "methodologies", "cited_authors", "research_gaps", "theoretical_frameworks"]:
        if isinstance(aggregate_findings[key], list):
            # For string items, we can deduplicate using a set
            if all(isinstance(item, str) for item in aggregate_findings[key]):
                aggregate_findings[key] = list(set(aggregate_findings[key]))
            else:
                # For non-string items, use a more cautious approach
                unique_items = []
                for item in aggregate_findings[key]:
                    if item not in unique_items:
                        unique_items.append(item)
                aggregate_findings[key] = unique_items
    
    display_process_status("SUBTOPIC RESEARCH COMPLETE", 
                           f"Completed research on subtopic: '{subtopic}'", 
                           aggregate_findings)
    
    # Save the results to a file
    save_subtopic_results(subtopic, parent_topic, aggregate_findings, analyzed_papers)
    
    # Update the final document with the new findings
    from text_compiler import update_final_document
    
    # Create a structured result to pass to the final document updater
    result_for_final = {
        "key_findings": aggregate_findings["key_findings"],
        "methodologies": aggregate_findings["methodologies"],
        "research_gaps": aggregate_findings["research_gaps"],
        "theoretical_frameworks": aggregate_findings["theoretical_frameworks"],
        "cited_authors": aggregate_findings["cited_authors"],
        "analyzed_papers": analyzed_papers
    }
    
    # Determine if this is a main topic or subtopic for final document purposes
    display_name = subtopic
    if parent_topic:
        display_name = f"{subtopic} ({parent_topic})"
    
    # Update the final document
    try:
        update_final_document(settings.get("problem_statement", "Research"), result_for_final, display_name)
        display_process_status("FINAL DOCUMENT UPDATED", 
                              f"Added '{subtopic}' to the final document")
    except Exception as e:
        logger.error(f"Error updating final document: {str(e)}")
    
    return aggregate_findings

def save_subtopic_results(subtopic, parent_topic, aggregate_findings, analyzed_papers):
    """
    Save research results for a subtopic to a well-formatted markdown file.
    
    Args:
        subtopic (str): The subtopic researched
        parent_topic (str): The parent topic
        aggregate_findings (dict): Aggregated findings from all papers
        analyzed_papers (list): List of analyzed papers
    """
    import os
    import datetime
    import json
    import content_analyzer
    
    # Create a clean filename based on the subtopic and parent topic
    if parent_topic:
        filename = f"{parent_topic.replace(' ', '_')}_{subtopic.replace(' ', '_')}.md"
    else:
        filename = f"{subtopic.replace(' ', '_')}.md"
    
    # Ensure the research_results directory exists
    if not os.path.exists("research_results"):
        os.makedirs("research_results")
    
    filepath = os.path.join("research_results", filename)
    
    # Debugging - Log the inputs
    logger.info(f"Saving subtopic: {subtopic}, Parent: {parent_topic}")
    logger.info(f"Aggregate findings: {json.dumps(aggregate_findings)}")
    logger.info(f"Analyzed papers count: {len(analyzed_papers) if analyzed_papers else 0}")
    
    # Prepare the content
    content = f"# Research: {subtopic}\n\n"
    
    if parent_topic:
        content += f"Parent Topic: {parent_topic}\n"
    
    # Add generation timestamp
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content += f"Generated: {current_time}\n\n"
    
    # Add key findings section
    content += "## Key Findings\n\n"
    if aggregate_findings.get("key_findings", []):
        for finding in aggregate_findings["key_findings"]:
            if finding and isinstance(finding, str) and finding.strip().lower() != "unknown":
                content += f"- {finding}\n"
    else:
        content += "- No key findings were identified for this subtopic.\n"
    
    content += "\n## Methodologies\n\n"
    if aggregate_findings.get("methodologies", []):
        for method in aggregate_findings["methodologies"]:
            if method and isinstance(method, str) and method.strip().lower() != "unknown":
                content += f"- {method}\n"
    else:
        content += "No methodologies were identified.\n"
    
    content += "\n## Research Gaps\n\n"
    if aggregate_findings.get("research_gaps", []):
        for gap in aggregate_findings["research_gaps"]:
            if gap and isinstance(gap, str) and gap.strip().lower() != "unknown":
                content += f"- {gap}\n"
    else:
        content += "No research gaps were identified.\n"
    
    content += "\n## Theoretical Frameworks\n\n"
    if aggregate_findings.get("theoretical_frameworks", []):
        for framework in aggregate_findings["theoretical_frameworks"]:
            if framework and isinstance(framework, str) and framework.strip().lower() != "unknown":
                content += f"- {framework}\n"
    else:
        content += "No theoretical frameworks were identified.\n"
    
    # Add References section
    content += "\n## References\n\n"
    # Format citations
    formatted_citations = []
    for author_set in aggregate_findings.get("cited_authors", []):
        if author_set and isinstance(author_set, str) and author_set.strip().lower() != "unknown":
            formatted_citations.append(f"- {author_set}")
    
    if formatted_citations:
        content += "\n".join(formatted_citations) + "\n"
    else:
        content += "No references were identified.\n"
    
    # Add individual paper analyses
    if analyzed_papers:
        content += "\n## Analyzed Papers\n\n"
        for i, paper in enumerate(analyzed_papers, 1):
            content += f"### {i}. {paper.get('title', 'Untitled Paper')}\n\n"
            
            # Format authors with proper handling
            authors = paper.get('authors', 'Unknown')
            # Clean up any problematic author formatting
            if isinstance(authors, str):
                if authors.strip() in ["...", "…"] or len(authors.strip()) <= 3:
                    authors = "Author information incomplete"
                # Handle case where authors might be broken into individual characters
                elif all(len(c.strip(',')) <= 1 for c in authors.split()):
                    authors = "".join(c for c in authors if c not in [',', ' '] and not c.isspace())
            
            content += f"**Authors**: {authors}\n\n"
            
            if 'journal' in paper and paper['journal']:
                content += f"**Journal/Publication**: {paper['journal']}\n\n"
            
            if 'url' in paper and paper['url']:
                content += f"**URL**: [{paper['url']}]({paper['url']})\n\n"
            
            if 'snippet' in paper and paper['snippet']:
                snippet = paper['snippet']
                # Clean up snippet
                if snippet.strip() in ["...", "…"]:
                    snippet = "Abstract not available"
                content += f"**Abstract/Snippet**:\n> {snippet}\n\n"
            
            if 'keywords' in paper and paper['keywords']:
                keywords = paper['keywords']
                if isinstance(keywords, list):
                    keywords = ", ".join(keywords)
                content += f"**Keywords**: {keywords}\n\n"
            
            if 'methodology' in paper and paper['methodology']:
                methodology = paper['methodology']
                if isinstance(methodology, list):
                    methodology = ", ".join(methodology)
                content += f"**Methodology**: {methodology}\n\n"
            
            if 'key_findings' in paper and paper['key_findings']:
                findings = paper['key_findings']
                content += "**Key Findings**:\n"
                if isinstance(findings, list):
                    for finding in findings:
                        if finding and finding.strip().lower() != "unknown":
                            content += f"- {finding}\n"
                elif isinstance(findings, str) and findings.strip().lower() != "unknown":
                    content += f"- {findings}\n"
                content += "\n"
            
            if i < len(analyzed_papers):
                content += "---\n\n"
    else:
        # Add a section to explain why there are no analyzed papers
        content += "\n## Research Notes\n\n"
        content += "This research subtopic could not be analyzed with specific papers. Possible reasons include:\n\n"
        content += "- Limited academic research available on this specific subtopic\n"
        content += "- Search limitations with academic databases\n"
        content += "- Technical issues during the research process\n\n"
        content += "Consider broadening the search scope or checking alternative sources for information on this topic.\n"
    
    # Generate an article section automatically if we have enough content
    if analyzed_papers and aggregate_findings.get("key_findings"):
        display_process_status("GENERATING ARTICLE", 
                            f"Creating article section for '{subtopic}'")
        
        try:
            # Import the article formatter and generate content
            article_section = content_analyzer.format_subtopic_as_article(
                subtopic, 
                parent_topic, 
                analyzed_papers, 
                aggregate_findings
            )
            
            if article_section:
                content += "\n## Article Sections\n\n"
                content += article_section + "\n"
                
                display_process_status("ARTICLE GENERATED", 
                                    f"Successfully created article section for '{subtopic}'")
            else:
                logger.warning(f"Failed to generate article section for {subtopic}")
        except Exception as e:
            logger.error(f"Error generating article section: {str(e)}")
    
    # Write the content to the file
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Successfully wrote content to {filepath}")
    except Exception as e:
        logger.error(f"Error writing to file {filepath}: {str(e)}")
    
    display_process_status("SUBTOPIC SAVED", 
                          f"Saved research results for '{subtopic}' to {filepath}", 
                          {"filepath": filepath})
    
    logger.info(f"Saved subtopic research results to {filepath}")

def sequential_research_workflow(topics_subtopics, settings=None):
    """Execute a sequential research workflow where each subtopic is researched thoroughly
    before moving to the next.
    
    Args:
        topics_subtopics (list): List of topic dictionaries with subtopics
        settings (dict): Settings for the search and analysis
        
    Returns:
        dict: Analyzed content organized by search term
    """
    if settings is None:
        settings = {}
    
    display_process_status("WORKFLOW START", 
                          "Beginning sequential research workflow", 
                          topics_subtopics)
    
    # Set up the browser
    logger.info("Setting up browser for sequential research")
    browser = web_scraper.setup_browser(headless=settings.get('headless', False), browser_type=settings.get('browser_type'))
    
    # Initialize results container
    all_research_results = {}
    
    try:
        # Process main topics as standalone search terms first
        for topic_dict in topics_subtopics:
            topic = topic_dict['topic']
            display_process_status("TOPIC RESEARCH", f"Researching topic: {topic}")
            logger.info(f"Researching main topic: {topic}")
            
            try:
                topic_results = research_subtopic(browser, topic, "", settings=settings)
                all_research_results[topic] = topic_results
            except Exception as e:
                logger.error(f"Error researching topic '{topic}': {str(e)}", exc_info=True)
                display_process_status("TOPIC ERROR", 
                                     f"Error researching topic: {topic}", 
                                     {"error": str(e)})
                # Continue with next topic
                continue
        
        # Now process each topic and its subtopics
        for topic_dict in topics_subtopics:
            topic = topic_dict['topic']
            subtopics = topic_dict.get('subtopics', [])
            
            display_process_status("SUBTOPICS", f"Processing subtopics for: {topic}", 
                                {"topic": topic, "subtopics": subtopics})
            
            logger.info(f"Processing topic: {topic} with {len(subtopics)} subtopics")
            
            # Research each subtopic
            for subtopic in subtopics:
                # Create a proper search term
                search_term = f"{topic} {subtopic}"
                
                try:
                    subtopic_results = research_subtopic(browser, subtopic, topic, settings=settings)
                    all_research_results[search_term] = subtopic_results
                except Exception as e:
                    logger.error(f"Error researching subtopic '{subtopic}' under '{topic}': {str(e)}", exc_info=True)
                    display_process_status("SUBTOPIC ERROR", 
                                         f"Error researching subtopic: {subtopic}", 
                                         {"error": str(e)})
                    # Continue with next subtopic
                    continue
    
    except Exception as e:
        logger.error(f"Error in research workflow: {str(e)}", exc_info=True)
        display_process_status("WORKFLOW ERROR", 
                             f"Error in research workflow: {str(e)}", 
                             {"error": str(e)})
    finally:
        # Always try to close the browser
        try:
            browser.quit()
            logger.info("Browser closed successfully")
        except:
            logger.warning("Error closing browser")
    
    display_process_status("RESEARCH COMPLETE", 
                         f"Completed research on {len(all_research_results)} topics/subtopics", 
                         {"researched_terms": list(all_research_results.keys())})
                         
    return all_research_results

def process_topic_with_subtopics(topic_data, args, browser=None, search_engines=None, search_settings=None):
    """Process a topic with its subtopics."""
    topic = topic_data.get("topic", "")
    subtopics = topic_data.get("subtopics", [])
    
    if search_engines is None:
        # Default search engines if not specified
        search_engines = ["Google Scholar", "PubMed", "IEEE Xplore"]
    
    if search_settings is None:
        search_settings = {}
    
    if not subtopics:
        logger.warning(f"No subtopics found for topic: {topic}")
        return
    
    logger.info(f"Processing topic: {topic} with {len(subtopics)} subtopics")
    
    # Print information about subtopics being processed
    display_process_status("RESEARCH", f"Processing subtopics for: {topic}", {
        "Topic": topic,
        "Subtopics": subtopics
    })
    
    # Process each subtopic
    for subtopic in subtopics:
        search_term = f"{subtopic}"
        parent_topic = topic
        
        # Print information about the subtopic being researched
        display_process_status("RESEARCH", f"Researching subtopic: '{subtopic}' under topic '{parent_topic}'", {
            "search_term": search_term,
            "parent": parent_topic
        })
        
        logger.info(f"Researching subtopic: '{subtopic}' under topic '{parent_topic}'")
        
        results = []
        failed_engines = []
        
        # Check if we're using DuckDuckGo
        if "DuckDuckGo" in search_engines or "duckduckgo" in search_engines:
            duckduckgo_search_term = f"{parent_topic} {search_term}"
            logger.info(f"Searching DuckDuckGo for: {duckduckgo_search_term}")
            
            display_process_status("RESEARCH", f"Searching DuckDuckGo for '{duckduckgo_search_term}'", {})
            
            try:
                # Use the provided browser instance if available, otherwise create one
                if browser:
                    # Browser is already set up, use it directly
                    duckduckgo_results = web_scraper.search_duckduckgo(
                        browser,
                        duckduckgo_search_term,
                        settings=search_settings
                    )
                else:
                    # Create a new browser instance (this is the fallback case)
                    with web_scraper.setup_browser(headless=not args.interactive, browser_type="duckduckgo") as temp_browser:
                        duckduckgo_results = web_scraper.search_duckduckgo(
                            temp_browser,
                            duckduckgo_search_term,
                            settings=search_settings
                        )
                
                if duckduckgo_results:
                    logger.info(f"Found {len(duckduckgo_results)} results from DuckDuckGo")
                    results.extend(duckduckgo_results)
                    display_process_status("RESULTS FOUND", 
                                          f"Found {len(duckduckgo_results)} results from DuckDuckGo")
                else:
                    logger.warning("No results found from DuckDuckGo")
                    display_process_status("NO RESULTS", 
                                          f"No results found from DuckDuckGo", {})
                    failed_engines.append("DuckDuckGo")
            except Exception as e:
                logger.error(f"Error searching DuckDuckGo: {e}")
                failed_engines.append("DuckDuckGo")
                
        # Continue with searching other engines as needed...
        
        # Process and save the results
        if results:
            # Process and save results
            pass
        else:
            logger.warning(f"No results found for '{search_term}' across any search engines")
            display_process_status("NO RESULTS", 
                                  f"No search results found for '{subtopic}' - check for CAPTCHA challenges in the browser window", {
                "failed_engines": failed_engines
            })

def main(demo_mode=False, settings=None):
    """
    Main function to run the academic research assistant.
    
    Args:
        demo_mode (bool): Whether to run in demo mode with mocked API calls
        settings (dict): Settings for the search and analysis
    """
    # Load environment variables
    load_dotenv()
    
    # If settings is None, initialize it
    if settings is None:
        settings = {}
    
    try:
        # Step 1: Get the problem statement from the user
        problem_statement = get_problem_statement()
        display_process_status("INITIALIZATION", f"Problem Statement: {problem_statement}")
        
        # Step 2: Generate topics and subtopics from the problem statement
        if demo_mode:
            topics_subtopics = generate_demo_topics(problem_statement)
        else:
            topics_subtopics = generate_topics_subtopics(problem_statement)
        
        # Print the topics in a more readable format with divider lines
        print("\n" + "-" * 85)
        print("[TOPIC GENERATION] Generated the following topics and subtopics:")
        for i, topic in enumerate(topics_subtopics, 1):
            topic_name = topic.get('topic', 'Unknown Topic')
            subtopics = topic.get('subtopics', [])
            print(f"  {i}. {topic_name}")
            # Print a few subtopics (up to 3) with ellipsis if there are more
            if subtopics:
                subtopics_preview = ", ".join(subtopics[:3])
                if len(subtopics) > 3:
                    subtopics_preview += f", ... ({len(subtopics) - 3} more)"
                print(f"     → {subtopics_preview}")
        print("-" * 85 + "\n")
        
        # New Step: Generate research roadmap before starting research
        roadmap = generate_research_roadmap(problem_statement, topics_subtopics)
        roadmap_path = save_roadmap(roadmap, problem_statement)
        display_process_status("ROADMAP GENERATION", f"Generated research roadmap and saved to {roadmap_path}")
        print("\n\n" + "="*80)
        print("RESEARCH ROADMAP GENERATED")
        print("="*80)
        print("A detailed roadmap for your research has been created.")
        print(f"You can view it at: {roadmap_path}")
        print("This roadmap outlines the research approach, methodology, and timeline.")
        print("="*80 + "\n\n")
        
        # Step 3: Search for relevant papers for each topic
        if demo_mode:
            search_results = generate_demo_search_results(topics_subtopics)
            # Give a feeling of processing time even in demo mode
            time.sleep(2)
            
            # In demo mode, we need to generate analyzed content
            analyzed_content, _ = generate_demo_analyzed_content(search_results)
        else:
            # Launch the browser one time and reuse for all searches
            with web_scraper.setup_browser(headless=settings.get('headless', True), browser_type=settings.get('browser_type')) as browser:
                analyzed_content = sequential_research_workflow(topics_subtopics, settings)
        
        # Step 4: Research any new topics if they were discovered
        if demo_mode:
            additional_results = generate_demo_search_results(topics_subtopics)
            additional_content, _ = generate_demo_analyzed_content(additional_results)
            analyzed_content.update(additional_content)
        else:
            new_topics = content_analyzer.identify_new_topics(analyzed_content, topics_subtopics)
            if new_topics:
                logger.info(f"Found {len(new_topics)} new topics, processing additional literature")
                display_process_status("NEW TOPICS FOUND", 
                                      f"Found {len(new_topics)} new topics for additional research", 
                                      new_topics)
                additional_content = sequential_research_workflow(new_topics, settings)
                analyzed_content.update(additional_content)
        
        # Step 5: Compile the paper
        logger.info("Compiling final paper")
        display_process_status("PAPER COMPILATION STARTED", 
                              "Beginning to compile final paper")
        final_paper = compile_paper(problem_statement, topics_subtopics, analyzed_content)
        
        # Step 6: Display the final paper
        display_final_paper(final_paper)
        
        # Step 7: Ensure references are properly formatted in all generated files
        try:
            display_process_status("REFERENCE FORMATTING", 
                                 "Checking all research documents for proper reference formatting")
            
            # Initialize reference manager
            ref_manager = ReferenceManager()
            
            # Update all documents in the project
            update_results = ref_manager.update_all_documents()
            
            if update_results:
                display_process_status("REFERENCE FORMATTING COMPLETE", 
                                     f"Updated references in {len(update_results)} documents", 
                                     update_results)
        except Exception as e:
            logger.warning(f"Error updating references: {e}", exc_info=True)
            display_process_status("REFERENCE FORMATTING WARNING", 
                                 f"Could not update references: {str(e)}")
        
        logger.info("Academic Research Assistant completed successfully")
        display_process_status("PROCESS COMPLETE", 
                              "Academic Research Assistant completed successfully", 
                              {"paper_length": len(final_paper)})
        
        return final_paper
        
    except Exception as e:
        logger.error(f"Error in main process: {e}", exc_info=True)
        print(f"\nAn error occurred: {e}")
        display_process_status("ERROR", 
                              f"An error occurred during processing: {e}")
        return None

def display_final_paper(paper):
    """
    Display the final paper to the user.
    
    Args:
        paper (str): The compiled paper content
    """
    print("\n" + "="*80)
    print("ACADEMIC RESEARCH ASSISTANT - FINAL PAPER")
    print("="*80)
    
    # Display paper
    print(paper)
    
    # Save the paper to a file
    try:
        with open("research_paper.md", "w", encoding="utf-8") as f:
            f.write(paper)
        
        print("\nResearch paper has been saved to research_paper.md")
        display_process_status("PAPER SAVED", 
                              "Research paper has been saved to research_paper.md", 
                              {"file_path": "research_paper.md"})
    except Exception as e:
        logger.error(f"Error saving paper to file: {e}")
        print(f"\nError saving paper to file: {e}")
        display_process_status("ERROR SAVING", 
                              f"Error saving paper to file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Academic Research Assistant')
    parser.add_argument('--demo', action='store_true', help='Run in demo mode without external dependencies')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode (invisible)')
    parser.add_argument('--real', action='store_true', help='Force real search mode with visible browser for CAPTCHA solving')
    
    # Search engine selection options
    parser.add_argument('--all-engines', action='store_true', help='Use all available search engines')
    parser.add_argument('--google-scholar', action='store_true', help='Use Google Scholar search engine')
    parser.add_argument('--semantic-scholar', action='store_true', help='Use Semantic Scholar search engine')
    parser.add_argument('--arxiv', action='store_true', help='Use arXiv search engine')
    parser.add_argument('--pubmed', action='store_true', help='Use PubMed search engine')
    parser.add_argument('--ieee', action='store_true', help='Use IEEE Xplore search engine')
    parser.add_argument('--research-gate', action='store_true', help='Use ResearchGate search engine')
    parser.add_argument('--duckduckgo', action='store_true', help='Use DuckDuckGo search engine (prioritizes PDF results)')
    
    args = parser.parse_args()
    
    # If --real is specified, override both demo and headless modes
    if args.real:
        demo_mode = False
        headless_mode = False
    else:
        demo_mode = args.demo
        headless_mode = args.headless
    
    # Configure settings that will be passed to modules
    settings = {
        'headless': headless_mode,  # Use headless mode if flag is provided and --real is not
        'captcha_wait_time': 120,  # Give user 2 minutes to solve CAPTCHAs
    }
    
    # Configure search engines to use
    search_engines = []
    
    # If DuckDuckGo is specified, set it as the exclusive search engine
    if args.duckduckgo:
        logger.info("Using DuckDuckGo as search engine")
        browser_type = 'duckduckgo'
        
        # Configure settings
        search_settings = {
            'prioritize_pdf': True,
            'max_results': 10,
        }
        
        # Step 1: Get the problem statement from the user
        problem_statement = get_problem_statement()
        display_process_status("INITIALIZATION", f"Problem Statement: {problem_statement}")
        
        # Step 2: Generate topics and subtopics from the problem statement
        if demo_mode:
            topics_subtopics = generate_demo_topics(problem_statement)
        else:
            topics_subtopics = generate_topics_subtopics(problem_statement)
        
        # Print the topics in a more readable format with divider lines
        print("\n" + "-" * 85)
        print("[TOPIC GENERATION] Generated the following topics and subtopics:")
        for i, topic in enumerate(topics_subtopics, 1):
            topic_name = topic.get('topic', 'Unknown Topic')
            subtopics = topic.get('subtopics', [])
            print(f"  {i}. {topic_name}")
            # Print a few subtopics (up to 3) with ellipsis if there are more
            if subtopics:
                subtopics_preview = ", ".join(subtopics[:3])
                if len(subtopics) > 3:
                    subtopics_preview += f", ... ({len(subtopics) - 3} more)"
                print(f"     → {subtopics_preview}")
        print("-" * 85 + "\n")
        
        browser = web_scraper.setup_browser(headless=not args.real, browser_type=browser_type)
        
        # Use a context manager for the browser
        with browser as browser_instance:
            for topic_data in topics_subtopics:
                process_topic_with_subtopics(
                    topic_data, 
                    args, 
                    browser_instance, 
                    search_engines=['duckduckgo'], 
                    search_settings=search_settings
                )
        search_engines.append("DuckDuckGo")
        settings['duckduckgo_only'] = True
        settings['pdf_priority'] = True  # Enable PDF prioritization
        settings['browser_type'] = 'duckduckgo'  # Use DuckDuckGo browser configuration
        settings['user_agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.3'  # Set a custom user agent
        settings['window_size'] = (1920, 1080)  # Set the window size for the browser
        settings['proxy'] = 'socks5://localhost:9050'  # Set a proxy for the browser
        settings['disable_images'] = True  # Disable images to improve performance
        settings['disable_js'] = False  # Enable JavaScript to improve functionality
        settings['incognito'] = True  # Enable incognito mode to improve privacy
        settings['disable_gpu'] = True  # Disable GPU acceleration to improve performance
        settings['no_sandbox'] = True  # Disable sandboxing to improve performance
        settings['disable_dev_shm_usage'] = True  # Disable shared memory usage to improve performance
    else:
        # If specific engines are selected, use only those
        specific_engines_selected = (
            args.google_scholar or args.semantic_scholar or args.arxiv or 
            args.pubmed or args.ieee or args.research_gate
        )
        
        if args.all_engines or not specific_engines_selected:
            # Use all engines if --all-engines is specified or no specific engines are selected
            search_engines = [
                "Google Scholar", "Semantic Scholar", "arXiv", 
                "PubMed", "IEEE Xplore", "ResearchGate", "DuckDuckGo"
            ]
        else:
            # Add only selected engines
            if args.google_scholar:
                search_engines.append("Google Scholar")
            if args.semantic_scholar:
                search_engines.append("Semantic Scholar")
            if args.arxiv:
                search_engines.append("arXiv")
            if args.pubmed:
                search_engines.append("PubMed")
            if args.ieee:
                search_engines.append("IEEE Xplore")
            if args.research_gate:
                search_engines.append("ResearchGate")
    
    settings['search_engines'] = search_engines
    
    print("\n" + "="*80)
    if demo_mode:
        print("RUNNING IN DEMO MODE: Using mock data instead of actual research")
    else:
        print("RUNNING IN REAL MODE: Performing actual web searches")
        if not headless_mode:
            print("Browser will be visible to allow solving CAPTCHAs if they appear")
            print("If a CAPTCHA appears, please solve it in the browser window that opens")
    print("\nUsing search engines:")
    for engine in search_engines:
        print(f"- {engine}")
    print("="*80 + "\n")
    
    # Pass settings to main function
    main(demo_mode=demo_mode, settings=settings)

def save_roadmap(roadmap_content, problem_statement):
    """
    Save roadmap content to a file
    
    Args:
        roadmap_content (str): Roadmap content to save
        problem_statement (str): Problem statement for filename generation
        
    Returns:
        str: Path to saved roadmap file
    """
    # Save directly to roadmap.md in the main directory
    filename = 'roadmap.md'
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(roadmap_content)
    
    return filename
