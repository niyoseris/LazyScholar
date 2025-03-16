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

check 10 PDF files for every topic and subtopic. If there's no result on the web page for selected topic, just ignore it.


add a --focus parameter which user can select which type of files to focus on. for example --focus pdf focuses on pdf files and tries to find enough pdf files. When it's empty I want it to get search results in order. If the search result is a html file, extract text and check if contains useful info.


The project's name is LazyScholar.


wrapper:

I want to build a Flask app for this project to make it more easy to setup search params. I want users can change the search parameters trough flask interface and can see created files, topics and suctopics files, downloaded pdf files within the user interface and can read them.

Be sure to cover all parameters from the lazy scholar.

don't make any changes in lazy scholar.py file, just make a wrapper.

also save user preferences as user profiles and let users can load previous research profiles easily