import os
import re
import json
import sys

def modify_generate_final_paper():
    """
    Modify the generate_final_paper method in lazy_scholar.py to include references.
    """
    print("Modifying LazyScholar to include references in the final paper...")
    
    # Read the lazy_scholar.py file
    with open('lazy_scholar.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the generate_final_paper method
    pattern = r'def generate_final_paper\(self\).*?return paper_path\s+except Exception as e:'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("Could not find the generate_final_paper method in lazy_scholar.py")
        return
    
    # Get the current method
    current_method = match.group(0)
    
    # Create the new method with references
    new_method = """def generate_final_paper(self) -> str:
        \"\"\"
        Generate the final research paper by combining all subtopic content.
        
        Returns:
            str: Path to the generated paper
        \"\"\"
        try:
            # Create the final paper path
            paper_path = os.path.join(self.output_dir, "final_paper.md")
            
            # Generate paper content
            markdown = f\"\"\"# Research Paper: {self.problem_statement}

## Abstract
This research paper explores {self.problem_statement} through a systematic analysis of various topics and subtopics.

## Table of Contents
\"\"\"
            # Add table of contents
            for topic in self.topics:
                markdown += f"\\n### {topic['title']}\\n"
                for subtopic in topic["subtopics"]:
                    markdown += f"* {subtopic['title']}\\n"
            
            markdown += "\\n## Introduction\\n"
            markdown += f"This research investigates {self.problem_statement} "
            markdown += "through a comprehensive analysis of multiple aspects and perspectives.\\n\\n"
            
            # Collect all references
            all_references = []
            
            # Add content from each topic and subtopic
            for topic in self.topics:
                markdown += f"\\n## {topic['title']}\\n"
                
                for subtopic in topic["subtopics"]:
                    # Get the subtopic file path
                    subtopic_file = os.path.join(
                        self.output_dir,
                        "topics",
                        self._sanitize_filename(topic["title"]),
                        f"{self._sanitize_filename(subtopic['title'])}.md"
                    )
                    
                    if os.path.exists(subtopic_file):
                        with open(subtopic_file, "r", encoding="utf-8") as f:
                            content = f.read()
                            
                            # Extract references from the Source section
                            source_match = re.search(r'## Source\\s*\\n(.*?)(?:\\n\\n|\\Z)', content, re.DOTALL)
                            if source_match:
                                sources = source_match.group(1).strip()
                                # Add to references with topic and subtopic context
                                ref_entry = f"**{topic['title']} - {subtopic['title']}**: {sources}"
                                all_references.append(ref_entry)
                                
                                # Remove the Source section as we'll collect them at the end
                                content = re.sub(r'## Source\\s*\\n.*?(?:\\n\\n|\\Z)', '', content, flags=re.DOTALL)
                            
                            # Remove the title and topic line as we'll add our own
                            content = re.sub(r"^#.*\\n.*\\n", "", content)
                            markdown += f"\\n### {subtopic['title']}\\n"
                            markdown += content
            
            # Add conclusion
            markdown += "\\n## Conclusion\\n"
            markdown += "This research has explored various aspects of the topic through systematic analysis "
            markdown += "of multiple sources and perspectives. The findings contribute to a better understanding "
            markdown += f"of {self.problem_statement}.\\n"
            
            # Add references section
            markdown += "\\n## References\\n"
            if all_references:
                for i, ref in enumerate(all_references, 1):
                    markdown += f"{i}. {ref}\\n\\n"
            else:
                markdown += "No references were found in the source materials.\\n"
            
            # Write the paper
            with open(paper_path, "w", encoding="utf-8") as f:
                f.write(markdown)
            
            logger.info(f"Generated final paper at {paper_path}")
            return paper_path
            
        except Exception as e:"""
    
    # Replace the old method with the new one
    modified_content = content.replace(current_method, new_method)
    
    # Write the modified content back to the file
    with open('lazy_scholar.py', 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print("Successfully modified lazy_scholar.py to include references in the final paper")

def add_regenerate_final_paper_option():
    """
    Add a --regenerate-final-paper option to the parse_arguments function.
    """
    print("Adding --regenerate-final-paper option...")
    
    # Read the lazy_scholar.py file
    with open('lazy_scholar.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the parse_arguments function
    pattern = r'def parse_arguments\(\):.*?return args'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("Could not find the parse_arguments function in lazy_scholar.py")
        return
    
    # Get the current function
    current_function = match.group(0)
    
    # Check if the option already exists
    if '--regenerate-final-paper' in current_function:
        print("The --regenerate-final-paper option already exists")
        return
    
    # Add the new option
    new_option = """    parser.add_argument(
        "--regenerate-final-paper",
        action="store_true",
        help="Regenerate the final paper from existing subtopic files"
    )
    """
    
    # Insert the new option before the "return args" line
    modified_function = current_function.replace("    return args", new_option + "\n    return args")
    
    # Replace the old function with the new one
    modified_content = content.replace(current_function, modified_function)
    
    # Write the modified content back to the file
    with open('lazy_scholar.py', 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print("Successfully added --regenerate-final-paper option")

def add_academic_format_option():
    """
    Add a --academic-format option to the parse_arguments function.
    """
    print("Adding --academic-format option...")
    
    # Read the lazy_scholar.py file
    with open('lazy_scholar.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the parse_arguments function
    pattern = r'def parse_arguments\(\):.*?return args'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("Could not find the parse_arguments function in lazy_scholar.py")
        return
    
    # Get the current function
    current_function = match.group(0)
    
    # Check if the option already exists
    if '--academic-format' in current_function:
        print("The --academic-format option already exists")
        return
    
    # Add the new option
    new_option = """    parser.add_argument(
        "--academic-format",
        action="store_true",
        help="Format the final paper as an academic paper with proper citations and references"
    )
    """
    
    # Insert the new option before the "return args" line
    modified_function = current_function.replace("    return args", new_option + "\n    return args")
    
    # Replace the old function with the new one
    modified_content = content.replace(current_function, modified_function)
    
    # Write the modified content back to the file
    with open('lazy_scholar.py', 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print("Successfully added --academic-format option")

def modify_main_function():
    """
    Modify the main function to handle the --regenerate-final-paper option.
    """
    print("Modifying main function to handle --regenerate-final-paper option...")
    
    # Read the lazy_scholar.py file
    with open('lazy_scholar.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the main function
    pattern = r'def main\(\):.*?sys\.exit\(1\)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("Could not find the main function in lazy_scholar.py")
        return
    
    # Get the current function
    current_function = match.group(0)
    
    # Check if the regenerate option is already handled
    if 'args.regenerate_final_paper' in current_function:
        print("The --regenerate-final-paper option is already handled")
        return
    
    # Add the code to handle the regenerate option
    new_code = """        # Initialize LazyScholar
        logger.info("Initializing LazyScholar...")
        scholar = LazyScholar(
            headless=args.headless,
            output_dir=args.output_dir,
            timeout=args.timeout,
            search_suffix=args.search_suffix,
            max_pdfs_per_topic=args.max_pdfs,
            focus=args.focus
        )
        
        # Check if we should just regenerate the final paper
        if hasattr(args, 'regenerate_final_paper') and args.regenerate_final_paper:
            logger.info("Regenerating final paper from existing subtopic files...")
            # Load topics from tracking file
            topics_file = os.path.join(args.output_dir, "topics_and_subtopics.json")
            if os.path.exists(topics_file):
                with open(topics_file, 'r', encoding='utf-8') as f:
                    scholar.topics = json.load(f)
                scholar.problem_statement = args.problem_statement
                final_paper = scholar.generate_final_paper()
                logger.info(f"Final paper regenerated at {final_paper}")
                
                # Check if we should format as academic paper
                if hasattr(args, 'academic_format') and args.academic_format:
                    logger.info("Formatting final paper as academic paper...")
                    try:
                        import subprocess
                        result = subprocess.run(
                            ["python", "academic_formatter.py", "--input", final_paper],
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0:
                            logger.info("Successfully formatted final paper as academic paper")
                        else:
                            logger.error(f"Failed to format final paper: {result.stderr}")
                    except Exception as e:
                        logger.error(f"Error formatting final paper: {str(e)}")
                
                sys.exit(0)
            else:
                logger.error(f"Topics tracking file not found at {topics_file}")
                sys.exit(1)
        
        # Start research process
        logger.info("Starting research process...")"""
    
    # Replace the initialization and research process code
    modified_function = re.sub(
        r'# Initialize LazyScholar.*?# Start research process\s+logger\.info\("Starting research process\.\.\.\"\)',
        new_code,
        current_function,
        flags=re.DOTALL
    )
    
    # Replace the old function with the new one
    modified_content = content.replace(current_function, modified_function)
    
    # Write the modified content back to the file
    with open('lazy_scholar.py', 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print("Successfully modified main function to handle --regenerate-final-paper option")

def modify_research_process():
    """
    Modify the research process to format the final paper as academic paper if requested.
    """
    print("Modifying research process to handle --academic-format option...")
    
    # Read the lazy_scholar.py file
    with open('lazy_scholar.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the main function
    pattern = r'def main\(\):.*?if __name__ == "__main__":'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("Could not find the main function in lazy_scholar.py")
        return
    
    # Get the current function
    current_function = match.group(0)
    
    # Check if the academic format option is already handled
    if 'academic_format' in current_function and 'academic_formatter.py' in current_function:
        print("The --academic-format option is already handled")
        return
    
    # Find the line after final paper generation
    pattern = r'final_paper = scholar\.generate_final_paper\(\)\s+logger\.info\(f"Final paper generated at \{final_paper\}"\)'
    
    # Add the code to handle the academic format option
    new_code = """final_paper = scholar.generate_final_paper()
        logger.info(f"Final paper generated at {final_paper}")
        
        # Check if we should format as academic paper
        if hasattr(args, 'academic_format') and args.academic_format:
            logger.info("Formatting final paper as academic paper...")
            try:
                import subprocess
                result = subprocess.run(
                    ["python", "academic_formatter.py", "--input", final_paper],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    logger.info("Successfully formatted final paper as academic paper")
                else:
                    logger.error(f"Failed to format final paper: {result.stderr}")
            except Exception as e:
                logger.error(f"Error formatting final paper: {str(e)}")"""
    
    # Replace the final paper generation code
    modified_function = re.sub(pattern, new_code, current_function)
    
    # Replace the old function with the new one
    modified_content = content.replace(current_function, modified_function)
    
    # Write the modified content back to the file
    with open('lazy_scholar.py', 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print("Successfully modified research process to handle --academic-format option")

if __name__ == "__main__":
    modify_generate_final_paper()
    add_regenerate_final_paper_option()
    add_academic_format_option()
    modify_main_function()
    modify_research_process()
    print("All modifications completed successfully!") 