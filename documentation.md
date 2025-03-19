no test data generation.
no mock data generation.
no mocking anything else.
no mock implementations or mock anything.

it's a research asistant. aim is helping users to do academic researches.
workflow:
    user enters the problem statement.
    asistant shares the problem statement with the LLM model (gemini-2.0-flash-exp) for topics and subtopic suggestions related the problem statement and writes down the list of topics and subtopics.
    asistant asks to user for search engine or web site.
    asistant opens the search engine or web site with selenium.
    asistant gets help from the vision LLM model (gemini-2.0-flash-exp) for detecting search area
    When detecting search area, asistan starts to search about topics and subtopics related the research.
    When asistant finds related results, opens the PDF file and sends it to LLM (gemini-2.0-flash-exp) for extracting research related info
    Collects results for topics and subtopics including citations and references in academic way.
    when saving a subtopic's findings, use academic reference and citation format.
    After every subtopic research is done, asistant writes down the generated subtopic into a file.
    When the research process is completed, combine the topics, subtopics, citations, references etc. into a final paper.

check sources for every topic and subtopic. If there's no result on the web page for selected topic, just ignore it.

add a --focus parameter which user can select which type of files to focus on. for example --focus pdf focuses on pdf files and tries to find enough pdf files. When it's empty I want it to get search results in order. If the search result is a html file, extract text and check if contains useful info.

The project's name is LazyScholar.

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

11. **UI Improvements**: Updated the user interface to reflect the broader focus on various content types rather than just PDFs:
    - Changed "Max PDFs per Topic" to "Max Sources per Topic"
    - Changed "Minimum PDFs per Topic" to "Minimum Sources per Topic"
    - Changed "Require PDF Files" to "Prioritize Document Files"
    - Updated help text to reflect these changes

12. **Output Format Selection**: Added ability to select the format for the final research output:
    - Markdown (default)
    - PDF
    - HTML
    - EPUB
    - Word (DOCX)
    - Plain Text (TXT)

wrapper:

I want to build a Flask app for this project to make it more easy to setup search params. I want users can change the search parameters trough flask interface and can see created files, topics and suctopics files, downloaded pdf files within the user interface and can read them.

Be sure to cover all parameters from the lazy scholar.

don't make any changes in lazy scholar.py file, just make a wrapper.

also save user preferences as user profiles and let users can load previous research profiles easily