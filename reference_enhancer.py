"""
Reference Enhancer - Helps enhance academic references with accessible sources
"""

import os
import sys
import json
import requests
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure constants
ARXIV_API_URL = "http://export.arxiv.org/api/query"
DEFAULT_RESULTS_PER_QUERY = 5
RATE_LIMIT_DELAY = 3  # seconds between API calls to avoid rate limiting

def search_arxiv(query: str, max_results: int = DEFAULT_RESULTS_PER_QUERY) -> List[Dict[str, Any]]:
    """
    Search arXiv for papers matching the query
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        
    Returns:
        List of dictionaries containing paper information
    """
    params = {
        'search_query': query,
        'max_results': max_results,
        'sortBy': 'relevance',
        'sortOrder': 'descending'
    }
    
    try:
        response = requests.get(ARXIV_API_URL, params=params)
        response.raise_for_status()
        
        # Parse the XML response
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)
        
        # Extract namespaces
        namespaces = {'atom': 'http://www.w3.org/2005/Atom',
                     'arxiv': 'http://arxiv.org/schemas/atom'}
        
        results = []
        for entry in root.findall('.//atom:entry', namespaces):
            # Get basic metadata
            title = entry.find('./atom:title', namespaces).text.strip()
            summary = entry.find('./atom:summary', namespaces).text.strip()
            published = entry.find('./atom:published', namespaces).text.strip()
            url = None
            for link in entry.findall('./atom:link', namespaces):
                if link.attrib.get('title') == 'pdf':
                    url = link.attrib.get('href')
                    break
            
            # Get authors
            authors = []
            for author in entry.findall('./atom:author/atom:name', namespaces):
                authors.append(author.text.strip())
            
            # Get categories
            categories = []
            for category in entry.findall('./atom:category', namespaces):
                categories.append(category.attrib.get('term'))
            
            # Get arXiv ID
            id_url = entry.find('./atom:id', namespaces).text
            arxiv_id = id_url.split('/abs/')[-1]
            
            results.append({
                'title': title,
                'summary': summary,
                'published': published,
                'published_year': published[:4],
                'url': url,
                'authors': authors,
                'categories': categories,
                'arxiv_id': arxiv_id
            })
        
        return results
    
    except requests.exceptions.RequestException as e:
        print(f"Error searching arXiv: {e}")
        return []
    except Exception as e:
        print(f"Error parsing arXiv results: {e}")
        return []

def format_citation(paper: Dict[str, Any], style: str = 'apa') -> str:
    """
    Format a paper as a citation string
    
    Args:
        paper: Dictionary containing paper information
        style: Citation style to use (currently only 'apa' is supported)
        
    Returns:
        Formatted citation string
    """
    if style == 'apa':
        # Format authors
        if len(paper['authors']) > 5:
            authors = ", ".join([a for a in paper['authors'][:5]]) + ", et al."
        else:
            authors = ", ".join([a for a in paper['authors']])
        
        # Format year
        year = paper.get('published_year', 'n.d.')
        
        # Format title (maintain original case)
        title = paper.get('title', '')
        
        # Format URL
        url = paper.get('url', '')
        
        return f"{authors} ({year}). {title}. *arXiv preprint arXiv:{paper['arxiv_id']}*."
    
    else:
        return f"Citation style '{style}' not supported"

def search_and_format_citations(query: str, max_results: int = DEFAULT_RESULTS_PER_QUERY, 
                               style: str = 'apa') -> List[str]:
    """
    Search for papers and format them as citations
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        style: Citation style to use
        
    Returns:
        List of formatted citation strings
    """
    papers = search_arxiv(query, max_results)
    return [format_citation(paper, style) for paper in papers]

def enhance_section_references(section_name: str, keywords: List[str], 
                              max_results_per_keyword: int = 2) -> List[str]:
    """
    Enhance references for a specific section using keywords
    
    Args:
        section_name: Name of the section (for logging)
        keywords: List of keywords to search for
        max_results_per_keyword: Maximum number of results to return per keyword
        
    Returns:
        List of formatted citation strings
    """
    print(f"Enhancing references for section: {section_name}")
    all_citations = []
    
    for keyword in keywords:
        print(f"  Searching for: {keyword}")
        query = f'"{keyword}" AND "quantum computing"'
        
        citations = search_and_format_citations(query, max_results_per_keyword)
        all_citations.extend(citations)
        
        # Respect rate limits
        time.sleep(RATE_LIMIT_DELAY)
    
    return all_citations

def enhance_paper_references(sections: Dict[str, List[str]], 
                            output_file: str = "enhanced_references.md") -> None:
    """
    Enhance references for each section in a paper
    
    Args:
        sections: Dictionary mapping section names to lists of keywords
        output_file: Path to output file
    """
    all_sections_citations = {}
    
    for section_name, keywords in sections.items():
        citations = enhance_section_references(section_name, keywords)
        all_sections_citations[section_name] = citations
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write("# Enhanced References\n\n")
        f.write(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for section_name, citations in all_sections_citations.items():
            f.write(f"## {section_name}\n\n")
            for citation in citations:
                f.write(f"* {citation}\n")
            f.write("\n")
    
    print(f"Enhanced references written to {output_file}")

if __name__ == "__main__":
    # Define sections and keywords
    sections = {
        "Personalized Medicine": [
            "quantum computing drug discovery",
            "quantum computing genomic analysis",
            "quantum machine learning medicine"
        ],
        "Financial Modeling": [
            "quantum computing portfolio optimization",
            "quantum computing risk management",
            "quantum finance"
        ],
        "Materials Science": [
            "quantum computing materials discovery",
            "quantum simulation materials",
            "quantum computing energy storage"
        ],
        "Smart City Optimization": [
            "quantum computing traffic optimization",
            "quantum computing energy grid",
            "quantum computing resource allocation"
        ],
        "Advanced AI": [
            "quantum machine learning",
            "quantum neural networks",
            "quantum reinforcement learning"
        ],
        "Security Implications": [
            "quantum resistant cryptography",
            "quantum key distribution",
            "post-quantum cryptography"
        ]
    }
    
    # Run the enhancement
    enhance_paper_references(sections, "enhanced_references.md")
