#!/usr/bin/env python3
"""
Script to generate topics_and_subtopics.json from existing directory structure
"""

import os
import json
import re

def main():
    # Define paths
    output_dir = "research_output"
    topics_dir = os.path.join(output_dir, "topics")
    tracking_file = os.path.join(output_dir, "topics_and_subtopics.json")
    
    # Check if topics directory exists
    if not os.path.exists(topics_dir):
        print(f"Error: Topics directory not found at {topics_dir}")
        return
    
    # Initialize topics list
    topics = []
    
    # Iterate through topic directories
    for topic_name in os.listdir(topics_dir):
        topic_dir = os.path.join(topics_dir, topic_name)
        
        # Skip if not a directory
        if not os.path.isdir(topic_dir):
            continue
        
        # Create topic entry
        topic = {
            "title": topic_name,
            "subtopics": []
        }
        
        # Iterate through subtopic files
        for subtopic_file in os.listdir(topic_dir):
            if not subtopic_file.endswith(".md"):
                continue
            
            # Extract subtopic title from filename
            subtopic_title = os.path.splitext(subtopic_file)[0]
            
            # Read file to determine status
            subtopic_path = os.path.join(topic_dir, subtopic_file)
            with open(subtopic_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Check if file has content (assuming completed if it has content)
                status = "completed" if len(content) > 100 else "pending"
            
            # Create subtopic entry
            subtopic = {
                "title": subtopic_title,
                "status": status
            }
            
            topic["subtopics"].append(subtopic)
        
        # Add topic to list if it has subtopics
        if topic["subtopics"]:
            topics.append(topic)
    
    # Write to tracking file
    with open(tracking_file, "w", encoding="utf-8") as f:
        json.dump(topics, f, indent=2)
    
    print(f"Generated tracking file at {tracking_file}")
    print(f"Found {len(topics)} topics with {sum(len(t['subtopics']) for t in topics)} subtopics")

if __name__ == "__main__":
    main() 