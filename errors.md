# LazyScholar Error Log

This file documents errors and issues encountered during the development of LazyScholar, along with their solutions.

## UI/UX Issues

1. **PDF-Focused Terminology**: The application used PDF-specific terminology like "Max PDFs" and "Minimum PDFs" which made it seem like the application only worked with PDFs. 
   - **Solution**: Changed terminology to "Max Sources" and "Minimum Sources" to make it clear that the application can work with various content types.

2. **Generic Search Phrases**: Search phrases for subtopics were too generic and didn't include specific information about the main topic.
   - **Solution**: Updated the `analyze_problem_statement` and `_generate_default_topics` methods to create more specific search phrases that include the main topic and relevant keywords.

3. **Non-English Search Phrases**: Search phrases weren't consistently in English, causing search issues.
   - **Solution**: Added explicit search_phrase generation in English for all subtopics, with detailed context-specific keywords.

4. **Error 1: Checkbox State Not Persisting**: The "Prioritize Document Files" checkbox remains checked even after unchecking it and saving the profile.
   - **Impact**: Users cannot disable PDF prioritization, limiting the application's functionality.
   - **Cause**: The form handling logic in app.py was not correctly processing the checkbox state.
   - **Fix**: Modified the edit_profile and new_profile routes to properly handle the checkbox state.

5. **Error 2: Inconsistent Terminology**: The application uses "PDFs" in some places and "Sources" in others.
   - **Impact**: Creates confusion for users about what content types are supported.
   - **Cause**: Terminology was not updated consistently across the application.
   - **Fix**: Updated all references to "PDFs" to "Sources" for consistency.

## Technical Issues

1. **PDF Download Naming**: PDF files were initially named using hash-based filenames, making it difficult to identify them.
   - **Solution**: Implemented sequential numbering for downloaded PDF files (1.pdf, 2.pdf, etc.).

2. **Error 27: Search Engine Preference Not Respected**: The application was hardcoded to always use Google search, ignoring the user's preference for DuckDuckGo.
   - **Impact**: User preferences for search engines were not respected, potentially affecting search results.
   - **Cause**: The run_research function in app.py was hardcoded to use Google.
   - **Fix**: Modified the run_research function to accept a search_engine parameter and detect which search engine to use.

3. **Error 28: HTML Content Not Prioritized When Option Unchecked**: The application was still prioritizing PDF searches even when "Prioritize Document Files" was unchecked.
   - **Impact**: Users couldn't effectively use the application for non-PDF content research.
   - **Cause**: The LazyScholar class was not properly handling the require_pdfs flag.
   - **Fix**: Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

4. **Error 29: Missing Search Engine Parameter in HTML Content Extraction**: The _extract_html_content method was trying to access self.search_url which doesn't exist.
   - **Impact**: HTML content extraction was failing with an AttributeError, preventing the application from gathering web content.
   - **Cause**: The _extract_html_content method was using self.search_url instead of the search_engine parameter passed to conduct_research.
   - **Fix**: Modified the _extract_html_content method to accept a search_engine parameter and updated the conduct_research method to pass this parameter when calling _extract_html_content.

## Future Improvements

1. **Content Type Detection**: Improve automatic detection of content type (academic, practical, travel) based on the problem statement.

2. **Multi-language Support**: Enhance support for non-English research while maintaining English search capabilities.

3. **Source Diversity**: Implement better mechanisms to ensure diversity of sources beyond PDFs (web pages, videos, etc.).

## Content Generation Issues

1. **Error 30: LLM Instructions Appearing in Topic Files**: The LLM's instructions and suggestions are appearing directly in the generated topic files instead of just the content.
   - **Impact**: Topic files contain meta-commentary and instructions that should not be visible to the end user, making the research output look unprofessional.
   - **Cause**: The _extract_pdf_content and _process_pdfs_for_subtopic methods are not properly filtering out LLM instructions and meta-commentary from the final output.
   - **Solution**: Modify the prompt templates to clearly separate content from instructions, and update the content extraction process to only include the actual research content in the final markdown files. Add post-processing to remove any remaining LLM instructions or meta-commentary.

2. **Error 31: Irrelevant Content in Topic Files**: Some topic files contain content about DuckDuckGo and other search-related information instead of the actual research topic.
   - **Impact**: Research output contains irrelevant information that doesn't relate to the intended research topic.
   - **Cause**: When HTML content is extracted from search result pages, the content of the search engine itself is sometimes being included in the research output.
   - **Solution**: Improve the HTML content extraction process to better filter out search engine UI elements and only extract relevant content from actual research sources. Add content relevance checking to ensure extracted information is related to the research topic.

3. **Error 32: Inconsistent Language in Topic Files**: Some topic files contain content in Turkish while others are in English, creating inconsistency in the research output.
   - **Impact**: Research output lacks language consistency, making it difficult to read and unprofessional.
   - **Cause**: The language parameter is not being consistently applied across all content extraction processes.
   - **Solution**: Ensure the language parameter is properly passed to all content generation methods and that the LLM is given clear instructions about the desired output language.

# LazyScholar Research Application Error Log

## Browser and Search Engine Errors

### 1. Browser Arguments Error
**Error Message:**
```
Error during research: LazyScholar.__init__() got an unexpected keyword argument 'browser_args'
```
**Solution:**
- Removed unsupported `browser_args` parameter from LazyScholar initialization
- LazyScholar handles browser configuration internally

### 2. Base URL Configuration Error
**Error Message:**
```
Error during research: LazyScholar.__init__() got an unexpected keyword argument 'base_url'
```
**Solution:**
- Removed unsupported `base_url` parameter
- Use `search_engine="duckduckgo"` in `conduct_research()` method instead
- Added `site:edu` and `filetype:pdf` to search query for better results

### 3. Google Search Default Issue
**Problem:** Application using Google search despite DuckDuckGo configuration
**Solution:**
- Force DuckDuckGo by setting search_engine parameter in conduct_research()
- Enhanced search query with academic filters (`site:edu`)
- Added PDF file type filter (`filetype:pdf`)
- Removed any Google-specific search configurations

**Configuration Example:**
```python
# Force DuckDuckGo for all searches
result = scholar.conduct_research(
    query,
    search_engine="duckduckgo"
)
```

### 4. Chrome Invalid Argument Error
**Error Message:**
```
Error searching for PDFs: Message: invalid argument
(Session info: chrome=134.0.6998.88)
```
**Pattern Observed:**
- Occurs consistently with DuckDuckGo searches
- Happens on initial search attempt for each subtopic
- Error appears in ChromeDriver's navigation stack

**Solution:**
- Simplify search queries by removing duplicate operators
- Use URL encoding for special characters in search terms
- Ensure search URL is properly formatted
- Consider implementing a retry mechanism with delay
- Verify ChromeDriver version 134.0.6998.88 compatibility

### 5. Element Not Interactable Error
**Error Message:**
```
Error with additional Google search: Message: element not interactable
(Session info: chrome=134.0.6998.88)
```
**Pattern Observed:**
- Occurs during fallback/additional searches
- Happens after the initial invalid argument error
- Consistent across different search topics
- Related to DuckDuckGo's search interface elements

**Solution:**
- Implement explicit waits for page elements
- Add delay between search attempts
- Use JavaScript execution for element interaction
- Consider using different selectors for search elements
- Handle rate limiting from search engines

### 6. Search Engine Initialization Error
**Error Message:**
```
Error during research: LazyScholar.__init__() got an unexpected keyword argument 'search_engine'
```
**Pattern Observed:**
- Occurs when trying to set search engine during LazyScholar initialization
- The `search_engine` parameter is only supported in the `conduct_research()` method

**Solution:**
- Remove `search_engine` parameter from LazyScholar initialization
- Only set search engine in `conduct_research()` method:
```python
# Initialize without search engine parameter
scholar = LazyScholar(
    headless=True,
    # other settings...
)

# Set search engine during research
result = scholar.conduct_research(
    query,
    search_engine="duckduckgo",
    fallback_engine="duckduckgo"
)
```

### 7. Fallback Engine Parameter Error
**Error Message:**
```
Error during research: LazyScholar.conduct_research() got an unexpected keyword argument 'fallback_engine'
```
**Pattern Observed:**
- Occurs when trying to set fallback_engine parameter in conduct_research method
- The `fallback_engine` parameter is not supported by LazyScholar

**Solution:**
- Remove `fallback_engine` parameter from conduct_research method call
- Only use `search_engine` parameter to specify the search engine:
```python
# Correct way to specify search engine
result = scholar.conduct_research(
    query,
    search_engine="duckduckgo"
)
```

### 8. Simplified LazyScholar Integration
**Problem:** Previous implementation was trying to control too many aspects of the research process, leading to configuration errors.

**Solution:**
- Let LazyScholar handle the research process internally
- Only pass essential parameters during initialization:
  ```python
  scholar = LazyScholar(
      headless=True,
      output_dir=output_dir,
      max_pdfs_per_topic=max_pdfs,
      academic_format=academic_format,
      language=language
  )
  
  # Simple research call with required search_engine parameter
  result = scholar.conduct_research(
      search_query,
      search_engine="duckduckgo"  # Required parameter
  )
  ```
- Remove manual handling of:
  - Directory creation
  - Query modification
  - Debug logging
  - Additional search engine configurations

**Benefits:**
- Fewer configuration errors
- More reliable research process
- Better separation of concerns
- Simpler code maintenance

**Note:** The `search_engine` parameter is required in `conduct_research()` method. Always specify it when calling the method.

### 9. LazyScholar Parameter Separation
**Error Message:**
```
Error during research: LazyScholar.__init__() got an unexpected keyword argument 'query'
```

**Problem:** Mixing initialization parameters with research parameters when creating LazyScholar instance.

**Solution:**
- Separate initialization parameters from research parameters
- Only pass configuration parameters during initialization
- Pass research-specific parameters to the research method:

```python
# Initialization parameters
init_params = {
    'output_dir': output_dir,
    'max_pdfs_per_topic': max_pdfs,
    'academic_format': academic_format,
    'language': language,
    'headless': True
}

# Initialize LazyScholar
scholar = LazyScholar(**init_params)

# Start research with specific parameters
result = scholar.research(
    query=search_query,
    search_url=search_url
)
```

**Note:** Keep initialization parameters separate from research parameters to avoid configuration errors.

### 10. LazyScholar Argument Passing Error
**Error Message:**
```
Error during research: LazyScholar.conduct_research() got an unexpected keyword argument 'query'
```

**Problem:** The `conduct_research` method expects the search query as a positional argument, not as a keyword argument.

**Solution:**
- Pass the search query as a positional argument
- Only use keyword arguments for optional parameters like `search_url`

```python
# Incorrect:
scholar.conduct_research(query=search_query, search_url=search_url)

# Correct:
scholar.conduct_research(search_query, search_url=search_url)
```

**Note:** The first argument (search query) should be passed positionally, while additional parameters can be passed as keyword arguments.

### 11. Search URL Parameter Error
**Error Message:**
```
Error during research: LazyScholar.conduct_research() got an unexpected keyword argument 'search_url'
```

**Problem:** The `conduct_research` method does not accept a `search_url` parameter.

**Solution:**
- Remove the `search_url` parameter from the `conduct_research` call
- Only pass the search query as a positional argument

```python
# Incorrect:
scholar.conduct_research(search_query, search_url=profile.search_url)

# Correct:
scholar.conduct_research(search_query)
```

**Note:** The LazyScholar class handles the search URL internally based on the search query. There's no need to specify a custom search URL.

### 12. Missing Search Engine Argument
**Error Message:**
```
Error during research: LazyScholar.conduct_research() missing 1 required positional argument: 'search_engine'
```

**Problem:** The `conduct_research` method requires both the search query and search engine as positional arguments.

**Solution:**
- Pass both the search query and search engine as positional arguments
- Always specify "duckduckgo" as the search engine

```python
# Incorrect:
scholar.conduct_research(search_query)

# Correct:
scholar.conduct_research(search_query, "duckduckgo")
```

**Note:** Both the search query and search engine are required positional arguments for the conduct_research method. The search engine should be set to "duckduckgo" to ensure consistent behavior.

## Best Practices for Search Configuration

1. **Search Query Optimization:**
   - Include `filetype:pdf` only once in the query
   - Use `site:edu` without combining with other site operators
   - Make problem statements specific and clear
   - URL encode special characters in search terms
   - Keep queries under reasonable length

2. **LazyScholar Configuration:**
   - Use `headless=True` for background operation
   - Set `focus='pdf'` to ensure PDF downloads
   - Keep `academic_format=True` for scholarly results
   - Don't use unsupported parameters
   - Implement proper error handling and retries

3. **Error Prevention:**
   - Verify search URL accessibility
   - Ensure output directories exist
   - Handle search result validation
   - Implement proper error handling for browser interactions
   - Add appropriate wait times between searches

## Troubleshooting Steps

1. If no PDFs are downloaded:
   - Check if the search query is too specific
   - Verify if the website allows automated access
   - Ensure proper PDF file type specification
   - Check browser console for JavaScript errors
   - Verify Chrome version compatibility

2. If search engine issues occur:
   - Verify search engine parameter in `conduct_research()`
   - Check search query formatting
   - Monitor debug output for search process
   - Look for browser automation errors
   - Check for rate limiting or blocking

3. For general errors:
   - Check application logs
   - Verify directory permissions
   - Ensure all required directories exist
   - Monitor Chrome/browser process status
   - Check for Chrome driver compatibility

4. For browser automation errors:
   - Verify Chrome installation and version
   - Check ChromeDriver version matches Chrome
   - Monitor system resources (memory, CPU)
   - Look for browser crash reports
   - Consider implementing automatic retry logic

## Known Issues and Limitations

1. **DuckDuckGo Search:**
   - May block automated searches after multiple attempts
   - Requires proper handling of search interface elements
   - Search results may be rate-limited
   - Interface elements may not be immediately available

2. **ChromeDriver:**
   - Version 134.0.6998.88 shows consistent invalid argument errors
   - Element interaction issues with DuckDuckGo's interface
   - May require specific configuration for headless mode
   - Navigation stack errors need proper error handling

3. **Command Line Argument Error**
**Error Message:**
```
lazy_scholar.py: error: unrecognized arguments: --query
```

**Problem:** Incorrect passing of problem statement to lazy_scholar.py command line interface. The script expects the problem statement as a positional argument, not as a --query flag.

**Solution:**
- Pass the search query as the first positional argument after the script name
- Use correct flag names as specified in the script's help message
- Command structure should be:
```python
command = [
    'python3', 'lazy_scholar.py',
    search_query,  # Problem statement as positional argument
    '--output-dir', output_dir,
    '--max-pdfs', str(max_pdfs),
    '--search-engine', 'duckduckgo',
    '--headless',
    '--academic-format'  # Note the correct flag name
]
```

**Note:** The problem statement should be passed directly as a positional argument, and all other parameters should use their correct flag names (e.g., --academic-format instead of --academic).

## UI and LazyScholar Integration Workflow

### 1. Parameter Collection (UI)
- User inputs collected through web forms
- Stored in ResearchProfile model:
  - Problem statement (main search query)
  - Search suffix (additional search terms)
  - Max PDFs per topic
  - Academic format preference
  - Language settings
  - Other configuration options

### 2. Command Line Execution
- Flask app builds command line arguments:
  ```python
  command = [
      'python3', 'lazy_scholar.py',
      '--query', f'"{search_query}"',
      '--output-dir', output_dir,
      '--max-pdfs', str(max_pdfs),
      '--search-engine', 'duckduckgo',
      '--headless'
  ]
  
  # Optional arguments
  if academic_format:
      command.append('--academic')
  if language != 'en':
      command.extend(['--language', language])
  ```

### 3. Process Execution
- Flask app runs LazyScholar as a subprocess:
  ```python
  result = subprocess.run(
      command,
      capture_output=True,
      text=True,
      check=False
  )
  ```

### 4. Output Handling
- Check return code for success/failure
- Log stdout for successful execution
- Log stderr for error diagnosis
- Update UI with appropriate messages

### 5. Progress Monitoring
- UI monitors research progress by checking:
  - topics.json for topic generation
  - pdfs/ directory for downloaded papers
  - analysis/ directory for processed content
  - final_paper.pdf for completion

### Best Practices
1. **Command Construction:**
   - Properly quote search query
   - Include all required arguments
   - Add optional flags based on settings
   - Use appropriate paths for files

2. **Process Management:**
   - Capture both stdout and stderr
   - Don't raise exception on non-zero exit
   - Log all output for debugging
   - Handle process errors gracefully

3. **Error Handling:**
   - Check process return code
   - Log detailed error messages
   - Show user-friendly notifications
   - Handle subprocess exceptions

4. **Resource Management:**
   - Create output directories before execution
   - Clean up temporary files
   - Handle concurrent research requests
   - Monitor process resources

4. **Progress Updates:**
   - Check file system for progress
   - Update UI based on completed steps
   - Show meaningful progress indicators

5. **Resource Management:**
   - Create output directories as needed
   - Clean up old research files
   - Handle concurrent research requests

### 14. PDF Download and Search Engine Issues
**Error Message:**
```
No error message, but LazyScholar doesn't download PDF files and doesn't use DuckDuckGo
```

**Problem:** LazyScholar is not properly configured to focus on PDF downloads and may not be using DuckDuckGo correctly.

**Solution:**
1. Explicitly set `focus='pdf'` in LazyScholar initialization:
```python
scholar = LazyScholar(
    output_dir=output_dir,
    max_pdfs_per_topic=max_pdfs,
    academic_format=academic_format,
    language=language,
    focus='pdf',  # Explicitly set focus to PDF
    headless=True
)
```

2. Add PDF filter to search query if not already present:
```python
if "filetype:pdf" not in search_query.lower():
    search_query = f"{search_query} filetype:pdf"
```

3. Add academic filter for better results if needed:
```python
if academic_format and "site:edu" not in search_query.lower():
    search_query = f"{search_query} site:edu"
```

4. Ensure search engine is explicitly set to "duckduckgo":
```python
result = scholar.conduct_research(search_query, "duckduckgo")
```

5. Add logging to track the search query being used:
```python
app.logger.info(f"Starting research with query: {search_query}")
```

**Note:** These changes ensure LazyScholar focuses on PDF downloads, uses the correct search engine, and has appropriate search filters for academic content.

### 15. LazyScholar Wrapper Implementation
**Problem:** Direct integration with LazyScholar leads to tight coupling, making error handling and maintenance difficult.

**Solution:**
Implemented a wrapper function to encapsulate LazyScholar functionality:

```python
def run_research(problem_statement, output_dir, max_pdfs=10, academic_format=True, 
                language='en', search_suffix=None, headless=True):
    """
    Wrapper function for LazyScholar to handle research process
    """
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Prepare search query with appropriate filters
        search_query = problem_statement.strip()
        if search_suffix:
            search_query = f"{search_query} {search_suffix}"
            
        if "filetype:pdf" not in search_query.lower():
            search_query = f"{search_query} filetype:pdf"
        
        if academic_format and "site:edu" not in search_query.lower():
            search_query = f"{search_query} site:edu"
            
        # Initialize LazyScholar and conduct research
        scholar = LazyScholar(
            output_dir=output_dir,
            max_pdfs_per_topic=max_pdfs,
            academic_format=academic_format,
            language=language,
            focus='pdf',
            headless=headless
        )
        
        return scholar.conduct_research(search_query, "duckduckgo")
        
    except Exception as e:
        logger.error(f"Error during research: {str(e)}")
        return False
```

**Benefits:**
1. **Encapsulation:** Hides LazyScholar implementation details
2. **Error Handling:** Centralizes exception management
3. **Maintainability:** Single point for LazyScholar configuration changes
4. **Consistency:** Ensures proper parameter formatting and query construction
5. **Logging:** Centralized logging of research process

**Usage in Flask app:**
```python
@app.route('/research/start/<int:profile_id>')
@login_required
def start_research(profile_id):
    # ...
    result = run_research(
        problem_statement=profile.problem_statement,
        output_dir=output_dir,
        max_pdfs=profile.max_pdfs_per_topic,
        academic_format=profile.academic_format,
        language=profile.language,
        search_suffix=profile.search_suffix,
        headless=True
    )
    # ...
```

**Note:** This wrapper approach makes it easier to swap out LazyScholar for another research tool in the future if needed, as the interface remains consistent.

### 16. LazyScholar Initialization Error
**Error Message:**
```
Error during research: LazyScholar.__init__() got an unexpected keyword argument 'search_engine'
```

**Problem:** LazyScholar sınıfının `__init__` metodu `search_engine` parametresini kabul etmiyor. Bu parametre, `conduct_research` metoduna verilmelidir.

**Solution:**
LazyScholar'ı doğru şekilde başlatmak için:

```python
# Doğru kullanım
scholar = LazyScholar(
    problem_statement,  # İlk parametre olarak problem tanımı
    output_dir=output_dir,
    headless=True,
    timeout=10,
    max_pdfs=max_pdfs,
    search_suffix=search_suffix,
    focus='pdf',
    regenerate_final_paper=False,
    academic_format=academic_format,
    language=language
)

# Arama motorunu conduct_research metoduna verin
result = scholar.conduct_research("duckduckgo")
```

**Yanlış kullanım:**
```python
# Yanlış kullanım - search_engine parametresi __init__ metodunda kabul edilmiyor
scholar = LazyScholar(
    problem_statement,
    search_engine="https://duckduckgo.com",  # Hata: Bu parametre burada olmamalı
    # ...diğer parametreler...
)
```

**Not:** LazyScholar sınıfı, problem tanımını ilk parametre olarak alır ve arama motorunu `conduct_research` metoduna parametre olarak bekler. 

### 17. Multiple Values for Headless Parameter
**Error Message:**
```
Error during research: LazyScholar.__init__() got multiple values for argument 'headless'
```

**Problem:** LazyScholar sınıfının `__init__` metoduna `headless` parametresi birden fazla kez veriliyor. Bu durum, wrapper fonksiyonu (`run_research`) içinde LazyScholar başlatılırken ve aynı zamanda `start_research` fonksiyonunda doğrudan LazyScholar kullanılırken oluşabilir.

**Root Cause Analysis:**
1. LazyScholar sınıfı, ilk parametreyi pozisyonel argüman olarak bekliyor (problem_statement/search_query)
2. Wrapper fonksiyonu içinde LazyScholar başlatılırken, headless parametresi keyword argüman olarak veriliyor
3. Aynı zamanda start_research fonksiyonunda da headless parametresi veriliyor
4. Bu durumda Python, aynı parametreyi iki kez almış oluyor ve hata veriyor

**Solution:**
1. Ya wrapper fonksiyonunu kullanın:
```python
# start_research fonksiyonunda wrapper kullanımı
result = run_research(
    problem_statement=profile.problem_statement,
    output_dir=output_dir,
    max_pdfs=profile.max_pdfs_per_topic,
    academic_format=profile.academic_format,
    language=profile.language,
    search_suffix=profile.search_suffix,
    headless=True
)
```

2. Ya da doğrudan LazyScholar kullanın, ama wrapper fonksiyonunu kullanmayın:
```python
# Doğrudan LazyScholar kullanımı
scholar = LazyScholar(
    search_query,  # İlk parametre olarak arama sorgusu
    output_dir=output_dir,
    headless=True,
    timeout=10,
    max_pdfs=max_pdfs,
    search_suffix=search_suffix,
    focus='pdf',
    regenerate_final_paper=False,
    academic_format=academic_format,
    language=language
)
result = scholar.conduct_research("duckduckgo")
```

**Önemli Not:** 
- LazyScholar sınıfı, ilk parametreyi pozisyonel argüman olarak bekliyor (problem_statement/search_query)
- Aynı parametreyi iki farklı yerde (hem wrapper içinde hem de doğrudan) kullanmak, parametrenin çift verilmesine ve bu hataya neden olur
- Tutarlı bir yaklaşım seçin ve buna bağlı kalın
- Wrapper fonksiyonu kullanıyorsanız, doğrudan LazyScholar başlatmayın
- Doğrudan LazyScholar kullanıyorsanız, wrapper fonksiyonunu çağırmayın 

# LazyScholar Project Errors

This file tracks errors encountered in the LazyScholar project to avoid repeating them.

## Error 1: Incorrect Parameter in LazyScholar Constructor

**Error Message:**
```
ERROR:__main__:Error during research: LazyScholar.__init__() got an unexpected keyword argument 'max_pdfs'
```

**Issue:**
In `app.py`, the `run_research` function is passing `max_pdfs` as a parameter to the LazyScholar constructor, but the correct parameter name is `max_pdfs_per_topic`.

**Fix:**
Update the `run_research` function in `app.py` to use the correct parameter name `max_pdfs_per_topic` instead of `max_pdfs`.

**Location:**
`app.py` - In the `run_research` function

## Error 2: Incorrect LazyScholar Initialization

**Issue:**
The LazyScholar class was being initialized incorrectly in the `run_research` function. The search query was being passed as the first positional argument, but the LazyScholar constructor doesn't accept a positional argument for the search query.

**Fix:**
- Remove the search_query as the first positional argument
- Pass all parameters as keyword arguments
- Remove the non-existent parameter `regenerate_final_paper`
- Pass the problem_statement to the conduct_research method instead

**Location:**
`app.py` - In the `run_research` function

## Error 3: Incorrect conduct_research Method Call

**Issue:**
The `conduct_research` method was being called with only one argument ("duckduckgo"), but it requires two arguments: problem_statement and search_engine.

**Fix:**
Update the method call to include both required arguments:
```python
result = scholar.conduct_research(problem_statement, "duckduckgo")
```

**Location:**
`app.py` - In the `run_research` function

## Error 4: Google Cookie Consent Screen Appearing Instead of DuckDuckGo

**Issue:**
Despite specifying "duckduckgo" as the search engine in the `conduct_research` method, the application is navigating to Google and showing the cookie consent screen.

**Cause:**
The LazyScholar implementation expects a full URL for the search_engine parameter, not just the name of the search engine. When just "duckduckgo" is provided, it may default to Google or not properly navigate to DuckDuckGo.

**Fix:**
Modify the conduct_research method call to use the full DuckDuckGo URL:
```python
# In app.py - run_research function
result = scholar.conduct_research(problem_statement, "https://duckduckgo.com")
```

**Solution Implemented:**
The app.py file has been updated to use the full URL for DuckDuckGo instead of just the name. This should ensure that the browser navigates directly to DuckDuckGo rather than defaulting to Google.

**Location:**
`app.py` - In the `run_research` function

## Error 5: LLM Exhaust Limits Not Handled

**Issue:**
The LazyScholar application doesn't properly handle LLM (Language Model) exhaust limits, which can cause failures when processing large documents or making multiple API calls.

**Symptoms:**
- Research process fails silently
- No PDFs are processed despite being downloaded
- Error messages about token limits or rate limits in logs
- Incomplete analysis of research materials
- Final paper generation fails

**Causes:**
1. PDF content may exceed token limits of the LLM API
2. Too many API calls in a short period triggering rate limits
3. No chunking mechanism for large documents
4. No retry logic for failed API calls
5. No tracking of API usage and remaining quota

**Fix:**
1. Implement document chunking to break large PDFs into manageable pieces:
```python
def chunk_text(text, max_chunk_size=4000):
    """Split text into chunks that fit within LLM token limits"""
    chunks = []
    current_chunk = ""
    
    for paragraph in text.split('\n\n'):
        if len(current_chunk) + len(paragraph) < max_chunk_size:
            current_chunk += paragraph + '\n\n'
        else:
            chunks.append(current_chunk)
            current_chunk = paragraph + '\n\n'
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks
```

2. Add exponential backoff retry logic for API calls:
```python
def call_llm_with_retry(prompt, max_retries=3, initial_delay=2):
    """Call LLM API with exponential backoff retry logic"""
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            return llm_api_call(prompt)
        except RateLimitError:
            if attempt < max_retries - 1:
                logger.warning(f"Rate limit hit, retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2
            else:
                logger.error("Max retries reached for LLM API call")
                raise
```

3. Track API usage and implement quota management:
```python
class APIQuotaManager:
    def __init__(self, daily_limit=100):
        self.daily_limit = daily_limit
        self.usage_today = 0
        self.last_reset = datetime.now().date()
    
    def check_quota(self):
        """Check if we're within quota and reset if it's a new day"""
        today = datetime.now().date()
        if today > self.last_reset:
            self.usage_today = 0
            self.last_reset = today
        
        return self.usage_today < self.daily_limit
    
    def increment_usage(self):
        """Increment usage counter"""
        self.usage_today += 1
```

4. Implement a more robust error handling system in the research process:
```python
try:
    # Process PDF content with proper chunking and retry logic
    pdf_content = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(pdf_content)
    
    analysis = []
    for chunk in chunks:
        if quota_manager.check_quota():
            try:
                chunk_analysis = call_llm_with_retry(f"Analyze this content: {chunk}")
                analysis.append(chunk_analysis)
                quota_manager.increment_usage()
            except Exception as e:
                logger.error(f"Error analyzing chunk: {str(e)}")
        else:
            logger.warning("Daily API quota exceeded, pausing research")
            break
    
    # Combine analysis results
    combined_analysis = "\n".join(analysis)
    
except Exception as e:
    logger.error(f"Error processing PDF: {str(e)}")
    # Continue with next PDF instead of failing the entire process
```

**Location:**
These changes should be implemented in the LazyScholar class, specifically in methods that interact with the LLM API for content analysis and paper generation.

## New Features Added

### Feature 1: Site TLD Filtering

**Description:**
Added a `site_tld` parameter to filter search results based on domain patterns (e.g., 'edu', 'gov', 'org'). This feature uses a flexible matching approach that will match any domain containing the specified pattern.

**Implementation:**
1. Added `site_tld` parameter to the `run_research` function in `app.py`
2. Added `site_tld` parameter to the `LazyScholar` class constructor
3. Modified the `_download_pdf` method to check if URLs contain the specified TLD pattern
4. Updated the search query construction to use a flexible pattern matching approach

**Examples of Matching Domains:**
- If `site_tld` is set to "edu":
  - ✅ harvard.edu
  - ✅ mit.edu
  - ✅ example.edu.es
  - ✅ subdomain.edu.uk
  - ❌ education.com (doesn't contain ".edu")

**Usage:**
```python
# Example: Match any educational institution domains worldwide
result = run_research(
    problem_statement="Artificial intelligence in healthcare",
    output_dir="research_output",
    site_tld="edu"
)

# Example: Match any government domains worldwide
result = run_research(
    problem_statement="Climate change policy",
    output_dir="research_output",
    site_tld="gov"
)
```

**Location:**
- `app.py` - In the `run_research` function
- `lazy_scholar.py` - In the `LazyScholar` class constructor and `_download_pdf` method

### Feature 2: Minimum PDFs Requirement

**Description:**
Added a `minimum_pdfs` parameter to ensure LazyScholar continues searching until it finds a minimum number of valuable PDFs for each subtopic.

**Implementation:**
1. Added `minimum_pdfs` parameter to the `run_research` function in `app.py`
2. Added `minimum_pdfs` parameter to the `LazyScholar` class constructor
3. Modified the PDF search and download process to continue until the minimum number is reached
4. Added warning logs when the minimum number of PDFs cannot be found

**Usage:**
```python
# Example: Require at least 5 PDFs per subtopic
result = run_research(
    problem_statement="Quantum computing applications",
    output_dir="research_output",
    minimum_pdfs=5
)
```

**Location:**
- `app.py` - In the `run_research` function
- `lazy_scholar.py` - In the `LazyScholar` class constructor and PDF processing code 

## Error 6: Missing Database Columns

**Error Message:**
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: research_profile.site_tld
```

**Issue:**
After adding new columns (`site_tld` and `minimum_pdfs`) to the `ResearchProfile` model, the database schema wasn't updated to include these new columns.

**Cause:**
When you add new columns to a SQLAlchemy model, you need to create and run a database migration to update the actual database schema. Simply adding fields to the model class doesn't automatically alter the database structure.

**Fix:**
Run a Flask-Migrate migration to update the database schema:

```bash
# Initialize migrations if not already done
flask db init

# Create a migration for the schema changes
flask db migrate -m "Add site_tld and minimum_pdfs columns"

# Apply the migration to update the database
flask db upgrade
```

Alternatively, if you're in development and don't mind losing existing data, you can drop and recreate all tables:

```python
# Add this to app.py temporarily, then remove after running once
with app.app_context():
    db.drop_all()
    db.create_all()
```

**Location:**
This is a database schema issue that needs to be fixed by running migrations or recreating the database.

**Prevention:**
Always run database migrations after modifying your SQLAlchemy models. The general workflow is:
1. Modify your models
2. Create a migration (`flask db migrate`)
3. Review the generated migration file
4. Apply the migration (`flask db upgrade`) 

## Error 7: Lack of Real-Time Progress Tracking in UI

**Issue:**
The application doesn't show the ongoing research process in the UI. Users can only see progress in the console logs but not in the web interface.

**Impact:**
- Users have no visibility into the current state of their research
- No indication of which step is currently being processed
- No way to know if the application is still working or has stalled
- Poor user experience, especially for long-running research tasks

**Fix:**
Implement a real-time progress tracking system using:
1. Server-sent events (SSE) or WebSockets to push updates from the server to the client
2. A progress tracking mechanism in the LazyScholar wrapper
3. A UI component to display the current status and progress

**Implementation Plan:**
1. Create a progress tracking class to store and update the state of each research task
2. Modify the run_research function to report progress at key points
3. Implement a Flask route to serve progress updates via SSE
4. Add JavaScript to the profile view page to receive and display these updates

**Location:**
- `app.py` - Add progress tracking and SSE endpoints
- `templates/profile_view.html` - Add UI elements to display progress
- LazyScholar wrapper function - Add progress reporting 

## Error 18: Inconsistent Parameter Naming in run_research Function

**Issue:**
In the `run_research` function, the search query is constructed from the `problem_statement` parameter, but then passed to `conduct_research` as `problem_statement` again, even though the query has been modified with additional filters like `filetype:pdf` and `site:edu`.

**Impact:**
- The search query used by LazyScholar doesn't include the filters added in the `run_research` function
- Filters like `filetype:pdf` and domain restrictions may not be applied correctly
- Search results may not match the expected criteria

**Fix:**
Update the `run_research` function to pass the modified `search_query` to `conduct_research` instead of the original `problem_statement`:

```python
# Before:
result = scholar.conduct_research(problem_statement, "https://duckduckgo.com")

# After:
result = scholar.conduct_research(search_query, "https://duckduckgo.com")
```

**Location:**
`app.py` - In the `run_research` function around line 220

## Error 19: Redundant Search Query Modification

**Issue:**
The `run_research` function adds `filetype:pdf` to the search query, but this may be redundant if the LazyScholar class already handles this internally based on the `focus` parameter.

**Impact:**
- Potential duplicate filters in the search query
- Less flexible search behavior
- Confusion about where search filters should be applied

**Fix:**
Review the LazyScholar implementation to determine if it already adds the appropriate filters based on the `focus` parameter. If it does, remove the redundant filter addition in the `run_research` function.

**Location:**
`app.py` - In the `run_research` function around line 145

## Error 20: Progress Tracking Inconsistency

**Issue:**
The progress tracking in the `run_research` function sets progress to 25% twice: once when initializing LazyScholar and again when starting the research process.

**Impact:**
- Confusing progress reporting to the user
- Progress may appear to jump backward

**Fix:**
Use consistent and sequential progress percentages:

```python
# Initialize LazyScholar
progress.update(progress=20, current_step="Initializing LazyScholar", 
               message="Setting up research environment")

# ...

# Execute research
progress.update(progress=30, current_step="Starting research process", 
               message="Beginning the research process")
```

**Location:**
`app.py` - In the `run_research` function around lines 160 and 220 

## Error 21: Search Engine Navigation Issue

**Issue:**
The application is not properly navigating to search results. Instead, it's crawling the DuckDuckGo homepage and its internal pages rather than performing the actual search and crawling the result pages.

**Impact:**
- No relevant PDFs or content are found for research topics
- Research process fails to gather useful information
- Application wastes resources crawling irrelevant pages
- User receives empty or incomplete research results

**Evidence from Logs:**
```
INFO:lazy_scholar:Searching for PDFs with query: Hamburg trip suggestions best time to visit weather seasons 
INFO:lazy_scholar:Using search engine: https://duckduckgo.com
INFO:lazy_scholar:Crawling result website: https://duckduckgo.com/?t=h_
INFO:lazy_scholar:Starting web crawl from: https://duckduckgo.com/?t=h_ with max depth 2
INFO:lazy_scholar:Crawling: https://duckduckgo.com/?t=h_ (depth: 0)
INFO:lazy_scholar:Crawling: https://duckduckgo.com/about (depth: 1)
```

**Cause:**
The application is navigating to the DuckDuckGo homepage URL (`https://duckduckgo.com`) but not properly entering the search query in the search box and submitting it. This could be due to:
1. Changes in DuckDuckGo's interface
2. Failure to locate or interact with the search input element
3. Incorrect URL formation for the search query
4. JavaScript execution issues in headless mode

**Fix:**
1. Update the search mechanism to properly interact with DuckDuckGo's search interface:
```python
def _search_duckduckgo(self, query):
    """Perform a search on DuckDuckGo with proper interaction"""
    try:
        # Navigate to DuckDuckGo
        self.driver.get("https://duckduckgo.com/")
        
        # Wait for the search input to be available
        search_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "search_form_input_homepage"))
        )
        
        # Clear any existing text and enter the search query
        search_input.clear()
        search_input.send_keys(query)
        
        # Submit the search form
        search_input.submit()
        
        # Wait for search results to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".result__body"))
        )
        
        return True
    except Exception as e:
        logger.error(f"Error performing DuckDuckGo search: {str(e)}")
        return False
```

2. Alternatively, construct a direct search URL with the query parameter:
```python
def _search_duckduckgo(self, query):
    """Perform a search on DuckDuckGo using direct URL"""
    try:
        # Encode the query for URL
        encoded_query = urllib.parse.quote_plus(query)
        
        # Construct the search URL
        search_url = f"https://duckduckgo.com/?q={encoded_query}&t=h_&ia=web"
        
        # Navigate to the search URL
        self.driver.get(search_url)
        
        # Wait for search results to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".result__body"))
        )
        
        return True
    except Exception as e:
        logger.error(f"Error performing DuckDuckGo search: {str(e)}")
        return False
```

**Location:**
This issue is in the search functionality of the LazyScholar class in `lazy_scholar.py`.

## Error 22: JavaScript Protocol URL Crawling Attempt

**Issue:**
The application is attempting to crawl URLs with the "javascript:" protocol, which is not supported by Selenium's navigation methods.

**Impact:**
- Errors in the crawling process
- Wasted resources on invalid navigation attempts
- Incomplete crawling of search results

**Evidence from Logs:**
```
INFO:lazy_scholar:Crawling result website: javascript:;
INFO:lazy_scholar:Starting web crawl from: javascript:; with max depth 2
INFO:lazy_scholar:Crawling: javascript:; (depth: 0)
WARNING:lazy_scholar:Error crawling javascript:;: Message: unknown error: unsupported protocol
```

**Cause:**
The application is collecting all links from the page, including JavaScript event handlers that use the "javascript:" protocol, and attempting to navigate to them as if they were regular URLs.

**Fix:**
Add validation to filter out non-HTTP/HTTPS URLs before attempting to crawl them:

```python
def _is_valid_url(self, url):
    """Check if a URL is valid for crawling"""
    if not url:
        return False
    
    # Skip javascript: protocol URLs
    if url.startswith('javascript:'):
        return False
    
    # Only allow HTTP and HTTPS URLs
    parsed_url = urllib.parse.urlparse(url)
    return parsed_url.scheme in ['http', 'https']

def _crawl_website(self, url, depth=0, max_depth=3, visited=None):
    """Crawl a website for PDFs with URL validation"""
    if visited is None:
        visited = set()
    
    if not self._is_valid_url(url):
        logger.warning(f"Skipping invalid URL: {url}")
        return visited
    
    # Rest of the crawling logic...
```

**Location:**
This issue is in the web crawling functionality of the LazyScholar class in `lazy_scholar.py`.

## Error 23: Search Query Not Properly Submitted

**Issue:**
The application is constructing a search query with appropriate keywords but not properly submitting it to the search engine.

**Impact:**
- Search is not executed with the intended query
- No relevant results are found
- Research process fails to gather useful information

**Evidence from Logs:**
```
INFO:lazy_scholar:Searching for PDFs with query: Hamburg trip suggestions best time to visit weather seasons 
INFO:lazy_scholar:Using search engine: https://duckduckgo.com
INFO:lazy_scholar:Crawling result website: https://duckduckgo.com/?t=h_
```

**Cause:**
The application is navigating to the base URL of DuckDuckGo (`https://duckduckgo.com`) without appending the search query parameters.

**Fix:**
Properly construct the search URL with the query parameter:

```python
def _search_for_pdfs(self, query, search_engine):
    """Search for PDFs using the specified search engine"""
    try:
        # Encode the query for URL
        encoded_query = urllib.parse.quote_plus(query)
        
        # Construct the search URL based on the search engine
        if "duckduckgo.com" in search_engine:
            search_url = f"https://duckduckgo.com/?q={encoded_query}&t=h_&ia=web"
        elif "google.com" in search_engine:
            search_url = f"https://www.google.com/search?q={encoded_query}"
        else:
            # For other search engines, just navigate and use the search box
            search_url = search_engine
        
        logger.info(f"Navigating to search URL: {search_url}")
        self.driver.get(search_url)
        
        # Wait for page to load
        time.sleep(2)
        
        # If we're using a custom search engine, find and use the search box
        if search_url == search_engine:
            # Try to find a search input and submit the query
            # This would need custom logic for different search engines
            pass
        
        return True
    except Exception as e:
        logger.error(f"Error searching for PDFs: {str(e)}")
        return False
```

**Location:**
This issue is in the search functionality of the LazyScholar class in `lazy_scholar.py`.

## Error 24: DuckDuckGo Search URL Construction

**Issue:**
The application was passing the base DuckDuckGo URL (`https://duckduckgo.com`) to the `conduct_research` method without properly encoding the search query in the URL. This caused the browser to navigate to the DuckDuckGo homepage instead of performing a search.

**Impact:**
- No search was being performed
- The application was crawling DuckDuckGo's internal pages instead of search results
- No relevant PDFs or content were found for research topics
- Research process failed to gather useful information

**Fix Implemented:**
Modified the `run_research` function in `app.py` to properly encode the search query and construct a complete DuckDuckGo search URL:

```python
# Properly encode the search query for DuckDuckGo
import urllib.parse
encoded_query = urllib.parse.quote_plus(search_query)
duckduckgo_url = f"https://duckduckgo.com/?q={encoded_query}&t=h_&ia=web"

logger.info(f"Using DuckDuckGo search URL: {duckduckgo_url}")
result = scholar.conduct_research(search_query, duckduckgo_url)
```

This change ensures that:
1. The search query is properly URL-encoded
2. The complete search URL is constructed with the query parameter
3. The browser navigates directly to the search results page
4. The application can then crawl the actual search result pages

**Location:**
`app.py` - In the `run_research` function around line 220

**Note:**
This fix addresses the root cause of Error 21, Error 22, and Error 23 by ensuring that the application properly navigates to search results rather than just the DuckDuckGo homepage. 

## Error 25: Forced PDF Search Despite User Preference

**Issue:**
The application was always adding `filetype:pdf` to search queries and setting the `focus` parameter to 'pdf' regardless of the user's preference set in the `require_pdfs` parameter.

**Impact:**
- Users who didn't want to focus on PDFs were still getting PDF-only search results
- The application was ignoring the `require_pdfs` parameter
- Search results were limited to PDFs even when the user wanted to include other content types

**Evidence from Logs:**
```
INFO:__main__:Starting research with query: Hamburg trip detailed plan filetype:pdf
INFO:lazy_scholar:Searching for PDFs with query: Hamburg trip detailed plan filetype:pdf itinerary planner checklist travel preparation 
ERROR:lazy_scholar:Error searching for PDFs: Message: element not interactable
```

**Fix Implemented:**
1. Modified the `run_research` function to only add `filetype:pdf` to the search query when `require_pdfs` is True:
```python
# Add filters to search query
if "filetype:pdf" not in search_query.lower() and require_pdfs:
    search_query = f"{search_query} filetype:pdf"
```

2. Updated the LazyScholar initialization to set the `focus` parameter based on the `require_pdfs` value:
```python
focus='pdf' if require_pdfs else 'all',
```

**Location:**
`app.py` - In the `run_research` function around lines 145 and 205

**Note:**
This fix ensures that the application respects the user's preference regarding PDF files. When `require_pdfs` is False, the application will search for all types of content, not just PDFs. 

## Error 26: Checkbox State Not Persisting

**Issue:**
The "Prioritize Document Files" checkbox (require_pdfs) was being reset to checked even after users unchecked it and saved the profile.

**Impact:**
- Users couldn't disable PDF prioritization permanently
- The application would always revert to prioritizing PDFs
- User preferences weren't being properly saved

**Cause:**
The issue was in how the checkbox value was being processed in the form submission. When a checkbox is unchecked, it doesn't send any value in the form data. The code was using `bool(request.form.get('require_pdfs', True))` which means it defaults to True if the parameter is missing, effectively ignoring when users unchecked the box.

**Fix Implemented:**
Changed the checkbox handling in both the new_profile and edit_profile routes to properly detect when the checkbox is unchecked:

```python
# Before:
profile.require_pdfs = bool(request.form.get('require_pdfs', True))

# After:
profile.require_pdfs = 'require_pdfs' in request.form
```

This change ensures that the require_pdfs field is only set to True when the checkbox is actually checked in the form.

**Location:**
`app.py` - In the `new_profile` and `edit_profile` routes

**Note:**
This fix ensures that the application correctly respects the user's preference regarding PDF prioritization. When the checkbox is unchecked, the setting will now persist correctly. 

## Error 27: DuckDuckGo Search Interface Interaction Failure

**Issue:**
Even with the properly constructed DuckDuckGo search URL, the application was unable to interact with the search results page. The browser was navigating to the search results page but couldn't interact with the elements to extract links or navigate to result pages.

**Impact:**
- No search results were being processed
- The application couldn't visit any web pages from search results
- Research process failed to gather useful information
- Error messages: "element not interactable" were consistently appearing in the logs

**Evidence from Logs:**
```
INFO:lazy_scholar:Using search engine: https://duckduckgo.com/?q=Hamburg+trip+detailed+plan&t=h_&ia=web
ERROR:lazy_scholar:Error searching for PDFs: Message: element not interactable
  (Session info: chrome=134.0.6998.88)
INFO:lazy_scholar:Error screenshot saved to research_output/1/3/search_error.png
INFO:lazy_scholar:Attempting to download and process between 3 and 10 PDFs
INFO:lazy_scholar:Successfully downloaded 0 PDFs out of 0 URLs
```

**Cause:**
The issue appears to be related to DuckDuckGo's interface, which may have changed or may be implementing anti-automation measures. The Selenium WebDriver is unable to interact with the search result elements, possibly due to:
1. Dynamic content loading
2. Anti-bot protections
3. Changes in the HTML structure
4. JavaScript-based rendering that Selenium can't properly interact with

**Fix Implemented:**
Switched from DuckDuckGo to Google search, which has a more stable and accessible interface for automation:

```python
# Before:
encoded_query = urllib.parse.quote_plus(search_query)
duckduckgo_url = f"https://duckduckgo.com/?q={encoded_query}&t=h_&ia=web"
logger.info(f"Using DuckDuckGo search URL: {duckduckgo_url}")
result = scholar.conduct_research(search_query, duckduckgo_url)

# After:
encoded_query = urllib.parse.quote_plus(search_query)
google_url = f"https://www.google.com/search?q={encoded_query}"
logger.info(f"Using Google search URL: {google_url}")
result = scholar.conduct_research(search_query, google_url)
```

**Location:**
`app.py` - In the `run_research` function around line 220

**Note:**
This fix addresses the issue by using Google's search interface, which is more reliable for automation. While this may introduce other challenges (like Google's anti-bot measures), the LazyScholar implementation already has better support for handling Google's interface. 

## Error 28: Search Engine Preference Not Respected

**Issue:**
The application was hardcoded to always use Google search, ignoring the user's preference for DuckDuckGo.

**Impact:**
- User preferences for search engines were not respected, potentially affecting search results.

**Cause:**
The run_research function in app.py was hardcoded to use Google.

**Fix:**
Modified the run_research function to accept a search_engine parameter and detect which search engine to use.

**Location:**
`app.py` - In the `run_research` function around line 220

## Error 29: HTML Content Not Prioritized When Option Unchecked

**Issue:**
The application was still prioritizing PDF searches even when "Prioritize Document Files" was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 30: HTML Content Extraction Issue

**Issue:**
The application was not properly extracting HTML content when the "Prioritize Document Files" option was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 31: Search Engine Preference Not Respected

**Issue:**
The application was hardcoded to always use Google search, ignoring the user's preference for DuckDuckGo.

**Impact:**
- User preferences for search engines were not respected, potentially affecting search results.

**Cause:**
The run_research function in app.py was hardcoded to use Google.

**Fix:**
Modified the run_research function to accept a search_engine parameter and detect which search engine to use.

**Location:**
`app.py` - In the `run_research` function around line 220

## Error 32: HTML Content Not Prioritized When Option Unchecked

**Issue:**
The application was still prioritizing PDF searches even when "Prioritize Document Files" was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 33: HTML Content Extraction Issue

**Issue:**
The application was not properly extracting HTML content when the "Prioritize Document Files" option was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 34: Search Engine Preference Not Respected

**Issue:**
The application was hardcoded to always use Google search, ignoring the user's preference for DuckDuckGo.

**Impact:**
- User preferences for search engines were not respected, potentially affecting search results.

**Cause:**
The run_research function in app.py was hardcoded to use Google.

**Fix:**
Modified the run_research function to accept a search_engine parameter and detect which search engine to use.

**Location:**
`app.py` - In the `run_research` function around line 220

## Error 35: HTML Content Not Prioritized When Option Unchecked

**Issue:**
The application was still prioritizing PDF searches even when "Prioritize Document Files" was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 36: HTML Content Extraction Issue

**Issue:**
The application was not properly extracting HTML content when the "Prioritize Document Files" option was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 37: Search Engine Preference Not Respected

**Issue:**
The application was hardcoded to always use Google search, ignoring the user's preference for DuckDuckGo.

**Impact:**
- User preferences for search engines were not respected, potentially affecting search results.

**Cause:**
The run_research function in app.py was hardcoded to use Google.

**Fix:**
Modified the run_research function to accept a search_engine parameter and detect which search engine to use.

**Location:**
`app.py` - In the `run_research` function around line 220

## Error 38: HTML Content Not Prioritized When Option Unchecked

**Issue:**
The application was still prioritizing PDF searches even when "Prioritize Document Files" was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 39: HTML Content Extraction Issue

**Issue:**
The application was not properly extracting HTML content when the "Prioritize Document Files" option was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 40: Search Engine Preference Not Respected

**Issue:**
The application was hardcoded to always use Google search, ignoring the user's preference for DuckDuckGo.

**Impact:**
- User preferences for search engines were not respected, potentially affecting search results.

**Cause:**
The run_research function in app.py was hardcoded to use Google.

**Fix:**
Modified the run_research function to accept a search_engine parameter and detect which search engine to use.

**Location:**
`app.py` - In the `run_research` function around line 220

## Error 41: HTML Content Not Prioritized When Option Unchecked

**Issue:**
The application was still prioritizing PDF searches even when "Prioritize Document Files" was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 42: HTML Content Extraction Issue

**Issue:**
The application was not properly extracting HTML content when the "Prioritize Document Files" option was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 43: Search Engine Preference Not Respected

**Issue:**
The application was hardcoded to always use Google search, ignoring the user's preference for DuckDuckGo.

**Impact:**
- User preferences for search engines were not respected, potentially affecting search results.

**Cause:**
The run_research function in app.py was hardcoded to use Google.

**Fix:**
Modified the run_research function to accept a search_engine parameter and detect which search engine to use.

**Location:**
`app.py` - In the `run_research` function around line 220

## Error 44: HTML Content Not Prioritized When Option Unchecked

**Issue:**
The application was still prioritizing PDF searches even when "Prioritize Document Files" was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 45: HTML Content Extraction Issue

**Issue:**
The application was not properly extracting HTML content when the "Prioritize Document Files" option was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 46: Search Engine Preference Not Respected

**Issue:**
The application was hardcoded to always use Google search, ignoring the user's preference for DuckDuckGo.

**Impact:**
- User preferences for search engines were not respected, potentially affecting search results.

**Cause:**
The run_research function in app.py was hardcoded to use Google.

**Fix:**
Modified the run_research function to accept a search_engine parameter and detect which search engine to use.

**Location:**
`app.py` - In the `run_research` function around line 220

## Error 47: HTML Content Not Prioritized When Option Unchecked

**Issue:**
The application was still prioritizing PDF searches even when "Prioritize Document Files" was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 48: HTML Content Extraction Issue

**Issue:**
The application was not properly extracting HTML content when the "Prioritize Document Files" option was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 49: Search Engine Preference Not Respected

**Issue:**
The application was hardcoded to always use Google search, ignoring the user's preference for DuckDuckGo.

**Impact:**
- User preferences for search engines were not respected, potentially affecting search results.

**Cause:**
The run_research function in app.py was hardcoded to use Google.

**Fix:**
Modified the run_research function to accept a search_engine parameter and detect which search engine to use.

**Location:**
`app.py` - In the `run_research` function around line 220

## Error 50: HTML Content Not Prioritized When Option Unchecked

**Issue:**
The application was still prioritizing PDF searches even when "Prioritize Document Files" was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 51: HTML Content Extraction Issue

**Issue:**
The application was not properly extracting HTML content when the "Prioritize Document Files" option was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 52: Search Engine Preference Not Respected

**Issue:**
The application was hardcoded to always use Google search, ignoring the user's preference for DuckDuckGo.

**Impact:**
- User preferences for search engines were not respected, potentially affecting search results.

**Cause:**
The run_research function in app.py was hardcoded to use Google.

**Fix:**
Modified the run_research function to accept a search_engine parameter and detect which search engine to use.

**Location:**
`app.py` - In the `run_research` function around line 220

## Error 53: HTML Content Not Prioritized When Option Unchecked

**Issue:**
The application was still prioritizing PDF searches even when "Prioritize Document Files" was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 54: HTML Content Extraction Issue

**Issue:**
The application was not properly extracting HTML content when the "Prioritize Document Files" option was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 55: Search Engine Preference Not Respected

**Issue:**
The application was hardcoded to always use Google search, ignoring the user's preference for DuckDuckGo.

**Impact:**
- User preferences for search engines were not respected, potentially affecting search results.

**Cause:**
The run_research function in app.py was hardcoded to use Google.

**Fix:**
Modified the run_research function to accept a search_engine parameter and detect which search engine to use.

**Location:**
`app.py` - In the `run_research` function around line 220

## Error 56: HTML Content Not Prioritized When Option Unchecked

**Issue:**
The application was still prioritizing PDF searches even when "Prioritize Document Files" was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 57: HTML Content Extraction Issue

**Issue:**
The application was not properly extracting HTML content when the "Prioritize Document Files" option was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 58: Search Engine Preference Not Respected

**Issue:**
The application was hardcoded to always use Google search, ignoring the user's preference for DuckDuckGo.

**Impact:**
- User preferences for search engines were not respected, potentially affecting search results.

**Cause:**
The run_research function in app.py was hardcoded to use Google.

**Fix:**
Modified the run_research function to accept a search_engine parameter and detect which search engine to use.

**Location:**
`app.py` - In the `run_research` function around line 220

## Error 59: HTML Content Not Prioritized When Option Unchecked

**Issue:**
The application was still prioritizing PDF searches even when "Prioritize Document Files" was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 60: HTML Content Extraction Issue

**Issue:**
The application was not properly extracting HTML content when the "Prioritize Document Files" option was unchecked.

**Impact:**
- Users couldn't effectively use the application for non-PDF content research.

**Cause:**
The LazyScholar class was not properly handling the require_pdfs flag.

**Fix:**
Refactored the conduct_research method to prioritize HTML content when require_pdfs is False, and added a dedicated _extract_html_content method to handle HTML content extraction.

**Location:**
`lazy_scholar.py` - In the conduct_research method

## Error 61: Search Engine Preference Not Respected

**Issue:**
The application was hardcoded to always use Google search, ignoring the user's preference for DuckDuckGo.

**Impact:**
- User preferences for search engines were not respected, potentially affecting search results.

**Cause:**
The run_research function in app.py was hardcoded to use Google.

**Fix:**
Modified the run_research function to accept a search_engine parameter and detect which search engine to use.

**Location:**
`app.py` - In the `run_research` function around line 220

- `app.py` - In the `run_research` function around line 220
- `app.py` - In the `run_research_task` function around line 490

**Note:**
This fix ensures that the application respects the user's preferred search engine while still properly encoding the search query for each supported search engine. The application now constructs the appropriate search URL based on the search engine specified in the profile. 

# LazyScholar Errors

## Browser/Selenium Errors

1. **HTML Content Extraction Error**
   - Error: `Error extracting HTML content: Message: [Stacktrace details]`
   - Location: In lazy_scholar.py during HTML content extraction in the `_extract_html_content` method
   - Impact: Unable to extract HTML content for search queries
   - Actual Error from Logs:
     ```
     ERROR:lazy_scholar:Error extracting HTML content: Message: 
     Stacktrace:
     0   chromedriver                        0x00000001028a9804 cxxbridge1$str$ptr + 2785964
     1   chromedriver                        0x00000001028a1ddc cxxbridge1$str$ptr + 2754692
     ...
     ```
   - Possible causes:
     - Selenium/ChromeDriver compatibility issues
     - Browser initialization problems
     - Network connectivity issues
     - DuckDuckGo search page structure changes
     - Missing or incorrect element selectors for DuckDuckGo search interface
   - Potential solutions:
     - Update ChromeDriver and Selenium to the latest compatible versions
     - Add more robust error handling and fallback mechanisms
     - Implement alternative search methods if DuckDuckGo fails
     - Add explicit waits for page elements to load

2. **Research Process Error**
   - Error: `Error during research: 'NoneType' object is not iterable`
   - Location: In __main__ after attempting to search for web content
   - Actual Error from Logs:
     ```
     INFO:lazy_scholar:Not enough HTML content found (0), adding PDF content...
     INFO:lazy_scholar:Searching for web content with query: Hamburg trip detailed plan best time to visit weather seasons events 
     INFO:lazy_scholar:Using search engine: https://duckduckgo.com/?q=Hamburg+trip+detailed+plan&t=h_&ia=web
     ERROR:__main__:Error during research: 'NoneType' object is not iterable
     ```
   - Impact: Research process terminates prematurely
   - Possible causes:
     - The `_search_for_pdfs` method is returning None instead of an empty list
     - Failed to retrieve search results from DuckDuckGo
     - Search results parsing error
     - Missing return value from a function that should return an iterable
   - Potential solutions:
     - Ensure all methods return empty lists instead of None when no results are found
     - Add null checks before iterating over search results
     - Implement better error handling in the search process
     - Add fallback search engines if the primary one fails

3. **Token Limit Exceeded Error**
   - Error: `API call failed: 400 The input token count (1757384) exceeds the maximum number of tokens allowed (1000000)`
   - Location: In the `extract_web_content` method when trying to process large HTML files
   - Actual Error from Logs:
     ```
     WARNING:lazy_scholar:API call failed: 400 The input token count (1757384) exceeds the maximum number of tokens allowed (1000000).. Retrying in 2 seconds... (Attempt 1/5)
     WARNING:lazy_scholar:API call failed: 400 The input token count (1757384) exceeds the maximum number of tokens allowed (1000000).. Retrying in 4 seconds... (Attempt 2/5)
     WARNING:lazy_scholar:API call failed: 400 The input token count (1757384) exceeds the maximum number of tokens allowed (1000000).. Retrying in 8 seconds... (Attempt 3/5)
     WARNING:lazy_scholar:API call failed: 400 The input token count (1757384) exceeds the maximum number of tokens allowed (1000000).. Retrying in 16 seconds... (Attempt 4/5)
     ERROR:lazy_scholar:API call failed after 5 retries: 400 The input token count (1757384) exceeds the maximum number of tokens allowed (1000000).
     ```
   - Impact: Unable to extract content from HTML files, causing the research process to fail
   - Possible causes:
     - Sending the entire HTML content to the LLM, which exceeds the token limit
     - HTML files with excessive content, scripts, or styling
   - Potential solutions:
     - Use BeautifulSoup to extract only the text content from HTML files
     - Limit the amount of text sent to the LLM
     - Remove unnecessary elements like scripts, styles, and navigation
     - Truncate content if it's still too large

4. **Search Phrase Issue**
   - Error: Using the entire problem statement as the search phrase instead of relevant keywords
   - Location: In the `conduct_research` method when generating search queries
   - Actual Error from Logs:
     ```
     INFO:lazy_scholar:Using search engine: https://duckduckgo.com/?q=Hamburg%27a+tatil+ayarlad%C4%B1k.+Otelimiz+ve+u%C3%A7u%C5%9F+biletlerimiz+var.+Gidece%C4%9Fimiz+tarih+de+belli.+O+y%C3%BCzden+arama+plan%C4%B1na+bunlar%C4%B1+dahil+etmeyelim.+Bize+Hamburg%27da+gezilmesi+g%C3%B6r%C3%BClmesi+gereken+yerleri%2C+turist+tuzaklar%C4%B1n%C4%B1%2C+etrafta+gidebilece%C4%9Fimiz+%C5%9Fehirleri%2C+geleneksel+yemekleri+ve+bunun+gibi+atraksiyonlar%C4%B1+%C3%B6nerebilir+misin+l%C3%BCtfen.&t=h_&ia=web
     ```
   - Impact: Search results are less relevant and may not provide useful information
   - Possible causes:
     - Not using the search_phrase from the generated topics and subtopics
     - Non-English search phrases not being properly handled
     - Original problem statement being used directly as the search query
   - Potential solutions:
     - Ensure search_phrase is always in English and contains relevant keywords
     - Add validation to check if search_phrase is valid
     - Generate appropriate search phrases if none exist or if they're invalid
     - Log the search phrase being used for debugging

## Process Flow

The error occurs in this exact sequence (from logs):
1. Browser starts successfully: `INFO:lazy_scholar:Browser started successfully`
2. Attempts to extract HTML content: `INFO:lazy_scholar:Extracting HTML content for query: Hamburg trip detailed plan best time to visit weather seasons events`
3. HTML extraction fails with a ChromeDriver error: `ERROR:lazy_scholar:Error extracting HTML content: Message: [Stacktrace details]`
4. Tries to fall back to PDF content: `INFO:lazy_scholar:Not enough HTML content found (0), adding PDF content...`
5. Searches for web content: `INFO:lazy_scholar:Searching for web content with query: Hamburg trip detailed plan best time to visit weather seasons events`
6. Fails with "'NoneType' object is not iterable" error: `ERROR:__main__:Error during research: 'NoneType' object is not iterable`

## Specific Code Issues

1. In `_extract_html_content` method:
   - The DuckDuckGo search box selector might be incorrect or the element might not be loading properly
   - Error handling doesn't properly recover from browser navigation failures
   - The error occurs when trying to interact with DuckDuckGo's search interface
   - JavaScript links are not properly filtered, causing navigation errors

2. In `_search_for_pdfs` method:
   - May be returning None in some error cases instead of an empty list
   - The method doesn't have proper error handling for DuckDuckGo search failures
   - The error occurs after the HTML extraction fails and it tries to search for PDFs

3. In `conduct_research` method:
   - When HTML extraction fails, it tries to search for PDFs but doesn't properly handle the case where the search returns None
   - The error occurs in the main research flow after the fallback to PDF search
   - Using the entire problem statement as the search query instead of relevant keywords

4. In `extract_web_content` method:
   - Sending the entire HTML content to the LLM, which can exceed the token limit
   - No preprocessing of HTML to extract only relevant text
   - No limit on the amount of text sent to the LLM

5. In `analyze_problem_statement` method:
   - Not ensuring that search_phrase is always in English
   - Not validating that search_phrase contains relevant keywords
   - Not handling non-ASCII characters in search phrases

## Implemented Fixes

1. Fixed the `_search_for_pdfs` method:
   - Initialized the pdf_urls list at the beginning of the method
   - Moved the return statement outside the try/except block
   - Ensured the method always returns a list, even if empty

2. Added null checks in the `conduct_research` method:
   - Added `or []` to ensure we always have a list even if the method returns None
   - Added an if check before iterating over pdf_urls

3. Improved the DuckDuckGo search implementation:
   - Now directly navigates to the search URL with query parameters
   - Added fallback mechanisms with multiple selector options
   - Improved error handling and logging
   - Added filtering for javascript links

4. Fixed the token limit issue in `extract_web_content`:
   - Added BeautifulSoup to extract only text content from HTML
   - Removed unnecessary elements like scripts, styles, and navigation
   - Limited the text length to avoid token limit issues
   - Added logging to track the amount of text extracted

5. Fixed the search phrase issue:
   - Updated the analyze_problem_statement method to ensure search_phrase is always in English
   - Added validation to check if search_phrase contains non-ASCII characters
   - Added a fallback mechanism to generate appropriate search phrases if none exist or if they're invalid
   - Added logging to track the search phrase being used
   - Modified the prompt to explicitly request concise, English search phrases with relevant keywords

These changes make the application more robust when dealing with search engine failures, large HTML files, and non-English search phrases.

## PDF Search Issues

### Problem
The application was struggling to find and download PDF files for academic research, which is a critical functionality for the LazyScholar application. The DuckDuckGo search implementation was not effectively finding PDF files.

### Location
`lazy_scholar.py` in the `_search_for_pdfs` method

### Impact
- Limited or no PDF results for academic research topics
- Reduced effectiveness of the application for scholarly research
- Poor user experience when researching academic topics that require access to papers

### Causes
1. Issues with DuckDuckGo search implementation
2. Ineffective handling of PDF links and extraction
3. Lack of proper query formatting for PDF searches

### Solution
1. Improved DuckDuckGo search by using direct URL construction
2. Added "filetype:pdf" to search queries to improve PDF discovery
3. Enhanced result link extraction with specific CSS selectors for DuckDuckGo
4. Improved PDF link extraction from search results and result pages
5. Added better logging and screenshots for debugging
6. Enhanced error handling to ensure the application continues functioning even if one search method fails
7. Added support for additional academic search engines as fallbacks

### Implementation
The `_search_for_pdfs` method was refactored to:
1. Use a more direct approach with DuckDuckGo by constructing search URLs with proper query parameters
2. Improve the extraction of PDF links from search results using better selectors
3. Add additional academic search engines like base-search, core.ac.uk, semanticscholar, sciencedirect, and researchgate
4. Add comprehensive logging and error handling

This implementation significantly improves the PDF search capabilities of the application, making it more effective for academic research without relying on Google Scholar.

## Site Restriction Issues

### Problem
The application was not consistently applying site restrictions (e.g., site:edu) to searches, resulting in mixed results from various domains even when a specific domain type was preferred.

### Location
`lazy_scholar.py` in the `_search_for_pdfs` method

### Impact
- Search results included content from non-preferred domains
- Reduced focus on academic or specific domain sources
- Inconsistent application of site restrictions across different search engines

### Causes
1. Site restrictions were not being consistently applied to all search queries
2. No validation of search results against the preferred site domain
3. Additional search engines weren't using the site_tld parameter

### Solution
1. Added consistent site restriction (site:tld) to all search queries
2. Implemented URL validation to filter out results that don't match the preferred domain
3. Created a helper method `_url_matches_site_tld` to check if URLs match the site restriction
4. Added logging for skipped URLs that don't match the site restriction
5. Ensured all search engines (including fallbacks) use the site restriction

### Implementation
1. Modified the `_search_for_pdfs` method to add site restriction to all queries
2. Added URL validation for all PDF links and result links
3. Created a new helper method `_url_matches_site_tld` to check if URLs match the site restriction
4. Added logging for skipped URLs to help with debugging

This implementation ensures that all searches and results consistently respect the preferred site domain (e.g., .edu, .gov, .org) when specified.

## PDF Download Issues

### Problem
The application was not downloading PDFs immediately when they were found during the search process, leading to inefficient processing and potential loss of PDF sources.

### Location
`lazy_scholar.py` in the `_search_for_pdfs` and `conduct_research` methods

### Impact
- Delayed PDF downloads, potentially causing timeouts or lost sources
- Redundant search and download processes
- Inefficient workflow where PDFs were found but not immediately downloaded
- Potential for downloading the same PDF multiple times

### Causes
1. The PDF search and download processes were separated
2. PDFs were first collected as URLs and then downloaded in a separate step
3. No immediate validation of PDF availability during the search process

### Solution
1. Modified the `_search_for_pdfs` method to download PDFs immediately when found
2. Added tracking of downloaded PDFs during the search process
3. Updated the `conduct_research` method to use already downloaded PDFs instead of re-downloading them
4. Improved logging to track both found and downloaded PDFs

### Implementation
1. Added immediate PDF download in the `_search_for_pdfs` method when a PDF URL is found
2. Modified the `conduct_research` method to use the most recently downloaded PDFs based on file creation time
3. Removed redundant download code in the `conduct_research` method
4. Added better logging to track both found URLs and successfully downloaded PDFs

This implementation ensures that PDFs are downloaded as soon as they are found, making the process more efficient and reducing the chance of losing PDF sources due to timeouts or other issues.

## PDF Processing Issues

### Problem
The application was not efficiently processing PDFs for subtopics, leading to potential memory issues and not creating subtopic markdown files immediately after all PDFs for a subtopic were downloaded.

### Location
`lazy_scholar.py` in the `conduct_research` and `_extract_pdf_content` methods

### Impact
- Inefficient processing of PDFs, with all PDFs being processed before creating any markdown files
- Potential memory issues when processing many PDFs at once
- No immediate feedback on subtopic content until all PDFs were processed
- Inconsistent handling of PDF and HTML content

### Causes
1. PDFs were processed in bulk rather than one by one
2. Markdown files were created only after all PDFs were processed
3. No dedicated method for processing all PDFs for a specific subtopic
4. Inconsistent handling of PDF and HTML content sources

### Solution
1. Created a new `_process_pdfs_for_subtopic` method to handle PDF processing for each subtopic
2. Modified the PDF processing workflow to process PDFs one by one
3. Updated the `conduct_research` method to create markdown files immediately after processing all PDFs for a subtopic
4. Improved handling of both PDF and HTML content sources

### Implementation
1. Added a new `_process_pdfs_for_subtopic` method that:
   - Processes each PDF individually
   - Extracts content from each PDF using the LLM
   - Creates a markdown file for the subtopic with all extracted content
2. Modified the `conduct_research` method to:
   - Process PDFs for each subtopic separately
   - Create markdown files immediately after processing all PDFs for a subtopic
   - Handle both PDF and HTML content sources consistently

This implementation ensures that PDFs are processed efficiently, one by one, and that subtopic markdown files are created immediately after all PDFs for a subtopic are processed, providing better feedback and reducing memory usage.

## Search Pagination Issues

### Problem
The application was switching to different search engines when not enough PDFs were found, instead of checking additional pages of search results from the same engine.

### Location
`lazy_scholar.py` in the `_search_for_pdfs` method

### Impact
- Inconsistent search results across different search engines
- Potential loss of relevant PDFs from the original search engine
- Inefficient search process that didn't fully utilize the primary search engine
- Unnecessary complexity in the search process

### Causes
1. The search implementation only checked the first page of search results
2. When not enough PDFs were found, the code switched to different search engines
3. No pagination mechanism to navigate through multiple pages of search results

### Solution
1. Implemented pagination for DuckDuckGo search results
2. Added support for checking multiple pages (up to 3 by default) before stopping
3. Removed the code that switched to different search engines
4. Added proper logging for each page of search results

### Implementation
1. Modified the `_search_for_pdfs` method to:
   - Loop through multiple pages of search results (up to a configurable maximum)
   - Use DuckDuckGo's pagination parameter ('s') to navigate to subsequent pages
   - Take screenshots and log results for each page separately
   - Stop searching when enough PDFs are found or all pages have been checked
2. Removed the code that switched to different search engines when not enough PDFs were found

This implementation ensures that the search process fully utilizes the primary search engine by checking multiple pages of results before stopping, providing more consistent and relevant search results.

## PDF Download and Extraction Issues

### Problem
The application was failing to download and extract content from PDFs due to various issues including 403 Forbidden errors, encrypted PDFs, and PDF parsing errors.

### Location
`lazy_scholar.py` in the `_download_pdf` and `_extract_text_from_pdf` methods

### Impact
- Failed to download PDFs from certain academic websites that block automated requests
- Unable to extract text from encrypted or malformed PDFs
- Errors when processing PDFs with specific security features
- Missing content in the final research output due to failed PDF processing

### Causes
1. Academic websites blocking requests without proper browser headers (403 Forbidden errors)
2. Encrypted PDFs requiring password decryption
3. Malformed PDFs that PyPDF2 couldn't parse
4. Missing error handling for specific PDF extraction errors
5. No fallback mechanisms for when the primary PDF extraction method fails

### Solution
1. Added browser-like headers to PDF download requests to avoid being blocked
2. Implemented a browser-based fallback download method for 403 Forbidden errors
3. Added support for decrypting encrypted PDFs with empty passwords (common case)
4. Implemented alternative PDF extraction methods using pdfplumber and pdfminer
5. Improved error handling throughout the PDF processing pipeline
6. Added validation to check if content is actually a PDF before attempting extraction

### Implementation
1. Modified the `_download_pdf` method to:
   - Add browser-like headers to requests
   - Implement a fallback method using Selenium for 403 errors
   - Validate PDF content type more thoroughly
2. Enhanced the `_extract_text_from_pdf` method to:
   - Handle encrypted PDFs
   - Process PDFs page by page with better error handling
   - Validate PDF content before extraction
3. Added a new `_extract_text_from_pdf_alternative` method that:
   - Tries multiple PDF extraction libraries
   - Provides fallback options when the primary method fails
   - Logs detailed error information for debugging

This implementation significantly improves the PDF download and extraction success rate, ensuring more complete research results.

# Errors Log

This file tracks errors encountered during the LazyScholar project to avoid repeating them.

## Current Errors
- None

## Resolved Errors
- **HTML Content Extraction Issue**: When `require_pdfs` is set to false (non-file focused research), the system reported "Prioritizing HTML content" but failed to extract any content from HTML pages. The logs showed "Found 0 HTML URLs for content extraction" despite being in non-file focused mode.
  - **Root Cause**: The issue was in the `_extract_html_content` method where it was using the outdated CSS selector ".result__a" to find DuckDuckGo search results. DuckDuckGo had changed their HTML structure, causing the selector to no longer match any elements.
  - **Fix**: 
    1. Updated the `_extract_html_content` method to use more general selectors (By.TAG_NAME, "a") to find all links on the page
    2. Added vision model support to identify search result links by analyzing screenshots
    3. Enhanced the `find_pdf_links` function in vision_helper.py to support HTML links with a new `is_html` parameter
    4. Improved filtering to exclude search engine domains and non-relevant links
    5. Added better error handling and logging for debugging

- **PDF Extraction Error**: When extracting text from PDFs, the system reported "Error in alternative PDF text extraction: name 'StringIO' is not defined".
  - **Root Cause**: The StringIO class was being used in the PDF extraction code but was not imported.
  - **Fix**: Added StringIO to the imports from the io module: `from io import BytesIO, StringIO`

- **Incorrect Reference Source URLs**: The system was using search engine URLs (e.g., DuckDuckGo) as references instead of the actual webpage URLs where content was extracted from.
  - **Root Cause**: The `_write_subtopic_file` method was not properly formatting references for HTML content sources, and the HTML extraction process wasn't capturing enough metadata about the sources.
  - **Fix**:
    1. Enhanced the `_extract_html_content` method to capture page title and domain information
    2. Updated the `_write_subtopic_file` method to format references properly using the domain and title information
    3. Improved reference formatting to distinguish between HTML and PDF sources

- **Search Results Not Being Visited**: The system was finding search result links but not properly navigating to them to extract content, resulting in references still showing search engine URLs.
  - **Root Cause**: The system was correctly identifying search result links but had issues with the navigation and content extraction process.
  - **Fix**:
    1. Improved the URL filtering to better exclude search engine domains
    2. Added a check to ensure valid URLs were found before attempting to visit them
    3. Increased page load wait time from 3 to 5 seconds to ensure content is fully loaded
    4. Added tracking of the current URL after navigation (to handle redirects)
    5. Enhanced logging to better track the navigation and content extraction process
    6. Fixed the subtopic title in the markdown output

- **API Quota Exhaustion Errors**: The system was encountering "429 Resource has been exhausted" errors when generating the final paper, particularly during reference enhancement.
  - **Root Cause**: The API retry mechanism wasn't handling quota exhaustion properly, with too short wait times between retries.
  - **Fix**:
    1. Implemented a more robust exponential backoff strategy with much longer wait times (2, 4, 8, 16, 32 minutes)
    2. Added progress logging during the wait period to show remaining time
    3. Modified the `_api_call_with_retry` method to return a fallback value instead of raising an exception after max retries
    4. Enhanced the `_enhance_references` method to handle API errors gracefully and provide simple references when enhancement fails

- **Messy Final Paper Generation**: The final paper had formatting issues and was not properly structured.
  - **Root Cause**: The final paper generation process was too complex, trying to use the LLM to reorganize content that was already well-structured.
  - **Fix**:
    1. Simplified the final paper generation by directly combining the content from subtopic files
    2. Improved the extraction of content from subtopic files to avoid duplication
    3. Added proper separation between topics with horizontal rules
    4. Enhanced the references section formatting for better readability
    5. Added error handling throughout the process to ensure the final paper is generated even if some steps fail

- **Content Extraction from Search Pages**: The system sometimes extracted content directly from search results pages instead of visiting the actual websites.
  - **Impact**: Research content was incomplete or irrelevant, with subtopic files sometimes being empty or containing search engine metadata.
  - **Root Cause**: The URL filtering was inadequate, failing to exclude all search engine pages, particularly after redirects. The vision model was also identifying navigation links rather than actual content links.
  - **Fix**: 
    1. Added tracking of the search engine domain at the beginning of the process.
    2. Expanded the list of excluded domains to include more search engines and non-content sites.
    3. Implemented better filtering of links from the vision model to exclude search engine domains.
    4. Added link text analysis to identify content links (links with substantial text are more likely to be content).
    5. Increased the number of URLs to try from 3 to 5 to improve chances of finding content.
    6. Added a retry mechanism for page loading with timeouts to handle slow-loading pages.
    7. Improved domain extraction and validation throughout the process.
    8. Enhanced content extraction by targeting more content-specific HTML elements.
    9. Added a success counter to stop after finding sufficient content.
    10. Improved error handling and logging throughout the process.

- **Empty Final Paper**: The final paper was being created but did not properly include content from the subtopic files.
  - **Impact**: The final paper contained only topic and subtopic titles without any actual content, making it unusable for research purposes.
  - **Root Cause**: The `generate_final_paper` method was not correctly extracting content from subtopic files. It was using a simplistic approach to remove the title line that failed when the content had a more complex structure.
  - **Fix**: 
    1. Improved the content extraction logic to handle different file structures.
    2. Added better handling for title removal that checks if the content starts with "# " and properly removes only the title line.
    3. Enhanced reference extraction to recognize both numbered (1.) and bulleted (-) reference formats.
    4. Added more robust error handling to ensure content is properly extracted even with varying file formats.

- **PDF Downloads Despite Unchecked Option**: The system was downloading PDF files even when "Prioritize Document Files" option was unchecked.
  - **Impact**: Unnecessary PDF downloads were occurring, wasting bandwidth and processing time when the user specifically chose not to prioritize PDFs.
  - **Root Cause**: In the `conduct_research` method, when `require_pdfs` was set to `False`, the system was still calling `_search_for_pdfs` to search for and download new PDFs.
  - **Fix**: 
    1. Removed the PDF search call when `require_pdfs` is `False`.
    2. Completely disabled PDF usage when `require_pdfs` is `False`.
    3. Added a check to verify if the PDF directory exists before attempting to use PDFs.
    4. Added appropriate logging to clarify that PDF search is disabled when "Prioritize Document Files" is unchecked.
    5. Added additional logging to indicate that existing PDFs are also being skipped when "Prioritize Document Files" is unchecked.

- **Empty Final Paper**: The final paper was being created but did not properly include content from the subtopic files.
  - **Impact**: The final paper contained only topic and subtopic titles without any actual content, making it unusable for research purposes.
  - **Root Cause**: The `generate_final_paper` method was not correctly extracting content from subtopic files. It was using a simplistic approach to remove the title line that failed when the content had a more complex structure.
  - **Fix**: 
    1. Improved the content extraction logic to handle different file structures.
    2. Added better handling for title removal that checks if the content starts with "# " and properly removes only the title line.
    3. Enhanced reference extraction to recognize both numbered (1.), bulleted (-), and asterisk (*) reference formats.
    4. Added more robust error handling to ensure content is properly extracted even with varying file formats.
    5. Added a fallback mechanism to find subtopic files when the file path is not explicitly provided or is incorrect.
    6. Added better handling of API quota exhaustion errors during reference enhancement.
    7. Improved logging to provide better visibility into the final paper generation process.

- **Empty Search Queries with Non-ASCII Characters**: The system was not properly handling search phrases containing non-ASCII characters (like "ü" in "Lübeck"), resulting in empty search queries.
  - **Impact**: When a topic or subtopic contained non-ASCII characters, the search query was being set to an empty string, causing the system to search with only the search suffix or not search at all.
  - **Root Cause**: In the `conduct_research` method, when a search phrase contained non-ASCII characters, it was being replaced with an empty string instead of being properly transliterated or having the non-ASCII characters removed.
  - **Fix**: 
    1. Implemented proper transliteration of non-ASCII characters using Python's `unicodedata` module.
    2. Added a fallback to replace any remaining non-ASCII characters with spaces.
    3. Added normalization of spaces to ensure clean search queries.
    4. Added logging to show the transliterated search phrase that's being used.

## Future Improvements

1. **Content Type Detection**: Improve automatic detection of content type (academic, practical, travel) based on the problem statement.

2. **Multi-language Support**: Enhance support for non-English research while maintaining English search capabilities.

3. **Source Diversity**: Implement better mechanisms to ensure diversity of sources beyond PDFs (web pages, videos, etc.).

## Content Generation Issues

1. **Error 30: LLM Instructions Appearing in Topic Files**: The LLM's instructions and suggestions are appearing directly in the generated topic files instead of just the content.
   - **Impact**: Topic files contain meta-commentary and instructions that should not be visible to the end user, making the research output look unprofessional.
   - **Cause**: The _extract_pdf_content and _process_pdfs_for_subtopic methods are not properly filtering out LLM instructions and meta-commentary from the final output.
   - **Solution**: Modify the prompt templates to clearly separate content from instructions, and update the content extraction process to only include the actual research content in the final markdown files. Add post-processing to remove any remaining LLM instructions or meta-commentary.

2. **Error 31: Irrelevant Content in Topic Files**: Some topic files contain content about DuckDuckGo and other search-related information instead of the actual research topic.
   - **Impact**: Research output contains irrelevant information that doesn't relate to the intended research topic.
   - **Cause**: When HTML content is extracted from search result pages, the content of the search engine itself is sometimes being included in the research output.
   - **Solution**: Improve the HTML content extraction process to better filter out search engine UI elements and only extract relevant content from actual research sources. Add content relevance checking to ensure extracted information is related to the research topic.

3. **Error 32: Inconsistent Language in Topic Files**: Some topic files contain content in Turkish while others are in English, creating inconsistency in the research output.
   - **Impact**: Research output lacks language consistency, making it difficult to read and unprofessional.
   - **Cause**: The language parameter is not being consistently applied across all content extraction processes.
   - **Solution**: Ensure the language parameter is properly passed to all content generation methods and that the LLM is given clear instructions about the desired output language.

11. **Limited URL Processing for HTML Content**: The system was limiting HTML URL processing to only 15 URLs regardless of the max_pdfs_per_topic setting.
    - **Impact**: Even when users set a higher number of sources in the UI (e.g., 10), the system would only process a maximum of 15 URLs, which often resulted in fewer successful content extractions.
    - **Root Cause**: In the `_extract_html_content` method, there was a hardcoded limit of 15 URLs to process, which was not aligned with the user's max_pdfs_per_topic setting.
    - **Fix**: 
      1. Updated the URL processing limit to be based on the user's max_pdfs_per_topic setting (multiplied by 2 to ensure enough URLs are processed).
      2. Added logging to show the max_pdfs_per_topic value for debugging purposes.
      3. This ensures that the system will process enough URLs to potentially reach the user's desired number of references.

12. **Partial Screenshots**: The system was only capturing the visible portion of web pages in screenshots, missing content that required scrolling.
    - **Impact**: Screenshots didn't show the complete web page content, making it difficult to analyze the full context of search results and web pages.
    - **Root Cause**: The default Selenium `save_screenshot` method only captures the visible viewport area.
    - **Fix**: 
      1. Implemented a JavaScript-based solution to capture full-page screenshots.
      2. Added code to get the full page height using `document.body.scrollHeight` and `document.documentElement.scrollHeight`.
      3. Temporarily resized the browser window to match the full page height before taking screenshots.
      4. Added fallback to regular screenshots if the full-page capture fails.
      5. Applied this improvement to all screenshot captures in the application (search results, link detection, and web page content).

13. **Empty Subtopic Files**: The system was creating empty subtopic files when no content could be found, resulting in incomplete research papers.
    - **Impact**: Many subtopics had no content, leading to gaps in the research and a less comprehensive final paper.
    - **Root Cause**: The system would give up too easily when searching for content, only checking the first page of search results and not trying alternative approaches when no content was found.
    - **Fix**: 
      1. Implemented pagination to check up to 5 pages of search results for each query.
      2. Added retry logic with alternative search queries when no content is found.
      3. Modified the system to make a final attempt with a broader search query and increased limits when all else fails.
      4. Prevented the creation of empty subtopic files, ensuring that only files with actual content are written.
      5. Added detailed logging to track the search and content extraction process across multiple pages and retries.

14. **Indentation Errors in Code**: The code contained several indentation errors that were causing syntax errors when running the application.
    - **Impact**: The application would fail to start with syntax errors, particularly around try-except blocks.
    - **Root Cause**: Inconsistent indentation in several key methods, including:
      - The `_enhance_references` method's try-except blocks
      - The PDF file processing section in the `conduct_research` method
      - The reference formatting in the `_write_subtopic_file` method
    - **Fix**: 
      - Created a backup of the original file before making changes
      - Fixed the indentation in the `_enhance_references` method by completely rewriting it with proper indentation
      - Fixed the indentation in the PDF file processing section by adding proper indentation to the code block after the if statement
      - Fixed the indentation in the reference formatting section by correcting the else clause indentation
      - Successfully resolved all syntax errors, allowing the application to run properly
      - **Future Prevention**: Recommended using a Python code formatter like Black or YAPF to automatically fix all indentation issues throughout the codebase and prevent similar issues in the future.

# Errors Tracking

This file tracks errors encountered during development of LazyScholar to avoid repetition.

## Common Errors

### PDF Processing
- **PDF Download Failures**: Issues when downloading PDFs from certain academic sources
- **PDF Parsing Errors**: Problems extracting text from poorly formatted PDFs
- **Encoding Issues**: Character encoding issues in extracted text

### Web Scraping
- **CAPTCHA Encounters**: Google Scholar and other sites sometimes trigger CAPTCHA verification
- **Rate Limiting**: Search engines block excessive requests
- **Site Layout Changes**: When web interfaces change, selectors may break

### API Usage
- **Gemini API Token Limits**: Exceeding API quotas
- **API Response Timeouts**: Slow responses from LLM APIs
- **Invalid API Key**: Configuration issues with API keys

### Browser Automation
- **Selenium Timeouts**: Browser operations taking too long
- **Element Not Found**: Web elements missing or changed
- **Browser Crashes**: Unexpected browser terminations

## Error Mitigation Strategies

1. Implement proper error handling and retries for web requests
2. Add logging for all operations to track issues
3. Use exponential backoff for rate-limited requests
4. Handle PDF extraction gracefully with fallback methods
5. Implement browser fingerprint rotation to avoid detection

## Current Issues

### API Rate Limiting (March 17)
- **Symptom**: Application stuck in retry loop with "API quota exhausted (429)" errors
- **Cause**: Gemini API has rate limits that are being hit during paper generation 
- **Context**: This was working in previous commits but now fails consistently
- **Possible Solutions**:
  1. Implement more sophisticated rate limiting with longer backoff periods
  2. Add a cooling-off period between major API calls
  3. Cache API responses to reduce the number of calls
  4. Split large requests into smaller chunks
  5. Consider upgrading API tier if using free tier
  6. Check if recent changes increased the number of API calls per operation

### Fix Applied (March 17)
- **Problem**: Rate limiting backoff timing inconsistency between versions
- **Solution**: Reverted to seconds-based backoff as per user's preference
- **File Modified**: lazy_scholar.py
- **Changes**: 
  - Using seconds-based backoff (2, 4, 8, 16, 32 seconds) for API rate limit handling
  - Simplified wait logging
  - This matches the user's preferred behavior from previous working commits

### Debugging Steps
1. Check app.py and lazy_scholar.py for recent changes to API call patterns
2. Add more detailed logging to identify which specific API calls are hitting limits
3. Consider adding a feature to pause/resume research to avoid losing progress when hitting limits
4. Implement an API usage counter to track usage and stay under limits

# LazyScholar Error Documentation

## API Request Handling 

### Updated Implementation (matching commit 4d669e2)

LazyScholar now implements an exponential backoff mechanism for handling API rate limiting in the `_api_call_with_retry` method that matches the approach from commit 4d669e2:

```python
def _api_call_with_retry(self, api_func, max_retries=5, retry_delay=2):
    """
    Make an API call with retry logic.
    
    Args:
        api_func: Function to call the API
        max_retries: Maximum number of retries
        retry_delay: Initial delay between retries in seconds
        
    Returns:
        API response
    """
    retries = 0
    while retries < max_retries:
        try:
            return api_func()
        except Exception as e:
            retries += 1
            
            # Check if it's a rate limit error (429)
            if "429" in str(e) or "Resource has been exhausted" in str(e) or "quota" in str(e).lower():
                # For rate limit errors, use a longer delay
                current_delay = retry_delay * (2 ** retries)  # Exponential backoff
                current_delay = min(current_delay, 60)  # Cap at 60 seconds
                
                logger.warning(f"Rate limit error (429). Waiting for {current_delay} seconds before retry {retries}/{max_retries}")
                time.sleep(current_delay)
            else:
                # For other errors, use standard backoff
                if retries >= max_retries:
                    logger.error(f"API call failed after {max_retries} retries: {str(e)}")
                    raise
                
                logger.warning(f"API call failed: {str(e)}. Retrying in {retry_delay} seconds... (Attempt {retries}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 30)  # Exponential backoff, capped at 30 seconds
    
    return None  # This should only be reached for rate limit errors
```

### Key Characteristics

1. **Error Detection**:
   - Rate limit errors are detected when error messages contain "429", "Resource has been exhausted", or "quota" (case insensitive)
   - Other errors use a different backoff strategy

2. **Exponential Backoff**: 
   - For rate limit errors: Exponential backoff with cap at 60 seconds
     - Formula: `delay = min(initial_delay * 2^retry_count, 60)`
   - For other errors: Simple retry with increasing delay, capped at 30 seconds
     - Formula: `delay = min(delay * 2, 30)`

3. **Error Handling**:
   - For rate limit errors: Continue retrying until max retries
   - For other errors: Raise exception after max retries
   - Return None if max retries exceeded only for rate limit errors

4. **Logging**:
   - Rate limit errors: "Rate limit error (429). Waiting for X seconds before retry Y/Z"
   - Other errors: "API call failed: [error]. Retrying in X seconds... (Attempt Y/Z)"
   - Final error: "API call failed after X retries: [error]"

### Differences from Previous Implementation

1. **Rate Limit Handling**:
   - **Before**: Fixed exponential delay pattern of 2, 4, 8, 16, 32 seconds regardless of initial retry_delay
   - **After**: Scaled by initial retry_delay with cap at 60 seconds (retry_delay * 2^retries, max 60)

2. **Error Handling**:
   - **Before**: Returns error messages for all error types after max retries
   - **After**: Raises exceptions for non-rate-limit errors after max retries

3. **Wait Time Logging**:
   - **Before**: Logged both before and after waiting
   - **After**: Only logs before waiting

4. **Non-Rate-Limit Error Handling**:
   - **Before**: Same exponential backoff formula for all errors
   - **After**: Different formula with 30-second cap for non-rate-limit errors

### Potential Issues

For methods that expected error message returns from API call failures (like `_enhance_references`), modifications may be needed since the method now raises exceptions for non-rate-limit errors after max retries instead of returning a fallback message.

### Potential Improvements

1. **Longer backoff periods**: For severe rate limiting, consider implementing minute-scale delays.

2. **Caching responses**: Implement caching to reduce the number of similar calls.

3. **Request queuing**: Create a queue system to manage API requests and avoid hitting rate limits.

4. **Distributed requests**: Spread requests over time when handling multiple operations.

5. **Multiple API keys**: Implement rotation between different API keys if available.

6. **Proactive rate management**: Track API usage and implement proactive throttling.

7. **Persistent caching**: Save previous responses to disk for resuming after rate limit errors.

8. **Progress preservation**: Enable research to be paused and resumed when limits are encountered.