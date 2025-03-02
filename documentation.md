no test data generation.
no mock data generation.
no mocking anything else.
no mock implementations or mock anything.

it's a research asistant. aim is helping users to do academic researches.
workflow:
    user enters the problem statement.
    asistant shares the problem statement with the LLM model (gemini-2.0-flash-exp) for topics and subtopic suggestions related the problem statement.
    asistant asks to user for search engine or web site.
    asistant opens the search engine or web site with selenium.
    asistant gets help from the vision LLM model (gemini-2.0-flash-exp) for detecting search area
    When detecting search area, asistan starts to search about topics and subtopics related the research.
    When asistant finds related results, opens the PDF file and sends it to LLM (gemini-2.0-flash-exp) for extracting research related info
    Collects results for topics and subtopics including citations and references in academic way.
    After every subtopic research is done, asistant writes down the generated subtopic into a file.
    When the research process is completed, combine the topics, subtopics, citations, references etc. into a final paper.

check 10 PDF files for every topic and subtopic. If there's no result on the web page for selected topic, just ignore it.

The project's name is LazyScholar.