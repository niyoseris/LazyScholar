"""
UI Module - Handles user interface elements for the academic research assistant.
"""

def get_problem_statement():
    """
    Get the problem statement from the user.
    
    Returns:
        str: The problem statement entered by the user.
    """
    print("\n" + "="*80)
    print(" "*30 + "ACADEMIC RESEARCH ASSISTANT")
    print("="*80 + "\n")
    
    print("Welcome to the Academic Research Assistant!")
    print("This application will help you generate a structured academic paper")
    print("based on a problem statement and automated literature review.\n")
    
    print("Please enter your research problem statement or question below.")
    print("This should be the main question or issue your research paper will address.")
    print("Example: 'What are the effects of climate change on marine biodiversity?'\n")
    
    while True:
        problem_statement = input("Enter your problem statement: ").strip()
        
        if not problem_statement:
            print("Problem statement cannot be empty. Please try again.")
            continue
            
        if len(problem_statement) < 10:
            print("Problem statement seems too short. Please provide more details.")
            continue
            
        confirm = input(f"\nYou entered: \"{problem_statement}\"\nIs this correct? (y/n): ").lower()
        
        if confirm == 'y':
            break
    
    print("\nThank you! Processing your request. This may take several minutes...")
    return problem_statement

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
