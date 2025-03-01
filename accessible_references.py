"""
Accessible References - A specialized tool for finding academic references 
while avoiding CAPTCHA and blocking issues
"""

import requests
import json
import time
import random
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configure various search APIs
CROSSREF_API = "https://api.crossref.org/works"
CORE_API = "https://api.core.ac.uk/v3/search/works"  # Requires API key
ARXIV_API = "http://export.arxiv.org/api/query"
UNPAYWALL_API = "https://api.unpaywall.org/v2/"  # Requires email

# Rate limiting to avoid being flagged as a bot
MIN_DELAY = 1.0  # Minimum delay between requests in seconds
MAX_DELAY = 3.0  # Maximum delay between requests in seconds

# Topic to API Query mapping
# This helps translate research topics to effective API queries
TOPIC_QUERIES = {
    "quantum_computing_general": {
        "crossref": "quantum+computing",
        "arxiv": "all:quantum+computing",
        "core": "quantum computing"
    },
    "quantum_medicine": {
        "crossref": "quantum+medicine+OR+quantum+drug+discovery",
        "arxiv": "all:quantum+AND+medicine",
        "core": "quantum medicine OR quantum drug discovery"
    },
    "quantum_finance": {
        "crossref": "quantum+finance+OR+quantum+portfolio+optimization",
        "arxiv": "all:quantum+AND+finance",
        "core": "quantum finance"
    },
    "quantum_materials": {
        "crossref": "quantum+materials+OR+quantum+simulation+materials",
        "arxiv": "cat:cond-mat+AND+quantum+simulation",
        "core": "quantum materials simulation"
    },
    "quantum_optimization": {
        "crossref": "quantum+optimization+OR+quantum+annealing",
        "arxiv": "all:quantum+optimization",
        "core": "quantum optimization OR quantum annealing"
    },
    "quantum_ml": {
        "crossref": "quantum+machine+learning",
        "arxiv": "all:quantum+AND+machine+learning",
        "core": "quantum machine learning"
    },
    "quantum_security": {
        "crossref": "quantum+cryptography+OR+post-quantum+cryptography",
        "arxiv": "all:quantum+AND+cryptography",
        "core": "quantum cryptography OR post-quantum"
    }
}

class ReferenceSearch:
    """Class to handle academic reference searching across multiple APIs"""
    
    def __init__(self, api_keys: Dict[str, str] = None):
        """
        Initialize the reference search
        
        Args:
            api_keys: Dictionary of API keys for various services
        """
        self.api_keys = api_keys or {}
        self.results_cache = {}
        self._setup_directories()
    
    def _setup_directories(self):
        """Set up directories for caching results"""
        self.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _random_delay(self):
        """Implement a random delay between requests to avoid rate limiting"""
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        time.sleep(delay)
    
    def search_crossref(self, query: str, max_results: int = 10, 
                       min_year: int = 2018) -> List[Dict[str, Any]]:
        """
        Search CrossRef for academic papers
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            min_year: Minimum publication year
            
        Returns:
            List of paper dictionaries
        """
        # Build query parameters
        params = {
            'query': query,
            'rows': max_results,
            'sort': 'relevance',
            'order': 'desc',
            'filter': f'from-pub-date:{min_year}'
        }
        
        # Cache key
        cache_key = f"crossref_{query}_{max_results}_{min_year}"
        
        # Check cache
        if cache_key in self.results_cache:
            return self.results_cache[cache_key]
        
        try:
            response = requests.get(CROSSREF_API, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('message', {}).get('items', []):
                # Extract relevant information
                title = item.get('title', [''])[0] if item.get('title') else ''
                
                # Get authors
                authors = []
                for author in item.get('author', []):
                    given = author.get('given', '')
                    family = author.get('family', '')
                    if given and family:
                        authors.append(f"{family}, {given[0]}.")
                    elif family:
                        authors.append(family)
                
                # Get year
                published_date = None
                if 'published' in item and 'date-parts' in item['published']:
                    date_parts = item['published']['date-parts'][0]
                    if date_parts and len(date_parts) > 0:
                        published_date = date_parts[0]
                
                # Get DOI and URL
                doi = item.get('DOI', '')
                url = f"https://doi.org/{doi}" if doi else ''
                
                # Get journal/publication
                container_title = item.get('container-title', [''])[0] if item.get('container-title') else ''
                
                # Format result
                result = {
                    'title': title,
                    'authors': authors,
                    'year': published_date,
                    'doi': doi,
                    'url': url,
                    'journal': container_title,
                    'source': 'crossref'
                }
                
                results.append(result)
            
            # Cache results
            self.results_cache[cache_key] = results
            return results
            
        except Exception as e:
            print(f"Error searching CrossRef: {e}")
            return []
    
    def search_arxiv(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search arXiv for papers
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of paper dictionaries
        """
        # Cache key
        cache_key = f"arxiv_{query}_{max_results}"
        
        # Check cache
        if cache_key in self.results_cache:
            return self.results_cache[cache_key]
        
        params = {
            'search_query': query,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        try:
            response = requests.get(ARXIV_API, params=params)
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
                    author_name = author.text.strip()
                    name_parts = author_name.split()
                    if len(name_parts) > 1:
                        surname = name_parts[-1]
                        initials = ''.join([n[0] + '.' for n in name_parts[:-1]])
                        authors.append(f"{surname}, {initials}")
                    else:
                        authors.append(author_name)
                
                # Get categories
                categories = []
                for category in entry.findall('./atom:category', namespaces):
                    categories.append(category.attrib.get('term'))
                
                # Get arXiv ID
                id_url = entry.find('./atom:id', namespaces).text
                arxiv_id = id_url.split('/abs/')[-1]
                
                results.append({
                    'title': title,
                    'summary': summary[:200] + "..." if len(summary) > 200 else summary,
                    'published': published,
                    'year': published[:4],
                    'url': url,
                    'authors': authors,
                    'categories': categories,
                    'arxiv_id': arxiv_id,
                    'source': 'arxiv'
                })
            
            # Cache results
            self.results_cache[cache_key] = results
            return results
        
        except Exception as e:
            print(f"Error searching arXiv: {e}")
            return []
    
    def search_core(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search CORE for academic papers
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of paper dictionaries
        """
        # Check if API key is available
        if 'core' not in self.api_keys:
            print("CORE API key not provided. Skipping CORE search.")
            return []
        
        # Cache key
        cache_key = f"core_{query}_{max_results}"
        
        # Check cache
        if cache_key in self.results_cache:
            return self.results_cache[cache_key]
        
        headers = {
            "Authorization": f"Bearer {self.api_keys['core']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "q": query,
            "size": max_results,
            "offset": 0
        }
        
        try:
            response = requests.post(CORE_API, headers=headers, json=data)
            response.raise_for_status()
            results_json = response.json()
            
            results = []
            for item in results_json.get('results', []):
                authors = []
                for author in item.get('authors', []):
                    author_name = author.get('name', '')
                    if author_name:
                        name_parts = author_name.split()
                        if len(name_parts) > 1:
                            surname = name_parts[-1]
                            initials = ''.join([n[0] + '.' for n in name_parts[:-1]])
                            authors.append(f"{surname}, {initials}")
                        else:
                            authors.append(author_name)
                
                # Format result
                result = {
                    'title': item.get('title', ''),
                    'authors': authors,
                    'year': item.get('year'),
                    'doi': item.get('doi'),
                    'url': item.get('downloadUrl'),
                    'journal': item.get('journal', {}).get('title', ''),
                    'source': 'core'
                }
                
                results.append(result)
            
            # Cache results
            self.results_cache[cache_key] = results
            return results
            
        except Exception as e:
            print(f"Error searching CORE: {e}")
            return []
    
    def search_all(self, topic_key: str, max_results_per_source: int = 5) -> List[Dict[str, Any]]:
        """
        Search all available sources for a topic
        
        Args:
            topic_key: Key from TOPIC_QUERIES
            max_results_per_source: Maximum results per source
            
        Returns:
            List of results across all sources
        """
        if topic_key not in TOPIC_QUERIES:
            print(f"Unknown topic key: {topic_key}")
            return []
        
        all_results = []
        
        # Search CrossRef
        if 'crossref' in TOPIC_QUERIES[topic_key]:
            self._random_delay()
            query = TOPIC_QUERIES[topic_key]['crossref']
            results = self.search_crossref(query, max_results_per_source)
            all_results.extend(results)
        
        # Search arXiv
        if 'arxiv' in TOPIC_QUERIES[topic_key]:
            self._random_delay()
            query = TOPIC_QUERIES[topic_key]['arxiv']
            results = self.search_arxiv(query, max_results_per_source)
            all_results.extend(results)
        
        # Search CORE if API key available
        if 'core' in self.api_keys and 'core' in TOPIC_QUERIES[topic_key]:
            self._random_delay()
            query = TOPIC_QUERIES[topic_key]['core']
            results = self.search_core(query, max_results_per_source)
            all_results.extend(results)
        
        return all_results
    
    def format_reference(self, paper: Dict[str, Any], style: str = 'apa') -> str:
        """
        Format a paper as a reference string
        
        Args:
            paper: Paper dictionary
            style: Citation style ('apa', 'mla', etc.)
            
        Returns:
            Formatted reference string
        """
        if style == 'apa':
            # Format authors
            authors = paper.get('authors', [])
            if len(authors) > 5:
                author_str = ", ".join(authors[:5]) + ", et al."
            elif len(authors) > 1:
                author_str = ", ".join(authors[:-1]) + ", & " + authors[-1]
            elif len(authors) == 1:
                author_str = authors[0]
            else:
                author_str = "No author"
            
            # Get year
            year = paper.get('year', 'n.d.')
            
            # Get title (in sentence case)
            title = paper.get('title', '')
            
            # Get source info
            if paper['source'] == 'arxiv':
                # arXiv paper
                arxiv_id = paper.get('arxiv_id', '')
                return f"{author_str} ({year}). {title}. *arXiv preprint arXiv:{arxiv_id}*."
            
            elif paper['source'] in ['crossref', 'core']:
                # Journal article
                journal = paper.get('journal', '')
                doi = paper.get('doi', '')
                doi_url = f"https://doi.org/{doi}" if doi else ''
                
                if journal:
                    return f"{author_str} ({year}). {title}. *{journal}*. {doi_url}"
                else:
                    return f"{author_str} ({year}). {title}. {doi_url}"
            
            else:
                # Generic format
                return f"{author_str} ({year}). {title}."
        
        else:
            return f"Citation style '{style}' not supported"
    
    def get_section_references(self, section_name: str, topic_keys: List[str], 
                              max_per_topic: int = 3) -> List[str]:
        """
        Get formatted references for a section
        
        Args:
            section_name: Name of the section
            topic_keys: List of topic keys to search for
            max_per_topic: Maximum references per topic
            
        Returns:
            List of formatted references
        """
        print(f"Finding references for section: {section_name}")
        references = []
        
        for topic_key in topic_keys:
            print(f"  Searching for topic: {topic_key}")
            
            if topic_key not in TOPIC_QUERIES:
                print(f"  Unknown topic key: {topic_key}")
                continue
            
            results = self.search_all(topic_key, max_per_topic)
            
            # Format references
            for paper in results:
                reference = self.format_reference(paper)
                references.append(reference)
        
        return references
    
    def save_references_to_file(self, sections_references: Dict[str, List[str]], 
                               output_file: str = "references.md") -> None:
        """
        Save references to a markdown file
        
        Args:
            sections_references: Dictionary mapping section names to lists of references
            output_file: Output file path
        """
        with open(output_file, 'w') as f:
            f.write("# Academic References\n\n")
            f.write(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for section_name, references in sections_references.items():
                f.write(f"## {section_name}\n\n")
                
                if not references:
                    f.write("*No references found for this section.*\n\n")
                    continue
                
                for reference in references:
                    f.write(f"* {reference}\n")
                
                f.write("\n")
        
        print(f"References saved to {output_file}")


def main():
    """Main function to demonstrate reference searching"""
    
    # Create searcher
    searcher = ReferenceSearch()
    
    # Define sections and topics
    sections = {
        "Quantum Computing in Personalized Medicine": [
            "quantum_medicine"
        ],
        "Financial Modeling with Quantum Computing": [
            "quantum_finance"
        ],
        "Materials Science and Quantum Computing": [
            "quantum_materials"
        ],
        "Smart City Optimization with Quantum Computing": [
            "quantum_optimization"
        ],
        "Quantum Computing in Advanced AI": [
            "quantum_ml"
        ],
        "Security Implications of Quantum Computing": [
            "quantum_security"
        ],
        "General Quantum Computing": [
            "quantum_computing_general"
        ]
    }
    
    # Get references for each section
    sections_references = {}
    for section_name, topic_keys in sections.items():
        references = searcher.get_section_references(section_name, topic_keys)
        sections_references[section_name] = references
    
    # Save to file
    searcher.save_references_to_file(sections_references)

if __name__ == "__main__":
    main()
