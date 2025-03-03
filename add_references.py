import os
import re

def add_references_to_final_paper():
    """
    Extract references from all subtopic files and add them to the final paper.
    """
    print("Starting to add references to the final paper...")
    
    # Collect all references
    all_references = []
    topics_dir = 'research_output/topics'
    
    # Iterate through all topic directories
    for topic in os.listdir(topics_dir):
        topic_dir = os.path.join(topics_dir, topic)
        if os.path.isdir(topic_dir):
            # Iterate through all subtopic files
            for subtopic_file in os.listdir(topic_dir):
                if subtopic_file.endswith('.md'):
                    file_path = os.path.join(topic_dir, subtopic_file)
                    print(f"Processing {file_path}")
                    
                    # Read the subtopic file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Extract references from the Source section
                        source_match = re.search(r'## Source\s*\n(.*?)(?:\n\n|\Z)', content, re.DOTALL)
                        if source_match:
                            sources = source_match.group(1).strip()
                            # Add to references with topic and subtopic context
                            subtopic_name = subtopic_file[:-3]  # Remove .md extension
                            ref_entry = f"**{topic} - {subtopic_name}**: {sources}"
                            all_references.append(ref_entry)
                            print(f"Found reference: {ref_entry[:50]}...")
    
    # Read the final paper
    final_paper_path = 'research_output/final_paper.md'
    with open(final_paper_path, 'r', encoding='utf-8') as f:
        paper_content = f.read()
    
    # Check if References section already exists
    if '## References' not in paper_content:
        # Add References section at the end
        paper_content += '\n## References\n'
    else:
        # Replace existing References section
        paper_content = re.sub(r'## References\s*\n.*', '## References\n', paper_content, flags=re.DOTALL)
    
    # Add all references
    if all_references:
        for i, ref in enumerate(all_references, 1):
            paper_content += f"{i}. {ref}\n\n"
    else:
        paper_content += "No references were found in the source materials.\n"
    
    # Write the updated content back to the file
    with open(final_paper_path, 'w', encoding='utf-8') as f:
        f.write(paper_content)
    
    print(f"Added {len(all_references)} references to {final_paper_path}")

if __name__ == "__main__":
    add_references_to_final_paper() 