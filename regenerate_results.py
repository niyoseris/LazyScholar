#!/usr/bin/env python3
"""
Script to regenerate research results with improved formatting.
"""

import os
import json
import logging
from dotenv import load_dotenv

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
    """Display process status."""
    print(f"\n{'-' * 80}")
    print(f"[{stage}] {message}")
    if content:
        for key, value in content.items():
            if isinstance(value, list) and value:
                print(f"  {key}:")
                for i, item in enumerate(value, 1):
                    print(f"    {i}. {item}")
            else:
                print(f"  {key}: {value}")
    print(f"{'-' * 80}")

def clean_authors(authors):
    """Clean and format author names."""
    if not authors:
        return "Unknown"
        
    if isinstance(authors, str):
        return authors
        
    if isinstance(authors, list):
        # Handle single characters
        if all(isinstance(a, str) and len(a) == 1 for a in authors):
            return "".join(authors)
            
        # Handle normal list
        proper_authors = []
        for author in authors:
            if isinstance(author, str) and len(author) <= 2 and author.strip() in [',', ' ', '-']:
                continue
            proper_authors.append(author)
        return ", ".join(proper_authors)
    
    return "Unknown"

def fix_research_gaps(gaps):
    """Fix research gaps that have been broken into individual letters."""
    if not gaps:
        return []
        
    # Handle string
    if isinstance(gaps, str):
        if gaps.strip().lower() == "unknown":
            return []
        return [gaps]
        
    # Handle list
    if isinstance(gaps, list):
        # Check if single characters (spelling "unknown")
        if all(isinstance(g, str) and len(g) == 1 for g in gaps):
            joined = "".join(gaps).strip().lower()
            if joined == "unknown":
                return []
            return [joined]
            
        # Otherwise filter out empty or "unknown" entries
        return [gap for gap in gaps if gap and isinstance(gap, str) and gap.strip().lower() != "unknown"]
        
    return []

def regenerate_research_file(filepath):
    """Regenerate a research file with improved formatting."""
    
    try:
        # Read the current file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse the content to extract paper information
        parsed_data = {
            'title': os.path.basename(filepath).replace('.md', '').replace('_', ' '),
            'key_findings': [],
            'methodologies': [],
            'research_gaps': [],
            'theoretical_frameworks': [],
            'references': [],
            'papers': []
        }
        
        # Extract key findings
        import re
        key_findings_match = re.search(r'## Key Findings\s+\n((?:- .*\n)+)', content)
        if key_findings_match:
            findings_text = key_findings_match.group(1)
            parsed_data['key_findings'] = [f.strip('- \n') for f in findings_text.split('\n') if f.strip()]
            
        # Extract methodologies
        methodologies_match = re.search(r'## Methodologies\s+\n((?:- .*\n|.*\n)+?)(?:\n##|\Z)', content)
        if methodologies_match:
            methodologies_text = methodologies_match.group(1)
            if "No methodologies were identified" not in methodologies_text:
                parsed_data['methodologies'] = [m.strip('- \n') for m in methodologies_text.split('\n') if m.strip()]
                
        # Extract research gaps
        gaps_match = re.search(r'## Research Gaps\s+\n((?:- .*\n|.*\n)+?)(?:\n##|\Z)', content)
        if gaps_match:
            gaps_text = gaps_match.group(1)
            if "No research gaps were identified" not in gaps_text:
                parsed_data['research_gaps'] = [g.strip('- \n') for g in gaps_text.split('\n') if g.strip()]
                # Fix research gaps
                parsed_data['research_gaps'] = fix_research_gaps(parsed_data['research_gaps'])
                
        # Extract theoretical frameworks
        frameworks_match = re.search(r'## Theoretical Frameworks\s+\n((?:- .*\n|.*\n)+?)(?:\n##|\Z)', content)
        if frameworks_match:
            frameworks_text = frameworks_match.group(1)
            if "No theoretical frameworks were identified" not in frameworks_text:
                parsed_data['theoretical_frameworks'] = [f.strip('- \n') for f in frameworks_text.split('\n') if f.strip()]
                
        # Extract references
        refs_match = re.search(r'## References\s+\n((?:\d+\. .*\n|.*\n)+?)(?:\n##|\Z)', content)
        if refs_match:
            refs_text = refs_match.group(1)
            if "No references were identified" not in refs_text:
                parsed_data['references'] = [r.strip('\n').split('. ', 1)[1] if '. ' in r else r.strip('\n') 
                                             for r in refs_text.split('\n') if r.strip()]
                
        # Extract papers
        papers_sections = re.findall(r'### \d+\. (.*?)(?=\n### \d+\. |\Z)', content, re.DOTALL)
        for paper_section in papers_sections:
            paper = {'title': paper_section.split('\n')[0].strip()}
            
            # Extract authors
            authors_match = re.search(r'\*\*Authors\*\*: (.*?)\n', paper_section)
            if authors_match:
                raw_authors = authors_match.group(1).strip()
                paper['authors'] = clean_authors(raw_authors)
                
            # Extract year
            year_match = re.search(r'\*\*Year\*\*: (.*?)\n', paper_section)
            if year_match:
                paper['year'] = year_match.group(1).strip()
                
            # Extract journal
            journal_match = re.search(r'\*\*Journal/Publication\*\*: (.*?)\n', paper_section)
            if journal_match:
                paper['journal'] = journal_match.group(1).strip()
                
            # Extract URL
            url_match = re.search(r'\*\*URL\*\*: \[(.*?)\]\((.*?)\)', paper_section)
            if url_match:
                paper['url'] = url_match.group(2).strip()
                
            # Extract snippet
            snippet_match = re.search(r'\*\*Abstract/Snippet\*\*:\s*>\s*(.*?)(?:\n\n|\Z)', paper_section, re.DOTALL)
            if snippet_match:
                paper['snippet'] = snippet_match.group(1).strip()
                
            # Extract keywords
            keywords_match = re.search(r'\*\*Keywords\*\*: (.*?)\n', paper_section)
            if keywords_match:
                keywords_text = keywords_match.group(1).strip()
                paper['keywords'] = [k.strip() for k in keywords_text.split(',')]
                
            # Extract key findings
            findings_match = re.search(r'\*\*Key Findings\*\*:\s*\n((?:- .*\n)+)', paper_section)
            if findings_match:
                findings_text = findings_match.group(1)
                paper['key_findings'] = [f.strip('- \n') for f in findings_text.split('\n') if f.strip()]
                
            # Extract research gaps
            gaps_match = re.search(r'\*\*Research Gaps\*\*:\s*\n((?:- .*\n)+)', paper_section)
            if gaps_match:
                gaps_text = gaps_match.group(1)
                paper['research_gaps'] = [g.strip('- \n') for g in gaps_text.split('\n') if g.strip()]
                # Fix research gaps
                paper['research_gaps'] = fix_research_gaps(paper['research_gaps'])
                
            # Add to papers list
            parsed_data['papers'].append(paper)
        
        # Create the new content with improved formatting
        from main import save_subtopic_results
        
        # Prepare the data for save_subtopic_results
        subtopic = os.path.basename(filepath).replace('.md', '').replace('_', ' ')
        parent_topic = ''
        if '_' in os.path.basename(filepath):
            parts = os.path.basename(filepath).replace('.md', '').split('_')
            parent_topic = parts[0].replace('_', ' ')
            subtopic = ' '.join(parts[1:]).replace('_', ' ')
            
        aggregate_findings = {
            'key_findings': parsed_data['key_findings'],
            'methodologies': parsed_data['methodologies'],
            'research_gaps': parsed_data['research_gaps'],
            'theoretical_frameworks': parsed_data['theoretical_frameworks'],
            'cited_authors': parsed_data['references']
        }
        
        analyzed_papers = []
        for paper in parsed_data['papers']:
            analyzed_paper = {
                'title': paper.get('title', 'Untitled'),
                'authors': paper.get('authors', 'Unknown'),
                'year': paper.get('year', ''),
                'journal': paper.get('journal', 'Unknown'),
                'url': paper.get('url', ''),
                'snippet': paper.get('snippet', ''),
                'keywords': paper.get('keywords', []),
                'key_findings': paper.get('key_findings', []),
                'research_gaps': paper.get('research_gaps', []),
                'cited_authors': []
            }
            analyzed_papers.append(analyzed_paper)
            
        # Regenerate the file with improved formatting
        save_subtopic_results(subtopic, parent_topic, aggregate_findings, analyzed_papers)
        
        display_process_status("RESEARCH FILE REGENERATED", 
                             f"Successfully regenerated research file: {filepath}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error regenerating research file {filepath}: {str(e)}", exc_info=True)
        display_process_status("ERROR", f"Failed to regenerate research file: {filepath}", {"error": str(e)})
        return False

def main():
    """Regenerate all research results."""
    
    # Load environment variables
    load_dotenv()
    
    # Add the main module directory to path
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Import necessary modules
    from main import save_subtopic_results, display_process_status
    
    # Get all research result files
    results_dir = os.path.join(os.getcwd(), "research_results")
    if not os.path.exists(results_dir):
        print(f"Research results directory not found: {results_dir}")
        return
        
    result_files = [os.path.join(results_dir, f) for f in os.listdir(results_dir) if f.endswith('.md')]
    
    print(f"Found {len(result_files)} research result files to regenerate.")
    
    # Regenerate each file
    success_count = 0
    for filepath in result_files:
        print(f"Regenerating: {os.path.basename(filepath)}")
        if regenerate_research_file(filepath):
            success_count += 1
            
    print(f"Successfully regenerated {success_count} out of {len(result_files)} research files.")

if __name__ == "__main__":
    main()
