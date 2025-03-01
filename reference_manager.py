"""
Reference Manager - Handles reference integration and formatting within research papers
"""

import os
import re
import json
import argparse
from typing import List, Dict, Any, Optional, Tuple
import time
from datetime import datetime

class ReferenceManager:
    """
    Class to manage references throughout a research project
    - Integrates in-text citations
    - Formats reference lists
    - Processes markdown files
    """
    
    def __init__(self, project_dir: str = None):
        """
        Initialize the reference manager
        
        Args:
            project_dir: Base directory for the project
        """
        self.project_dir = project_dir or os.path.dirname(os.path.abspath(__file__))
        self.references_file = os.path.join(self.project_dir, "references.md")
        self.citations_map = {}
        self.loaded_references = []
        self._load_references()
    
    def _load_references(self):
        """Load references from the references file"""
        if not os.path.exists(self.references_file):
            print(f"References file not found: {self.references_file}")
            return
        
        current_section = None
        with open(self.references_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Check if it's a section header
                if line.startswith('## '):
                    current_section = line[3:]
                    continue
                
                # Check if it's a reference entry
                if line.startswith('* '):
                    ref_text = line[2:]
                    # Extract author and year
                    author_year_match = re.search(r'([^(]+)\((\d{4})\)', ref_text)
                    if author_year_match:
                        author = author_year_match.group(1).strip()
                        year = author_year_match.group(2).strip()
                        
                        # Create citation key
                        first_author = author.split(',')[0].strip()
                        citation_key = f"{first_author}, {year}"
                        
                        self.citations_map[citation_key] = ref_text
                        self.loaded_references.append({
                            'citation_key': citation_key,
                            'full_reference': ref_text,
                            'section': current_section
                        })
    
    def generate_in_text_citation(self, author: str, year: str) -> str:
        """
        Generate an in-text citation
        
        Args:
            author: Author name
            year: Publication year
            
        Returns:
            Formatted in-text citation
        """
        return f"({author}, {year})"
    
    def extract_citations_from_text(self, text: str) -> List[str]:
        """
        Extract citations from text
        
        Args:
            text: Text to extract citations from
            
        Returns:
            List of citation keys
        """
        citation_pattern = r'\(([^,]+), (\d{4})\)'
        matches = re.findall(citation_pattern, text)
        return [f"{author}, {year}" for author, year in matches]
    
    def format_references_section(self, citations: List[str]) -> str:
        """
        Format the references section
        
        Args:
            citations: List of citation keys
            
        Returns:
            Formatted references section
        """
        if not citations:
            return "## References\n\nNo citations found in the document."
        
        # Get unique citations
        unique_citations = set(citations)
        
        # Format references section
        references_text = "## References\n\n"
        
        for citation_key in sorted(unique_citations):
            if citation_key in self.citations_map:
                references_text += f"* {self.citations_map[citation_key]}\n"
            else:
                references_text += f"* {citation_key} - [CITATION NOT FOUND]\n"
        
        return references_text
    
    def process_markdown_file(self, file_path: str, update_references: bool = True) -> Tuple[str, List[str]]:
        """
        Process a markdown file to extract citations and optionally update references
        
        Args:
            file_path: Path to the markdown file
            update_references: Whether to update the references section
            
        Returns:
            Tuple of (processed text, list of citations)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r') as f:
            text = f.read()
        
        # Extract citations
        citations = self.extract_citations_from_text(text)
        
        if update_references:
            # Check if there's an existing references section
            references_pattern = r'## References\s*\n(.*?)($|##)'
            references_match = re.search(references_pattern, text, re.DOTALL)
            
            formatted_references = self.format_references_section(citations)
            
            if references_match:
                # Replace existing references section
                text = text[:references_match.start()] + formatted_references + text[references_match.end()-2:]
            else:
                # Add references section at the end
                text += "\n\n" + formatted_references
        
        return text, citations
    
    def update_document_references(self, file_path: str, save: bool = True) -> str:
        """
        Update references in a document
        
        Args:
            file_path: Path to the document
            save: Whether to save the updated document
            
        Returns:
            Updated document text
        """
        updated_text, citations = self.process_markdown_file(file_path)
        
        if save:
            with open(file_path, 'w') as f:
                f.write(updated_text)
            print(f"Updated references in {file_path}")
        
        return updated_text
    
    def scan_project_files(self, file_extension: str = ".md") -> List[str]:
        """
        Scan project directory for files with the specified extension
        
        Args:
            file_extension: File extension to scan for
            
        Returns:
            List of file paths
        """
        file_paths = []
        for root, _, files in os.walk(self.project_dir):
            for file in files:
                if file.endswith(file_extension):
                    file_paths.append(os.path.join(root, file))
        return file_paths
    
    def update_all_documents(self) -> Dict[str, int]:
        """
        Update references in all markdown documents in the project
        
        Returns:
            Dictionary mapping file paths to number of citations
        """
        file_paths = self.scan_project_files(".md")
        results = {}
        
        for file_path in file_paths:
            # Skip the references file itself
            if os.path.basename(file_path) == os.path.basename(self.references_file):
                continue
            
            try:
                updated_text, citations = self.process_markdown_file(file_path)
                
                if citations:
                    with open(file_path, 'w') as f:
                        f.write(updated_text)
                    results[file_path] = len(citations)
                    print(f"Updated {len(citations)} citations in {file_path}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        
        return results

def main():
    """Main function to run the reference manager"""
    parser = argparse.ArgumentParser(description='Manage references in research papers')
    parser.add_argument('--project-dir', type=str, help='Project directory')
    parser.add_argument('--file', type=str, help='Specific file to process')
    parser.add_argument('--update-all', action='store_true', help='Update all markdown files')
    
    args = parser.parse_args()
    
    manager = ReferenceManager(args.project_dir)
    
    if args.file:
        manager.update_document_references(args.file)
    elif args.update_all:
        results = manager.update_all_documents()
        print(f"Updated {len(results)} documents with references")
    else:
        print("No action specified. Use --file or --update-all.")

if __name__ == "__main__":
    main()
