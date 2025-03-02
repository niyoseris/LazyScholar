# LazyScholar - Technical Documentation

## Project Overview

LazyScholar is an AI-powered academic research assistant designed to help users conduct comprehensive literature reviews and generate structured academic papers. The application leverages Google's Gemini Flash 2.0 LLM for both text and vision tasks, automating the process of searching academic databases, analyzing research papers, and compiling findings.

## Architecture

The application follows a modular architecture with the following components:

1. **Problem Statement Analysis**: Analyzes the user's research problem to generate topics and subtopics
2. **Web Search**: Searches academic databases for relevant papers
3. **PDF Processing**: Downloads and extracts information from PDF files
4. **Content Extraction**: Extracts relevant information for each subtopic
5. **Paper Generation**: Compiles all research into a final academic paper

## Key Components

### LazyScholar Class

The main class that orchestrates the research process. It provides methods for:

- Analyzing problem statements
- Searching academic databases
- Downloading PDF files
- Extracting content from PDFs
- Writing subtopic files
- Generating the final paper

### Web Scraper Module

Leverages the existing web_scraper package for browser automation and web scraping. Key components include:

- Browser factory for creating browser instances
- Vision helper for analyzing screenshots
- File utilities for managing files and directories

### Gemini Integration

Integrates with Google's Gemini Flash 2.0 LLM for:

- Text analysis (problem statement, PDF content)
- Vision analysis (search interfaces, PDF links)
- Content generation (final paper)

## Workflow

1. **Input**: User provides a research problem statement
2. **Topic Generation**: The application analyzes the problem statement and generates topics and subtopics
3. **Search**: For each topic, the application searches academic databases
4. **PDF Processing**: The application downloads and processes up to 10 PDFs per topic
5. **Content Extraction**: For each PDF, the application extracts content relevant to each subtopic
6. **File Generation**: The application writes subtopic files with extracted content
7. **Paper Compilation**: The application compiles all research into a final paper

## Implementation Details

### Problem Statement Analysis

The application uses Gemini Flash 2.0 to analyze the problem statement and generate topics and subtopics. The response is formatted as a JSON array of objects, each containing a topic and its subtopics.

### Web Search

The application uses Selenium to automate web searches on academic databases. It leverages Gemini's vision capabilities to identify search inputs and extract search results.

### PDF Processing

The application downloads PDF files from search results and uses PyPDF2 to extract text. It then uses Gemini to analyze the text and extract relevant information for each subtopic.

### Content Extraction

For each PDF, the application extracts:
- Key findings
- Methodologies
- Important data
- Conclusions
- Citation information

### Paper Generation

The application compiles all extracted content into a final paper with:
- Title
- Abstract
- Introduction
- Literature Review
- Methodology
- Results and Discussion
- Conclusion
- References

## Usage Examples

### Basic Usage

```python
from lazy_scholar import LazyScholar

# Create LazyScholar instance
scholar = LazyScholar()

# Conduct research
final_paper_path = scholar.conduct_research(
    "The impact of artificial intelligence on healthcare delivery"
)

print(f"Final paper saved to: {final_paper_path}")
```

### Custom Search Engine

```python
from lazy_scholar import LazyScholar

# Create LazyScholar instance
scholar = LazyScholar(headless=True)

# Conduct research using a custom search engine
final_paper_path = scholar.conduct_research(
    "The effectiveness of renewable energy technologies",
    search_engine="https://www.researchgate.net"
)

print(f"Final paper saved to: {final_paper_path}")
```

## Future Enhancements

1. **Multiple Search Engines**: Support for searching multiple academic databases
2. **Citation Management**: Improved citation extraction and formatting
3. **Interactive Mode**: Interactive mode for user feedback during the research process
4. **PDF Annotation**: Visual annotation of PDFs to highlight relevant sections
5. **Research Quality Metrics**: Metrics to evaluate the quality of the research
6. **Custom Templates**: Support for custom paper templates and formats

## Dependencies

- Python 3.8+
- Selenium for web automation
- PyPDF2 and pdfplumber for PDF processing
- Google Generative AI Python SDK for Gemini integration
- Requests for HTTP requests
- Pillow for image processing

## License

This project is licensed under the MIT License. 