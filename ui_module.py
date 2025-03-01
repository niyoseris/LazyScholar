"""
UI Module - Handles user interface elements for the academic research assistant.
"""

import os
import logging
import sys

logger = logging.getLogger(__name__)

def is_interactive():
    """Check if the script is running in an interactive mode."""
    return os.isatty(sys.stdin.fileno())

def get_problem_statement():
    """
    Get the research problem statement from the user.
    
    Returns:
        str: The validated problem statement
    """
    print("\n" + "="*80)
    print(" " * 30 + "ACADEMIC RESEARCH ASSISTANT")
    print("="*80 + "\n")
    
    print("Welcome to the Academic Research Assistant!")
    print("This application will help you generate a structured academic paper")
    print("based on a problem statement and automated literature review.\n")
    
    print("Please enter your research problem statement or question below.")
    print("This should be the main question or issue your research paper will address.")
    print("Example: 'What are the effects of climate change on marine biodiversity?'\n")
    
    while True:
        try:
            print("Enter your problem statement: ", end="")
            problem_statement = sys.stdin.readline().strip()
            
            # Handle non-interactive mode (stdin is being piped)
            if not is_interactive():
                print(f"\nYou entered: \"{problem_statement}\"")
                print("Auto-confirming in non-interactive mode.")
                return problem_statement
                
            if not problem_statement:
                print("Problem statement cannot be empty. Please try again.")
                continue
                
            confirm = input(f"\nYou entered: \"{problem_statement}\"\nIs this correct? (y/n): ").lower()
            if confirm in ["y", "yes"]:
                return problem_statement
                
        except EOFError:
            # Handle EOF error (e.g., when input is piped)
            if problem_statement:
                print(f"\nProcessing input: \"{problem_statement}\"")
                return problem_statement
            else:
                print("\nNo input detected. Using default problem statement.")
                return "What are the effects of climate change on marine biodiversity?"
                
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            raise SystemExit(0)

def display_final_paper(paper_content, references):
    """
    Display the final generated paper to the user.
    
    Args:
        paper_content (str): The content of the generated paper.
        references (list): List of references used in the paper.
    """
    print("\n" + "="*80)
    print(" "*30 + "GENERATED RESEARCH PAPER")
    print("="*80 + "\n")
    
    # Display a preview of the paper
    preview_length = 500
    preview = paper_content[:preview_length] + "..." if len(paper_content) > preview_length else paper_content
    
    print(preview)
    
    print("\n" + "-"*80)
    print(f"Total paper length: {len(paper_content)} characters")
    print(f"Number of references: {len(references)}")
    print("-"*80 + "\n")
    
    print("The complete paper has been saved to 'research_paper.md'")
    
    # Ask if user wants to see the full paper
    if input("Would you like to see the full paper? (y/n): ").lower() == 'y':
        print("\n" + "="*80)
        print(paper_content)
        print("\n\nREFERENCES:")
        for i, ref in enumerate(references, 1):
            print(f"{i}. {ref}")
        print("="*80)
