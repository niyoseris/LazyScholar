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
- **Specialized Templates**: Includes pre-defined templates for various research domains
- **Dry Run Mode**: Test initialization and analysis without performing full research

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
   
   You can obtain a Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

## Usage

Run the LazyScholar application with a research problem statement:

```bash
python lazy_scholar.py "Your research problem statement here"
```

### Options

- `--search-engine`: Specify a different search engine URL (default: https://scholar.google.com)
- `--headless`: Run browser in headless mode
- `--output-dir`: Specify output directory (default: research_output)
- `--dry-run`: Test initialization and analysis without performing full research
- `--timeout`: Set browser operation timeout in seconds (default: 120)
- `--max-pdfs`: Maximum number of PDFs to download per topic (default: 10)

Example:

```bash
python lazy_scholar.py "The impact of climate change on marine ecosystems" --output-dir climate_research --dry-run
```

## Specialized Research Templates

LazyScholar includes specialized templates for various research domains:

1. **Music and Politics**: For research on music's relationship with political views and movements
2. **AI and Education**: For research on artificial intelligence in educational contexts
3. **Technology and Society**: For research on digital transformation and social impacts
4. **Health and Medicine**: For research on medical innovations and healthcare systems
5. **Environment and Sustainability**: For research on climate change and conservation
6. **Business and Economics**: For research on economic theories and business strategies
7. **Psychology and Human Behavior**: For research on cognitive processes and mental health

These templates are automatically selected based on keywords in your research problem statement.

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
- Without a valid API key, only default templates will be used

## License

This project is licensed under the MIT License - see the LICENSE file for details.
