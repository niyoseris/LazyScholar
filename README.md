# LazyScholar - Academic Research Assistant

LazyScholar is an AI-powered research assistant that helps users conduct academic research by automating the process of literature review and academic paper writing.

## Features

- **Topic Generation**: Analyzes a problem statement to generate relevant topics and subtopics
- **Automated Research**: Searches academic databases (like Google Scholar) for relevant papers
- **PDF Analysis**: Downloads and extracts information from PDF files
- **Vision AI Integration**: Uses Google's Gemini Flash Vision LLM to navigate search interfaces
- **Content Extraction**: Extracts relevant information from research papers
- **Paper Generation**: Compiles findings into a structured academic paper with proper citations
- **Organized Output**: Saves research findings in a structured directory format

## How It Works

1. **Problem Statement Analysis**: User enters a research problem statement
2. **Topic Generation**: LazyScholar uses Gemini Flash LLM to generate topics and subtopics
3. **Web Search**: Searches academic databases for each topic
4. **PDF Processing**: Downloads and analyzes up to 10 PDF files per topic
5. **Content Extraction**: Extracts relevant information for each subtopic
6. **Paper Compilation**: Combines all research into a final academic paper

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Usage

Run the LazyScholar application with a research problem statement:

```bash
python lazy_scholar.py "Your research problem statement here"
```

### Options

- `--search-engine`: Specify a different search engine URL (default: https://scholar.google.com)
- `--headless`: Run browser in headless mode
- `--output-dir`: Specify output directory (default: research_output)

Example:

```bash
python lazy_scholar.py "The impact of climate change on marine ecosystems" --output-dir climate_research
```

## Output Structure

LazyScholar organizes research output in the following structure:

```
research_output/
├── pdfs/                      # Downloaded PDF files
├── Topic_1/                   # Directory for Topic 1
│   ├── Subtopic_1_1.md        # Research on Subtopic 1.1
│   ├── Subtopic_1_2.md        # Research on Subtopic 1.2
│   └── ...
├── Topic_2/                   # Directory for Topic 2
│   ├── Subtopic_2_1.md        # Research on Subtopic 2.1
│   └── ...
└── final_paper.md             # Final compiled research paper
```

## Requirements

- Python 3.8+
- Google API key for Gemini Flash 2.0
- Internet connection
- Chrome or Firefox browser

## Limitations

- Requires a valid Google API key with access to Gemini Flash 2.0
- May trigger CAPTCHAs on academic search engines
- PDF extraction quality depends on the PDF structure
- Limited to 10 PDFs per topic to avoid excessive processing

## License

This project is licensed under the MIT License - see the LICENSE file for details.
