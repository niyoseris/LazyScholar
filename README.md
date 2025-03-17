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

## Recent Updates

1. **Content Type Support**: LazyScholar now supports different content types:
   - Academic research (default)
   - Practical how-to guides
   - Travel guides

2. **Search Purpose Parameter**: Added a search_purpose parameter to specify the type of content to generate.

3. **Source Flexibility**: Changed terminology from "PDFs" to "Sources" to make it clear that the application can work with various content types.

4. **Improved Search Phrases**: Search phrases for subtopics are now more specific and always in English, including relevant keywords about the main topic.

5. **PDF Requirement Toggle**: Added a require_pdfs parameter to specify whether PDFs are required for the search.

6. **Sequential PDF Naming**: Implemented sequential numbering for downloaded PDF files (1.pdf, 2.pdf, etc.) instead of using hash-based filenames, making it easier to identify and manage downloaded files.

7. **Domain Filtering**: Added site_tld parameter to filter search results based on domain patterns (e.g., 'edu', 'gov', 'org').

8. **Minimum Sources Requirement**: Added minimum_pdfs parameter to ensure LazyScholar continues searching until it finds a minimum number of valuable sources for each subtopic.

9. **Crawl Depth Control**: Added crawl_depth and max_crawl_pages parameters to control how deeply the application crawls websites for content.

10. **Real-time Progress Tracking**: Implemented a progress tracking system in the Flask wrapper to provide real-time updates on the research process.

11. **UI Improvements**: Updated the user interface to reflect the broader focus on various content types rather than just PDFs.

## Flask Web Interface

LazyScholar now includes a Flask web application that provides a user-friendly interface to:

- Configure research parameters
- Track real-time progress of research
- View and read generated content and downloaded sources
- Save and load user research profiles

### Using the Flask Interface

1. **Start the Flask Application**:
   ```bash
   python app.py
   ```
   This will launch the web server, typically at http://127.0.0.1:5000/

2. **User Account**:
   - Register a new account or log in with existing credentials
   - Accounts allow you to save and manage multiple research profiles

3. **Dashboard**:
   - View all your saved research profiles
   - Access research results from previous projects
   - Create new research profiles

4. **Create/Edit Research Profile**:
   - Name your research project
   - Enter your research problem statement
   - Configure search settings:
     - Content type (academic, practical, travel)
     - Search engine
     - Language preferences
     - Maximum and minimum sources per topic
     - Domain filtering (edu, gov, org, etc.)
     - Crawl depth settings

5. **Start Research**:
   - Select a profile from your dashboard
   - Click "Start Research" to begin the automated research process
   - Monitor real-time progress of topic generation, searches, and content extraction

6. **View Results**:
   - Browse all generated files organized by topic
   - Read downloaded sources
   - Access the final compiled research paper

7. **Save & Load Templates**:
   - Save successful research configurations as templates
   - Quickly start new research using proven settings

## License

This project is licensed under the MIT License - see the LICENSE file for details.
