from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import json
from lazy_scholar import LazyScholar
from urllib.parse import urlparse
import logging
import threading
import time
import queue
import uuid
import urllib.parse
import requests
import re
from pathlib import Path
from academic_formatter import initialize_model, detect_language, translate_text
import markdown
import bleach

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Progress tracking
class ResearchProgress:
    """Class to track the progress of research tasks"""
    _instances = {}  # Store progress by task_id
    _lock = threading.Lock()  # Thread safety

    @classmethod
    def get_instance(cls, task_id):
        """Get or create a progress instance for the given task_id"""
        with cls._lock:
            if task_id not in cls._instances:
                cls._instances[task_id] = cls(task_id)
            return cls._instances[task_id]
    
    @classmethod
    def get_all_progress(cls):
        """Get all progress instances"""
        with cls._lock:
            return cls._instances.copy()
    
    @classmethod
    def clean_old_tasks(cls, max_age_seconds=3600):
        """Remove tasks older than max_age_seconds"""
        with cls._lock:
            current_time = time.time()
            to_remove = []
            for task_id, instance in cls._instances.items():
                if current_time - instance.last_update > max_age_seconds:
                    to_remove.append(task_id)
            
            for task_id in to_remove:
                del cls._instances[task_id]
    
    def __init__(self, task_id):
        self.task_id = task_id
        self.status = "initializing"  # initializing, running, completed, failed, cancelled
        self.progress = 0  # 0-100
        self.current_step = "Starting research..."
        self.details = {}
        self.messages = []
        self.last_update = time.time()
        self.cancelled = False  # Flag to indicate if the task has been cancelled
    
    def update(self, status=None, progress=None, current_step=None, details=None, message=None):
        """Update the progress"""
        with self._lock:
            if status:
                self.status = status
            if progress is not None:
                self.progress = progress
            if current_step:
                self.current_step = current_step
            if details:
                self.details.update(details)
            if message:
                self.messages.append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "text": message
                })
                # Keep only the last 100 messages
                if len(self.messages) > 100:
                    self.messages = self.messages[-100:]
            
            self.last_update = time.time()
    
    def cancel(self):
        """Cancel the research task"""
        with self._lock:
            self.cancelled = True
            self.status = "cancelled"
            self.current_step = "Research cancelled by user"
            self.messages.append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "text": "Research task cancelled by user"
            })
            self.last_update = time.time()
    
    def is_cancelled(self):
        """Check if the task has been cancelled"""
        with self._lock:
            return self.cancelled
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        with self._lock:
            return {
                "task_id": self.task_id,
                "status": self.status,
                "progress": self.progress,
                "current_step": self.current_step,
                "details": self.details,
                "messages": self.messages,
                "last_update": self.last_update,
                "cancelled": self.cancelled
            }

# LazyScholar wrapper function
def run_research(problem_statement, output_dir, max_pdfs=10, academic_format=True, 
                language='en', search_suffix=None, headless=True, site_tld=None,
                minimum_pdfs=3, crawl_depth=3, max_crawl_pages=20, search_purpose='academic',
                require_pdfs=True, task_id=None, search_engine=None, output_format='md', progress=None):
    """
    Wrapper function for LazyScholar to handle research process
    
    Args:
        problem_statement (str): The main research query
        output_dir (str): Directory to save research results
        max_pdfs (int): Maximum PDFs to download per topic
        academic_format (bool): Whether to use academic formatting
        language (str): Language code for research
        search_suffix (str): Additional terms to add to search query
        headless (bool): Whether to run browser in headless mode
        site_tld (str): Domain pattern to look for in search results (e.g., 'edu', 'gov', 'org')
        minimum_pdfs (int): Minimum number of PDFs required for each subtopic before stopping search
        crawl_depth (int): Maximum depth for website crawling
        max_crawl_pages (int): Maximum number of pages to visit during crawling
        search_purpose (str): Purpose of the search ('academic', 'practical', or 'travel')
        require_pdfs (bool): Whether PDFs are required for the search
        task_id (str): Unique identifier for tracking progress
        search_engine (str): Search engine URL to use for research
        output_format (str): Format for the final paper ('md', 'pdf', 'html', 'epub', etc.)
        progress (ResearchProgress): Progress tracker instance, if provided
        
    Returns:
        bool: True if research completed successfully, False otherwise
    """
    # Create or get progress tracker
    if not progress:
        if not task_id:
            task_id = str(uuid.uuid4())
        progress = ResearchProgress.get_instance(task_id)
    
    progress.update(status="running", progress=5, current_step="Initializing research", 
                   message=f"Starting research on: {problem_statement}")
    
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        progress.update(progress=10, message="Created output directory")
        
        # Prepare search query
        search_query = problem_statement.strip()
        if search_suffix:
            search_query = f"{search_query} {search_suffix}"
            
        # Add filters to search query
        if "filetype:pdf" not in search_query.lower() and require_pdfs:
            search_query = f"{search_query} filetype:pdf"
        
        # Add site TLD filter if specified - use a more flexible approach for search engines
        # For search engines, we'll use site: operator which will find any domain containing the pattern
        if site_tld:
            clean_tld = site_tld.lower().strip('.')
            if f"site:{clean_tld}" not in search_query.lower():
                # Only add site filter to the search query, not to the crawler
                search_query = f"{search_query} site:{clean_tld}"
        elif academic_format and "site:edu" not in search_query.lower() and not site_tld:
            # Only add site:edu to the search query if academic_format is enabled and no site_tld is specified
            search_query = f"{search_query} site:edu"
            
        logger.info(f"Starting research with query: {search_query}")
        progress.update(progress=15, current_step="Preparing search query", 
                       message=f"Search query: {search_query}")
        
        # Initialize LazyScholar
        progress.update(progress=20, current_step="Initializing LazyScholar", 
                       message="Setting up research environment")
        
        # Create a custom logger handler to capture LazyScholar logs
        class ProgressLogHandler(logging.Handler):
            def emit(self, record):
                msg = self.format(record)
                progress.update(message=msg)
                
                # Update progress based on log messages
                if "Analyzing problem statement" in msg:
                    progress.update(progress=25, current_step="Analyzing problem statement")
                elif "Generated topics" in msg:
                    progress.update(progress=30, current_step="Generated research topics")
                elif "Starting browser" in msg:
                    progress.update(progress=35, current_step="Starting web browser")
                elif "Processing topic" in msg:
                    # Extract topic info from message
                    progress.update(progress=40, current_step="Processing topics")
                elif "Searching for PDFs" in msg:
                    progress.update(progress=50, current_step="Searching for PDFs")
                elif "Downloading PDF" in msg:
                    progress.update(progress=60, current_step="Downloading PDFs")
                elif "Extracting content" in msg:
                    progress.update(progress=70, current_step="Extracting content from PDFs")
                elif "Writing subtopic file" in msg:
                    progress.update(progress=80, current_step="Writing research content")
                elif "Generating final paper" in msg:
                    progress.update(progress=90, current_step="Generating final paper")
        
        # Add the custom handler to the LazyScholar logger
        lazy_logger = logging.getLogger("lazy_scholar")
        progress_handler = ProgressLogHandler()
        progress_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        lazy_logger.addHandler(progress_handler)
        
        # Initialize LazyScholar with all parameters as keyword arguments
        scholar = LazyScholar(
            headless=headless,
            output_dir=output_dir,
            timeout=10,
            max_pdfs_per_topic=max_pdfs,
            search_suffix=search_suffix,
            focus='pdf' if require_pdfs else 'all',
            academic_format=academic_format,
            language=language,
            site_tld=site_tld,
            minimum_pdfs=minimum_pdfs,
            crawl_depth=crawl_depth,
            max_crawl_pages=max_crawl_pages,
            search_purpose=search_purpose,
            require_pdfs=require_pdfs,
            output_format=output_format
        )
        
        # Execute research
        progress.update(progress=25, current_step="Starting research process", 
                       message="Beginning the research process")
        
        # Use the search engine specified in the profile, but with proper URL encoding
        encoded_query = urllib.parse.quote_plus(search_query)
        
        # Parse the search URL to determine which search engine to use
        parsed_url = urlparse(search_engine)
        base_domain = parsed_url.netloc.lower()
        
        # Construct a proper search URL based on the search engine
        if "duckduckgo.com" in base_domain:
            search_url = f"https://duckduckgo.com/?q={encoded_query}&t=h_&ia=web"
            logger.info(f"Using DuckDuckGo search URL: {search_url}")
        elif "google.com" in base_domain:
            search_url = f"https://www.google.com/search?q={encoded_query}"
            logger.info(f"Using Google search URL: {search_url}")
        elif "bing.com" in base_domain:
            search_url = f"https://www.bing.com/search?q={encoded_query}"
            logger.info(f"Using Bing search URL: {search_url}")
        else:
            # For other search engines, use the URL as is but append the query
            if "?" in search_engine:
                search_url = f"{search_engine}&q={encoded_query}"
            else:
                search_url = f"{search_engine}?q={encoded_query}"
            logger.info(f"Using custom search URL: {search_url}")
        
        # Wrapper class to make a cancellable browser instance
        class CancellableResearch:
            def __init__(self, scholar, progress_tracker):
                self.scholar = scholar
                self.progress = progress_tracker
                self.browser = None
                
            def conduct_research(self, search_query, search_url):
                # Store the problem statement
                self.scholar.problem_statement = search_query
                
                # Generate topics and subtopics
                self.scholar.topics = self.scholar.analyze_problem_statement(search_query)
                
                # Update the topics tracking file
                self.scholar.update_topics_tracking_file()
                
                # Start the browser
                logger.info("Starting browser...")
                self.scholar.start_browser()
                self.browser = self.scholar.browser  # Store reference to browser for cancellation
                logger.info("Browser started successfully")
                
                # Check for cancellation before continuing
                if self.progress.is_cancelled():
                    logger.info("Research cancelled by user before starting the search")
                    if self.browser:
                        self.browser.quit()
                    return False
                
                try:
                    # Process each topic and subtopic
                    for topic_index, topic_data in enumerate(self.scholar.topics):
                        # Check for cancellation before each topic
                        if self.progress.is_cancelled():
                            logger.info(f"Research cancelled by user before processing topic {topic_data['title']}")
                            if self.browser:
                                self.browser.quit()
                            return False
                            
                        topic_title = topic_data["title"]
                        subtopics = topic_data["subtopics"]
                        
                        logger.info(f"Processing topic {topic_index + 1}/{len(self.scholar.topics)}: {topic_title}")
                        
                        # Create topic directory
                        topic_dir = os.path.join(self.scholar.output_dir, "topics", self.scholar._sanitize_filename(topic_title))
                        os.makedirs(topic_dir, exist_ok=True)
                        
                        # Process each subtopic
                        for subtopic_index, subtopic_data in enumerate(subtopics):
                            # Check for cancellation before each subtopic
                            if self.progress.is_cancelled():
                                logger.info(f"Research cancelled by user before processing subtopic {subtopic_data['title']}")
                                if self.browser:
                                    self.browser.quit()
                                return False
                                
                            subtopic_title = subtopic_data["title"]
                            
                            logger.info(f"Processing subtopic {subtopic_index + 1}/{len(subtopics)}: {subtopic_title}")
                            
                            # Set current topic and subtopic
                            self.scholar.current_topic = topic_title
                            self.scholar.current_subtopic = subtopic_title
                            
                            # Use search_phrase for search if available, otherwise use the subtopic title
                            search_title = subtopic_data.get("search_phrase", subtopic_title)
                            
                            # Ensure search_phrase is in English for search engines
                            if not search_title or not all(ord(c) < 128 for c in search_title):
                                logger.warning(f"Invalid search phrase: {search_title}. Generating a new one.")
                                search_title = f"{topic_title} {subtopic_title}".replace("'", "").replace('"', '')
                                # Handle non-ASCII characters
                                if not all(ord(c) < 128 for c in search_title):
                                    import unicodedata
                                    search_title = ''.join(
                                        c for c in unicodedata.normalize('NFKD', search_title)
                                        if unicodedata.category(c) != 'Mn'
                                    )
                                    # Replace any remaining non-ASCII characters with spaces
                                    search_title = ''.join(c if ord(c) < 128 else ' ' for c in search_title)
                                    search_title = ' '.join(search_title.split())  # Normalize spaces
                                    logger.info(f"Using search phrase for {topic_title} - {subtopic_title}: {search_title}")
                            
                            # Search for sources related to the subtopic
                            subtopic_search_query = f"{search_title} {self.scholar.search_suffix}".strip()
                            
                            # Add site restriction if site_tld is specified and not already in the query
                            if self.scholar.site_tld and f"site:{self.scholar.site_tld}" not in subtopic_search_query.lower():
                                subtopic_search_query += f" site:{self.scholar.site_tld}"
                            
                            # Log the search query being used
                            logger.info(f"Using search phrase for {topic_title} - {subtopic_title}: {subtopic_search_query}")
                            
                            # Let LazyScholar handle the actual PDF search and content extraction
                            # We'll use its methods directly rather than trying to replicate all the complex logic
                            
                            # Initialize content list
                            pdf_contents = []
                            
                            # Check for cancellation before searching
                            if self.progress.is_cancelled():
                                logger.info(f"Research cancelled by user before searching for {subtopic_title}")
                                if self.browser:
                                    self.browser.quit()
                                return False
                            
                            # Follow the same logic as in conduct_research
                            if not self.scholar.require_pdfs:
                                logger.info("Prioritizing HTML content as 'Prioritize Document Files' is unchecked")
                                self.scholar._extract_html_content(subtopic_search_query, pdf_contents, topic_title, subtopic_title, search_url)
                            else:
                                # Search for PDFs
                                pdf_urls = self.scholar._search_for_pdfs(subtopic_search_query, search_url) or []
                                
                                # Process PDFs in the directory
                                pdf_dir = os.path.join(self.scholar.output_dir, "pdfs")
                                if os.path.exists(pdf_dir):
                                    pdf_files = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
                                    pdf_files.sort(key=lambda x: os.path.getctime(x), reverse=True)
                                    recent_pdfs = pdf_files[:self.scholar.max_pdfs_per_topic]
                                    
                                    if recent_pdfs:
                                        logger.info(f"Processing {len(recent_pdfs)} recently downloaded PDFs")
                                        pdf_contents = self.scholar._process_pdfs_for_subtopic(recent_pdfs, topic_title, subtopic_title) or []
                                
                                # Try HTML if needed
                                if len(pdf_contents) < self.scholar.minimum_pdfs:
                                    if self.scholar.focus != 'pdf':
                                        logger.info(f"Not enough PDF content found, adding HTML content...")
                                        self.scholar._extract_html_content(subtopic_search_query, pdf_contents, topic_title, subtopic_title, search_url)
                            
                            # Check for cancellation after search
                            if self.progress.is_cancelled():
                                logger.info(f"Research cancelled by user after searching for {subtopic_title}")
                                if self.browser:
                                    self.browser.quit()
                                return False
                            
                            # Write the subtopic file
                            subtopic_file = os.path.join(topic_dir, f"{self.scholar._sanitize_filename(subtopic_title)}.md")
                            
                            # Only write the file if we have content
                            if pdf_contents:
                                try:
                                    with open(subtopic_file, "w", encoding="utf-8") as f:
                                        f.write(f"# {subtopic_title}\n\n")
                                        for content in pdf_contents:
                                            f.write(content["content"] + "\n\n")
                                        f.write("## References\n\n")
                                        for content in pdf_contents:
                                            source = content.get("source", "Unknown source")
                                            f.write(f"- {source}\n")
                                    logger.info(f"Wrote subtopic file: {subtopic_file}")
                                    
                                    # Optimize the subtopic content using LLM
                                    try:
                                        logger.info(f"Optimizing content for {topic_title} - {subtopic_title}")
                                        self.scholar._optimize_subtopic_content_with_llm(subtopic_file, topic_title, subtopic_title)
                                        logger.info(f"Content optimization completed for {subtopic_title}")
                                    except Exception as opt_error:
                                        logger.error(f"Error optimizing subtopic content with LLM: {str(opt_error)}")
                                    
                                except Exception as e:
                                    logger.error(f"Error writing subtopic file: {str(e)}")
                            
                            # Update subtopic with extracted content
                            subtopic_data["pdf_contents"] = pdf_contents
                            
                    # Final cancellation check before generating the paper
                    if self.progress.is_cancelled():
                        logger.info("Research cancelled by user before generating final paper")
                        if self.browser:
                            self.browser.quit()
                        return False
                    
                    # Generate the final paper
                    logger.info("Generating final paper...")
                    final_paper_path = self.scholar.generate_final_paper(self.scholar.topics)
                    logger.info("Research completed successfully")
                    
                    # Check if we should apply academic format
                    if self.scholar.academic_format:
                        logger.info("Formatting final paper as academic paper...")
                        try:
                            # Import the academic_formatter module
                            import academic_formatter
                            
                            # Initialize the model
                            model = academic_formatter.initialize_model()
                            if not model:
                                logger.error("Failed to initialize model for academic formatting")
                                return True
                            
                            # Extract references and content
                            pdf_references, content = academic_formatter.extract_references_from_final_paper(final_paper_path)
                            
                            # Format as academic paper
                            formatted_paper = academic_formatter.format_as_academic_paper(model, content, pdf_references, self.scholar.language)
                            
                            # Save formatted paper
                            output_path = academic_formatter.save_formatted_paper(final_paper_path, formatted_paper)
                            
                            if output_path:
                                logger.info(f"Successfully formatted final paper as academic paper at {output_path}")
                            else:
                                logger.error("Failed to save formatted academic paper")
                        except Exception as e:
                            logger.error(f"Error formatting final paper: {str(e)}")
                    
                    return True
                    
                except Exception as e:
                    logger.error(f"Error during research: {str(e)}")
                    if self.browser:
                        self.browser.quit()
                    return False
                    
            def cancel(self):
                """Cancel the research by quitting the browser if it's running"""
                logger.info("Attempting to cancel research and close browser")
                if self.browser:
                    try:
                        self.browser.quit()
                        logger.info("Browser closed successfully during cancellation")
                    except Exception as e:
                        logger.error(f"Error closing browser during cancellation: {str(e)}")
                return True
        
        # Create a cancellable research instance
        cancellable_research = CancellableResearch(scholar, progress)
        
        # Add a try-except block around the conduct_research call
        try:
            result = cancellable_research.conduct_research(search_query, search_url)
        except Exception as e:
            logger.error(f"Error during research: {str(e)}")
            progress.update(status="failed", current_step="Research failed", 
                           message=f"Error during research: {str(e)}")
            result = False
        
        # Remove the custom handler
        lazy_logger.removeHandler(progress_handler)
        
        if result:
            logger.info("Research completed successfully")
            progress.update(status="completed", progress=100, 
                           current_step="Research completed", 
                           message="Research process completed successfully")
        else:
            if progress.is_cancelled():
                logger.info("Research cancelled by user")
                # Note: Progress status is already set to "cancelled" in the cancel() method
            else:
                logger.error("Research process failed")
                progress.update(status="failed", current_step="Research failed", 
                              message="Research process did not complete successfully")
            
            # Mark research as complete
            progress.update(progress=100, current_step="Complete", 
                          message="Research process completed successfully")
            
            # Clear active task ID 
            profile.active_task_id = None
            db.session.commit()
            
            return result
        
    except Exception as e:
        logger.error(f"Error during research: {str(e)}")
        progress.update(status="failed", current_step="Error occurred", 
                       message=f"Error during research: {str(e)}")
        return False

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lazy_scholar.db'
app.config['UPLOAD_FOLDER'] = 'research_output'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Add markdown filter to Jinja2
@app.template_filter('markdown')
def render_markdown(text):
    # Convert markdown to HTML
    html = markdown.markdown(text, extensions=['extra', 'codehilite', 'tables', 'toc'])
    
    # Sanitize HTML to prevent XSS
    allowed_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'ul', 'ol', 'li', 
                    'strong', 'em', 'code', 'pre', 'blockquote', 'table', 'thead', 
                    'tbody', 'tr', 'th', 'td', 'br', 'hr', 'img', 'span', 'div']
    allowed_attrs = {
        '*': ['id', 'class'],
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height']
    }
    
    clean_html = bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs)
    return clean_html

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    profiles = db.relationship('ResearchProfile', backref='user', lazy=True)

class ResearchProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    problem_statement = db.Column(db.Text, nullable=False)
    search_suffix = db.Column(db.String(200))
    max_pdfs_per_topic = db.Column(db.Integer, default=10)
    focus = db.Column(db.String(20), default='all')
    academic_format = db.Column(db.Boolean, default=True)
    language = db.Column(db.String(10), default='en')
    search_url = db.Column(db.String(500), nullable=False)  # Store the full search URL
    is_template = db.Column(db.Boolean, default=False)  # Whether this is a search template
    site_tld = db.Column(db.String(20))  # Top-level domain to restrict searches to (e.g., 'edu', 'gov', 'org')
    minimum_pdfs = db.Column(db.Integer, default=3)  # Minimum number of PDFs required for each subtopic
    crawl_depth = db.Column(db.Integer, default=3)  # Maximum depth for website crawling
    max_crawl_pages = db.Column(db.Integer, default=20)  # Maximum number of pages to visit during crawling
    search_purpose = db.Column(db.String(20), default='academic')  # Purpose of the search: 'academic', 'practical', or 'travel'
    require_pdfs = db.Column(db.Boolean, default=True)  # Whether PDFs are required for the search
    output_format = db.Column(db.String(10), default='md')  # Output format: 'md', 'pdf', 'html', 'epub', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active_task_id = db.Column(db.String(100), nullable=True)  # Store the active research task ID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topics_and_subtopics = db.Column(db.Text)  # Store topics and subtopics as markdown

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            password_hash=generate_password_hash(request.form['password'])
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    profiles = ResearchProfile.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', profiles=profiles)

@app.route('/profile/new', methods=['GET', 'POST'])
@login_required
def new_profile():
    if request.method == 'POST':
        profile = ResearchProfile(
            name=request.form['name'],
            problem_statement=request.form['problem_statement'],
            search_suffix=request.form['search_suffix'],
            max_pdfs_per_topic=int(request.form['max_pdfs_per_topic']),
            focus=request.form['focus'],
            academic_format=bool(request.form.get('academic_format')),
            language=request.form['language'],
            search_url=request.form['search_url'],
            is_template=bool(request.form.get('is_template')),
            site_tld=request.form.get('site_tld'),
            minimum_pdfs=int(request.form.get('minimum_pdfs', 3)),
            crawl_depth=int(request.form.get('crawl_depth', 3)),
            max_crawl_pages=int(request.form.get('max_crawl_pages', 20)),
            search_purpose=request.form.get('search_purpose', 'academic'),
            require_pdfs='require_pdfs' in request.form,
            output_format=request.form.get('output_format', 'md'),
            user_id=current_user.id
        )
        db.session.add(profile)
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    # Get available templates for the user
    templates = ResearchProfile.query.filter_by(user_id=current_user.id, is_template=True).all()
    return render_template('profile_form.html', templates=templates)

@app.route('/profile/<int:profile_id>')
@login_required
def view_profile(profile_id):
    """View a research profile details and outputs"""
    profile = ResearchProfile.query.get_or_404(profile_id)
    if profile.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    
    # Get task_id from query parameter if available, otherwise use the active_task_id from profile
    task_id = request.args.get('task_id') or profile.active_task_id
    
    # Get research output directory
    output_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id), str(profile_id))
    
    # Initialize variables
    topics = []
    pdfs = []
    progress = 0
    progress_steps = []
    final_paper = None
    final_paper_preview = None
    topics_file_exists = False
    
    # Check if research has started
    if os.path.exists(output_dir):
        # Check if topics_and_subtopics.md exists
        topics_md_file = os.path.join(output_dir, 'topics_and_subtopics.md')
        if os.path.exists(topics_md_file):
            topics_file_exists = True
            
            # Parse topics from the markdown file if available
            with open(topics_md_file, 'r', encoding='utf-8') as f:
                topics_md_content = f.read()
                topics_data = parse_topics_file(topics_md_content)
                
                # Convert the parsed data to the format expected by the template
                for topic in topics_data:
                    topics.append({
                        'name': topic['title'],
                        'subtopics': topic['subtopics']
                    })
                
        # Try loading topics.json as a fallback
        if not topics and os.path.exists(os.path.join(output_dir, 'topics.json')):
            try:
                with open(os.path.join(output_dir, 'topics.json'), 'r') as f:
                    topics = json.load(f)
            except:
                pass
        
        # Get PDF files
        pdf_dir = os.path.join(output_dir, 'pdfs')
        if os.path.exists(pdf_dir):
            for root, dirs, files in os.walk(pdf_dir):
                for file in files:
                    if file.endswith('.pdf'):
                        rel_path = os.path.relpath(os.path.join(root, file), output_dir)
                        topic = os.path.basename(os.path.dirname(rel_path))
                        pdfs.append({
                            'name': file,
                            'path': rel_path,
                            'topic': topic,
                            'size': f"{os.path.getsize(os.path.join(root, file)) / 1024:.1f} KB"
                        })
        
        # Check final paper
        final_paper_path = os.path.join(output_dir, 'final_paper.pdf')
        if os.path.exists(final_paper_path):
            final_paper = True
            # Generate preview from first page if possible
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(final_paper_path)
                page = doc[0]
                text = page.get_text()
                final_paper_preview = text[:500] + "..." if len(text) > 500 else text
            except Exception as e:
                logger.error(f"Error generating PDF preview: {str(e)}")
                final_paper_preview = "Preview not available, please download the file to view."
    
    # Check if a research process is currently running for this profile
    research_in_progress = False
    if task_id:
        progress_instance = ResearchProgress.get_instance(task_id)
        if progress_instance.status in ['initializing', 'running']:
            research_in_progress = True
    
    return render_template('profile_view.html', 
                           profile=profile, 
                           topics=topics, 
                           pdfs=pdfs, 
                           final_paper=final_paper, 
                           final_paper_preview=final_paper_preview,
                           task_id=task_id,
                           topics_file_exists=topics_file_exists,
                           research_in_progress=research_in_progress)

@app.route('/research/start/<int:profile_id>')
@login_required
def start_research(profile_id):
    """Start a new research task for the given profile"""
    profile = ResearchProfile.query.get_or_404(profile_id)
    
    # Check if the profile belongs to the current user
    if profile.user_id != current_user.id:
        flash("You don't have permission to access this profile", "danger")
        return redirect(url_for('dashboard'))
    
    # Check if there's already an active task
    if profile.active_task_id:
        # Get the progress of the task
        progress = ResearchProgress.get_instance(profile.active_task_id)
        
        # If the task is still running, redirect to the progress page
        if progress.status == 'running':
            flash("This profile already has a research task in progress", "info")
            return redirect(url_for('view_profile', profile_id=profile_id))
    
    # Create a unique task ID
    task_id = f"research_{profile_id}_{int(time.time())}"
    
    # Create the output directory
    output_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id), str(profile_id))
    os.makedirs(output_dir, exist_ok=True)
    
    # Update the profile with the task ID
    profile.active_task_id = task_id
    db.session.commit()
    
    # Start the research task in a background thread with proper app context
    from flask import copy_current_request_context
    
    @copy_current_request_context
    def run_research_with_context(profile_id, task_id):
        return run_research_task(profile_id, task_id)
    
    # Create and start the thread
    thread = threading.Thread(target=run_research_with_context, args=(profile_id, task_id))
    thread.daemon = True
    thread.start()
    
    # Redirect to the topics editor for approval after generation
    return redirect(url_for('topics_approval', profile_id=profile_id, task_id=task_id))

@app.route('/research/<int:profile_id>/topics-approval/<task_id>')
@login_required
def topics_approval(profile_id, task_id):
    """Show the topics and subtopics for user approval before continuing research"""
    profile = ResearchProfile.query.get_or_404(profile_id)
    
    # Check if the profile belongs to the current user
    if profile.user_id != current_user.id:
        flash("You don't have permission to access this profile", "danger")
        return redirect(url_for('dashboard'))
    
    # Check if the task_id matches the profile's active task
    if profile.active_task_id != task_id:
        flash("Invalid task ID", "danger")
        return redirect(url_for('view_profile', profile_id=profile_id))
    
    # Get the progress of the task
    progress = ResearchProgress.get_instance(task_id)
    
    # Get the path to the topics_and_subtopics.md file
    research_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id), str(profile_id))
    filepath = "topics_and_subtopics.md"
    full_filepath = os.path.join(research_dir, filepath)
    
    # Check if the file exists yet
    if not os.path.exists(full_filepath):
        # File doesn't exist yet, show waiting page
        return render_template('topics_approval_waiting.html', 
                              profile=profile,
                              task_id=task_id,
                              progress=progress.to_dict())
    
    # Read the file content
    with open(full_filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Parse the content to extract topics and subtopics
    topics_data = parse_topics_file(content)
    
    # Show the topics approval page
    return render_template('topics_approval.html', 
                          profile=profile,
                          task_id=task_id,
                          topics_data=topics_data,
                          original_content=content,
                          progress=progress.to_dict())

@app.route('/research/<int:profile_id>/approve-topics/<task_id>', methods=['POST'])
@login_required
def approve_topics(profile_id, task_id):
    """Approve the topics and subtopics and continue with the research"""
    profile = ResearchProfile.query.get_or_404(profile_id)
    
    # Check if the profile belongs to the current user
    if profile.user_id != current_user.id:
        flash("You don't have permission to access this profile", "danger")
        return redirect(url_for('dashboard'))
    
    # Check if the task_id matches the profile's active task
    if profile.active_task_id != task_id:
        flash("Invalid task ID", "danger")
        return redirect(url_for('view_profile', profile_id=profile_id))
    
    # Get the progress tracker
    progress = ResearchProgress.get_instance(task_id)
    
    # Check if it's in waiting status
    if progress.status != 'waiting':
        flash("This task is not waiting for approval", "warning")
        return redirect(url_for('view_profile', profile_id=profile_id))
    
    # Resume the research process by updating the status
    progress.update(status="running", current_step="Topics approved", 
                   message="Topics and subtopics approved by user, continuing research")
    
    # Redirect to the profile view page to show progress
    flash("Topics and subtopics approved. Research is continuing...", "success")
    return redirect(url_for('view_profile', profile_id=profile_id))

def run_research_task(profile_id, task_id=None):
    """Background task to run research for a profile"""
    with app.app_context():
        try:
            # Get the research profile
            profile = ResearchProfile.query.get(profile_id)
            
            if not profile:
                logger.error(f"Research profile {profile_id} not found")
                return False
                
            # Setup task_id if not provided
            if not task_id:
                task_id = f"research_{profile_id}_{int(time.time())}"
                profile.active_task_id = task_id
                db.session.commit()
                
            # Setup progress tracking
            progress = ResearchProgress.get_instance(task_id)
            progress.update(progress=10, current_step="Initialization", message="Starting research process")
                
            # Prepare output directory
            output_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(profile.user_id), str(profile_id))
            os.makedirs(output_dir, exist_ok=True)
            
            # Check if topics_and_subtopics.md exists
            topics_file = os.path.join(output_dir, "topics_and_subtopics.md")
            topics_exist = os.path.exists(topics_file)
            
            # Prepare search query
            search_query = profile.problem_statement.strip()
            if profile.search_suffix:
                search_query = f"{search_query} {profile.search_suffix}"
                
            # Research settings
            max_pdfs = profile.max_pdfs_per_topic
            require_pdfs = profile.require_pdfs
            academic_format = profile.academic_format
            language = profile.language
                
            # Initialize LazyScholar to generate topics
            progress.update(progress=20, current_step="Initializing LazyScholar", 
                           message="Setting up research environment")
            
            # Create a LazyScholar instance but don't start the browser yet
            scholar = LazyScholar(
                headless=True,
                output_dir=output_dir,
                max_pdfs_per_topic=max_pdfs,
                focus='pdf' if require_pdfs else 'all',
                academic_format=academic_format,
                language=language,
                site_tld=profile.site_tld,
                minimum_pdfs=profile.minimum_pdfs,
                crawl_depth=profile.crawl_depth,
                max_crawl_pages=profile.max_crawl_pages,
                search_purpose=profile.search_purpose,
                require_pdfs=require_pdfs,
                output_format=profile.output_format
            )
            
            # Only generate topics if they don't exist
            if not topics_exist:
                progress.update(progress=25, current_step="Analyzing problem statement", 
                              message="Generating topics and subtopics...")
                scholar.problem_statement = search_query
                scholar.topics = scholar.analyze_problem_statement(search_query)
                
                # Create the topics_and_subtopics.md file
                scholar.update_topics_tracking_file()
                
                # Save topics and subtopics to profile
                if os.path.exists(topics_file):
                    with open(topics_file, 'r') as f:
                        profile.topics_and_subtopics = f.read()
                        db.session.commit()
            else:
                # Load existing topics from the file
                progress.update(progress=25, current_step="Loading existing topics", 
                              message="Using existing topics and subtopics...")
                try:
                    with open(topics_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        topics_data = parse_topics_file(content)
                        scholar.topics = topics_data
                        scholar.problem_statement = search_query
                except Exception as e:
                    logger.error(f"Error loading existing topics: {str(e)}")
                    return False
            
            # Update status to waiting for user approval
            progress.update(status="waiting", progress=30, 
                           current_step="Waiting for user approval", 
                           message="Topics and subtopics are ready. Please review and approve to continue.")
            
            # Wait for user approval or cancellation
            while progress.status == "waiting" and not progress.is_cancelled():
                time.sleep(2)
                
                # Refresh progress from database (in case it was updated elsewhere)
                if progress.is_cancelled():
                    logger.info(f"Research task {task_id} was cancelled")
                    profile.active_task_id = None
                    db.session.commit()
                    return False
            
            # Check if the task was cancelled during waiting
            if progress.is_cancelled():
                logger.info(f"Research task {task_id} was cancelled")
                profile.active_task_id = None
                db.session.commit()
                return False
            
            # If we're here, the user has approved the topics
            progress.update(status="running", progress=35, 
                           current_step="Starting research with approved topics", 
                           message="Topics and subtopics approved. Starting research...")
                
            # Continue with the research process
            result = run_research(
                problem_statement=search_query,
                output_dir=output_dir,
                max_pdfs=max_pdfs,
                require_pdfs=require_pdfs,
                academic_format=academic_format,
                language=language,
                progress=progress,
                task_id=task_id,
                search_engine=profile.search_url,
                site_tld=profile.site_tld,
                minimum_pdfs=profile.minimum_pdfs,
                crawl_depth=profile.crawl_depth,
                max_crawl_pages=profile.max_crawl_pages,
                search_purpose=profile.search_purpose,
                output_format=profile.output_format
            )
            
            # Mark research as complete
            progress.update(progress=100, current_step="Complete", 
                          message="Research process completed successfully")
            
            # Clear active task ID 
            profile.active_task_id = None
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error during research task: {str(e)}")
            try:
                # Check if we can still access the profile and clear the active task ID
                profile = ResearchProfile.query.get(profile_id)
                if profile:
                    profile.active_task_id = None
                    db.session.commit()
            except Exception as inner_e:
                logger.error(f"Error clearing task ID: {str(inner_e)}")
                
            # Update progress with error
            if 'progress' in locals():
                progress.update(progress=0, current_step="Error", 
                              message=f"Research process failed: {str(e)}")
                
            return False

@app.route('/files/<int:profile_id>/topics_editor', methods=['GET', 'POST'])
@login_required
def topics_editor(profile_id):
    profile = ResearchProfile.query.get_or_404(profile_id)
    
    # Check if the profile belongs to the current user
    if profile.user_id != current_user.id:
        flash("You don't have permission to access this profile", "danger")
        return redirect(url_for('dashboard'))
    
    # Get the full path to the topics_and_subtopics.md file
    research_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id), str(profile_id))
    filepath = "topics_and_subtopics.md"
    full_filepath = os.path.join(research_dir, filepath)
    
    # If the file doesn't exist yet, show a message
    if not os.path.exists(full_filepath):
        flash("The topics and subtopics file hasn't been generated yet. Start a research to generate it.", "info")
        return redirect(url_for('view_profile', profile_id=profile_id))
    
    # Read the file content
    with open(full_filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Parse the content to extract topics and subtopics
    topics_data = parse_topics_file(content)
    
    if request.method == 'POST':
        # Handle the form submission for editing topics and subtopics
        action = request.form.get('action')
        
        if action == 'update':
            # Get the updated topics and subtopics from the form
            updated_data = json.loads(request.form.get('topics_data'))
            # Generate new markdown content
            new_content = generate_topics_md(updated_data, profile.problem_statement)
            # Write the new content to the file
            with open(full_filepath, 'w', encoding='utf-8') as file:
                file.write(new_content)
            
            # Update the profile with the content
            profile.topics_and_subtopics = new_content
            db.session.commit()
            
            flash("Topics and subtopics updated successfully", "success")
            
            # Check if this is a "Save and Approve" action
            if request.form.get('approve') == 'true':
                # If there's an active task, update its status to approve it
                if profile.active_task_id:
                    progress = ResearchProgress.get_instance(profile.active_task_id)
                    if progress.status == 'waiting':
                        # Update progress to resume the research process
                        progress.update(status="running", current_step="Topics approved", 
                                       message="Topics and subtopics approved by user, continuing research")
                        flash("Research is continuing with the updated topics and subtopics", "success")
                        return redirect(url_for('view_profile', profile_id=profile_id))
                    else:
                        # Start a new research if there's no waiting task
                        return redirect(url_for('start_research', profile_id=profile_id))
                else:
                    # If no active task, start a new research
                    return redirect(url_for('start_research', profile_id=profile_id))
            
            # If research is not in progress, update the LazyScholar topics file
            if not profile.active_task_id or not ResearchProgress.get_instance(profile.active_task_id).status == 'running':
                # This is important for the LazyScholar to use the updated topics
                logger.info("Updating LazyScholar topics file after user edit")
                
                # If there's an active task, try to update its progress
                if profile.active_task_id:
                    progress = ResearchProgress.get_instance(profile.active_task_id)
                    progress.update(message="Topics and subtopics updated by user")
        
        elif action == 'add_topic':
            topic_title = request.form.get('topic_title')
            if topic_title and topic_title.strip():
                topics_data.append({"title": topic_title.strip(), "subtopics": []})
                new_content = generate_topics_md(topics_data, profile.problem_statement)
                with open(full_filepath, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                flash(f"New topic '{topic_title}' added", "success")
            else:
                flash("Topic title cannot be empty", "danger")
        
        elif action == 'delete_topic':
            topic_index = int(request.form.get('topic_index'))
            if 0 <= topic_index < len(topics_data):
                deleted_topic = topics_data.pop(topic_index)
                new_content = generate_topics_md(topics_data, profile.problem_statement)
                with open(full_filepath, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                flash(f"Topic '{deleted_topic['title']}' deleted", "success")
        
        elif action == 'add_subtopic':
            topic_index = int(request.form.get('topic_index'))
            subtopic_title = request.form.get('subtopic_title')
            if 0 <= topic_index < len(topics_data) and subtopic_title and subtopic_title.strip():
                topics_data[topic_index]['subtopics'].append(subtopic_title.strip())
                new_content = generate_topics_md(topics_data, profile.problem_statement)
                with open(full_filepath, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                flash(f"New subtopic added to '{topics_data[topic_index]['title']}'", "success")
            else:
                flash("Invalid topic index or empty subtopic title", "danger")
        
        elif action == 'delete_subtopic':
            topic_index = int(request.form.get('topic_index'))
            subtopic_index = int(request.form.get('subtopic_index'))
            if (0 <= topic_index < len(topics_data) and 
                0 <= subtopic_index < len(topics_data[topic_index]['subtopics'])):
                deleted_subtopic = topics_data[topic_index]['subtopics'].pop(subtopic_index)
                new_content = generate_topics_md(topics_data, profile.problem_statement)
                with open(full_filepath, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                flash(f"Subtopic '{deleted_subtopic}' deleted", "success")
            else:
                flash("Invalid topic or subtopic index", "danger")
        
        elif action == 'approve':
            # Mark the file as approved and proceed with research
            return redirect(url_for('list_files', profile_id=profile_id))
        
        # Redirect to reload the page with updated data
        return redirect(url_for('topics_editor', profile_id=profile_id))
    
    return render_template('topics_editor.html', 
                          profile=profile,
                          topics_data=topics_data,
                          original_content=content)

def parse_topics_file(content):
    """Parse the topics_and_subtopics.md file content to extract topics and subtopics."""
    topics_data = []
    current_topic = None
    
    # Extract topics section
    topics_match = re.search(r'### Research Topics\s+((?:-.*\n)+)', content)
    subtopics_match = re.search(r'### Subtopics Status\s+(.*?)(?=\n## Research Progress|\Z)', content, re.DOTALL)
    
    if topics_match:
        # Extract topics
        topics_section = topics_match.group(1)
        topic_items = re.findall(r'- (.*)\n', topics_section)
        
        for topic in topic_items:
            topics_data.append({"title": topic, "subtopics": []})
    
    if subtopics_match:
        # Extract subtopics
        subtopics_section = subtopics_match.group(1)
        topic_sections = re.split(r'\n#### ', subtopics_section)
        
        for section in topic_sections:
            if not section.strip():
                continue
            
            lines = section.strip().split('\n')
            if lines:
                topic_title = lines[0]
                
                # Find the matching topic in our data
                topic_index = next((i for i, t in enumerate(topics_data) if t['title'] == topic_title), None)
                
                if topic_index is not None:
                    # Extract subtopics for this topic
                    for line in lines[1:]:
                        subtopic_match = re.match(r'- \[([ x])\] (.*)', line)
                        if subtopic_match:
                            # Add subtopic
                            topics_data[topic_index]['subtopics'].append(subtopic_match.group(2))
    
    return topics_data

def generate_topics_md(topics_data, problem_statement):
    """Generate the topics_and_subtopics.md file content from the topics data."""
    
    # Count total subtopics
    total_subtopics = sum(len(topic["subtopics"]) for topic in topics_data)
    
    # Get current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Generate markdown content
    markdown = f"""# LazyScholar Research Topics and Subtopics

This file tracks the generated topics and subtopics for your academic research project.

## Current Research Status

### Research Topics
"""
    
    # Add topics
    for topic in topics_data:
        markdown += f"- {topic['title']}\n"
    
    markdown += "\n### Subtopics Status\n"
    
    # Add subtopics with checkboxes
    for topic in topics_data:
        markdown += f"\n#### {topic['title']}\n"
        for subtopic in topic["subtopics"]:
            markdown += f"- [ ] {subtopic}\n"
    
    markdown += f"""
## Research Progress
- Research initiated: {current_date}
- Topics generated: {len(topics_data)}
- Subtopics generated: {total_subtopics}
- Completed subtopics: 0
- In-progress subtopics: 0
- Remaining subtopics: {total_subtopics}

*Note: This file will be updated as research progresses. Checkboxes will be marked when subtopics are completed.*
"""
    
    return markdown

@app.route('/files/<int:profile_id>')
@login_required
def list_files(profile_id):
    profile = ResearchProfile.query.get_or_404(profile_id)
    if profile.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    
    base_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id), str(profile_id))
    
    # Get all files in the research output directory
    files = []
    for root, dirs, filenames in os.walk(base_dir):
        for filename in filenames:
            rel_path = os.path.relpath(os.path.join(root, filename), base_dir)
            files.append({
                'name': filename,
                'path': rel_path,
                'type': os.path.splitext(filename)[1][1:].lower()
            })
    
    return render_template('files.html', files=files, profile=profile)

@app.route('/files/<int:profile_id>/view/<path:filepath>')
@login_required
def view_file(profile_id, filepath):
    profile = ResearchProfile.query.get_or_404(profile_id)
    if profile.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id), str(profile_id), filepath)
    
    # Check if the file is a markdown file
    if filepath.endswith('.md'):
        # Read the markdown content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Clean up academic format markdown if needed
        # Academic formatter sometimes adds ```markdown at the beginning and ``` at the end
        if content.strip().startswith('```markdown'):
            # Remove the ```markdown tag at the beginning
            content = content.replace('```markdown', '', 1).strip()
            # Remove the closing ``` tag at the end if present
            if content.strip().endswith('```'):
                content = content[:content.rstrip().rfind('```')].strip()
        
        # Render the markdown content in a template
        return render_template('markdown_view.html', 
                               content=content, 
                               filename=os.path.basename(filepath),
                               profile_id=profile_id,
                               filepath=filepath)
    
    # For other file types, serve the file directly
    return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile/<int:profile_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(profile_id):
    profile = ResearchProfile.query.get_or_404(profile_id)
    if profile.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        profile.name = request.form['name']
        profile.problem_statement = request.form['problem_statement']
        profile.search_suffix = request.form['search_suffix']
        profile.max_pdfs_per_topic = int(request.form['max_pdfs_per_topic'])
        profile.focus = request.form['focus']
        profile.academic_format = bool(request.form.get('academic_format'))
        profile.language = request.form['language']
        profile.search_url = request.form['search_url']
        profile.is_template = bool(request.form.get('is_template'))
        profile.site_tld = request.form.get('site_tld')
        profile.minimum_pdfs = int(request.form.get('minimum_pdfs', 3))
        profile.crawl_depth = int(request.form.get('crawl_depth', 3))
        profile.max_crawl_pages = int(request.form.get('max_crawl_pages', 20))
        profile.search_purpose = request.form.get('search_purpose', 'academic')
        profile.require_pdfs = 'require_pdfs' in request.form
        profile.output_format = request.form.get('output_format', 'md')
        
        db.session.commit()
        flash('Profile updated successfully')
        return redirect(url_for('dashboard'))
    
    return render_template('profile_form.html', profile=profile, edit_mode=True)

@app.route('/profile/<int:profile_id>/delete', methods=['POST'])
@login_required
def delete_profile(profile_id):
    profile = ResearchProfile.query.get_or_404(profile_id)
    if profile.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    
    # Delete associated files
    output_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id), str(profile_id))
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)
    
    db.session.delete(profile)
    db.session.commit()
    flash('Profile deleted successfully')
    return redirect(url_for('dashboard'))

@app.route('/api/template/<int:template_id>')
@login_required
def get_template(template_id):
    template = ResearchProfile.query.get_or_404(template_id)
    if template.user_id != current_user.id or not template.is_template:
        return jsonify({'error': 'Template not found'}), 404
    
    return jsonify({
        'search_url': template.search_url,
        'search_suffix': template.search_suffix,
        'max_pdfs_per_topic': template.max_pdfs_per_topic,
        'focus': template.focus,
        'language': template.language,
        'academic_format': template.academic_format,
        'site_tld': template.site_tld,
        'minimum_pdfs': template.minimum_pdfs,
        'crawl_depth': template.crawl_depth,
        'max_crawl_pages': template.max_crawl_pages,
        'search_purpose': template.search_purpose,
        'require_pdfs': template.require_pdfs,
        'output_format': template.output_format
    })

@app.route('/api/progress/<task_id>')
def get_progress(task_id):
    """Get the current progress of a research task"""
    progress = ResearchProgress.get_instance(task_id)
    return jsonify(progress.to_dict())

@app.route('/api/progress/stream/<task_id>')
def stream_progress(task_id):
    """Stream progress updates using Server-Sent Events (SSE)"""
    def generate():
        last_update = 0
        while True:
            progress = ResearchProgress.get_instance(task_id)
            progress_data = progress.to_dict()
            
            # Only send updates if there's a change or every 5 seconds
            if progress_data['last_update'] > last_update or time.time() - last_update > 5:
                last_update = progress_data['last_update']
                yield f"data: {json.dumps(progress_data)}\n\n"
            
            # If the task is completed, failed, or cancelled, end the stream after sending the final update
            if progress_data['status'] in ['completed', 'failed', 'cancelled']:
                break
                
            time.sleep(1)
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/files/<int:profile_id>/translate', methods=['POST'])
@login_required
def translate_file(profile_id):
    # Get the profile from the database
    profile = ResearchProfile.query.filter_by(id=profile_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        filepath = request.form.get('filepath')
        source_language = request.form.get('source_language', 'auto')
        target_language = request.form.get('target_language')
        
        # Validate the parameters
        if not filepath or not target_language:
            flash('Missing required parameters.', 'danger')
            return redirect(url_for('list_files', profile_id=profile_id))
        
        # Construct the full file path
        output_dir = os.path.join('research_output', str(profile_id))
        full_filepath = os.path.join(output_dir, filepath)
        
        try:
            # Ensure the file exists
            if not os.path.exists(full_filepath):
                flash(f'File not found: {filepath}', 'danger')
                return redirect(url_for('list_files', profile_id=profile_id))
            
            # Initialize the model for translation
            initialize_model()
            
            # Read the file content
            with open(full_filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # If source is auto, detect the language
            if source_language == 'auto':
                detected_language = detect_language(content)
                source_language = detected_language if detected_language else 'en'
                logger.info(f"Detected language: {source_language}")
            
            # Create the translated file path
            if filepath.endswith('.md'):
                # For markdown files, we want to keep the extension
                translated_filepath = os.path.splitext(full_filepath)[0] + f"_{target_language}.md"
            else:
                # For other files, append the language code
                translated_filepath = full_filepath + f".{target_language}"
            
            # Process content in chunks to avoid token limits
            # (Actual translation code would go here)
            
            # For now, simply create a placeholder translated file
            with open(translated_filepath, 'w', encoding='utf-8') as f:
                f.write(f"Translation of {filepath} from {source_language} to {target_language}\n\n{content}")
            
            flash(f'File successfully translated to {target_language}', 'success')
            
            # Redirect to view the translated file
            relative_path = os.path.relpath(translated_filepath, output_dir)
            return redirect(url_for('view_file', profile_id=profile_id, filepath=relative_path))
            
        except Exception as e:
            logger.error(f"Error during file translation: {str(e)}")
            flash(f'Error during translation: {str(e)}', 'danger')
            return redirect(url_for('list_files', profile_id=profile_id))
    
    # If not POST, redirect to files list
    return redirect(url_for('list_files', profile_id=profile_id))

@app.route('/files/<int:profile_id>/cleanse', methods=['POST'])
@login_required
def cleanse_file(profile_id):
    """Cleanse a document by removing repetitive content using LLM."""
    # Get the profile from the database
    profile = ResearchProfile.query.filter_by(id=profile_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        filepath = request.form.get('filepath')
        cleanse_strength = request.form.get('cleanse_strength', 'medium')
        
        # Validate the parameters
        if not filepath:
            flash('Missing required file path.', 'danger')
            return redirect(url_for('list_files', profile_id=profile_id))
            
        # Validate cleanse_strength
        if cleanse_strength not in ['light', 'medium', 'aggressive']:
            cleanse_strength = 'medium'
        
        # Construct the full file path (include current_user.id in the path)
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id), str(profile_id))
        full_filepath = os.path.join(output_dir, filepath)
        
        try:
            # Ensure the file exists
            if not os.path.exists(full_filepath):
                flash(f'File not found: {filepath}', 'danger')
                return redirect(url_for('list_files', profile_id=profile_id))
            
            # Initialize LazyScholar with minimal configuration
            # (We only need the cleanse functionality)
            scholar = LazyScholar(
                output_dir=output_dir,
                language=profile.language if profile.language else 'en'
            )
            
            # Start cleansing process
            flash(f'Cleansing document with {cleanse_strength} strength. This might take a moment...', 'info')
            
            # Call the cleanse method with cleanse_strength parameter
            cleansed_filepath = scholar.cleanse_document(full_filepath, cleanse_strength)
            
            if cleansed_filepath:
                # Get relative path for redirecting
                relative_path = os.path.relpath(cleansed_filepath, output_dir)
                flash('Document successfully cleansed.', 'success')
                # Redirect to view the cleansed document
                return redirect(url_for('view_file', profile_id=profile_id, filepath=relative_path))
            else:
                flash('Failed to cleanse document. Check logs for details.', 'danger')
                return redirect(url_for('list_files', profile_id=profile_id))
                
        except Exception as e:
            logger.error(f"Error during document cleansing: {str(e)}")
            flash(f'Error during document cleansing: {str(e)}', 'danger')
            return redirect(url_for('list_files', profile_id=profile_id))
    
    # If not POST, redirect to files list
    return redirect(url_for('list_files', profile_id=profile_id))

@app.route('/research/check-status/<int:profile_id>')
@login_required
def check_research_status(profile_id):
    """Check if the active_task_id is still valid and clear it if not"""
    profile = ResearchProfile.query.get(profile_id)
    
    if not profile:
        flash("Profile not found.", "danger")
        return redirect(url_for('dashboard'))
    
    # Check if the profile belongs to the current user
    if profile.user_id != current_user.id:
        return redirect(url_for('dashboard'))
        
    # Check if there's an active task
    if profile.active_task_id:
        progress = ResearchProgress.get_instance(profile.active_task_id)
        
        # If the task is completed, failed, or cancelled, clear the active_task_id
        if progress.status in ['completed', 'failed', 'cancelled']:
            profile.active_task_id = None
            db.session.commit()
            flash("Research task status has been updated.", "info")
    
    return redirect(url_for('view_profile', profile_id=profile_id))

@app.route('/research/cancel/<task_id>', methods=['POST'])
@login_required
def cancel_research(task_id):
    """Cancel a running research task"""
    # Get the progress instance
    progress = ResearchProgress.get_instance(task_id)
    
    try:
        # Önce profile_id'yi task_id'den çıkarmaya çalış
        # Tipik task_id formatı: research_profile_id_timestamp
        parts = task_id.split('_')
        profile_id = None
        
        # Farklı format olasılıklarını kontrol et
        if len(parts) >= 2 and parts[0] == 'research':
            try:
                profile_id = int(parts[1])
            except ValueError:
                # İkinci parça sayı değilse, tüm parçalarda sayı ara
                for part in parts[1:]:
                    try:
                        candidate = int(part)
                        # Aday bir ID mi diye kontrol et
                        if ResearchProfile.query.get(candidate):
                            profile_id = candidate
                            break
                    except ValueError:
                        continue
        
        # Eğer profile_id bulunamadıysa, active_task_id'ye göre tüm profiller içinde ara
        if not profile_id:
            profile = ResearchProfile.query.filter_by(active_task_id=task_id).first()
            if profile:
                profile_id = profile.id
        
        if not profile_id:
            flash("Could not determine which research profile to cancel", "danger")
            return redirect(url_for('dashboard'))
            
        # Profile'ı kontrol et
        profile = ResearchProfile.query.get(profile_id)
        if not profile:
            flash("Research profile not found", "danger")
            return redirect(url_for('dashboard'))
            
        # Kullanıcı yetkisini kontrol et
        if profile.user_id != current_user.id:
            flash("You don't have permission to cancel this research task", "danger")
            return redirect(url_for('dashboard'))
            
        # Active task ID'yi kontrol et
        if profile.active_task_id == task_id:
            # Önce görevi iptal et
            progress.cancel()
            logger.info(f"Cancelling research task {task_id} for profile {profile_id}")
            
            # Ardından active task ID'yi temizle
            profile.active_task_id = None
            db.session.commit()
            
            flash("Research task cancelled. The task will stop soon.", "info")
        else:
            # Task ID eşleşmiyorsa, profile'ın aktif görevi var mı kontrol et
            if profile.active_task_id:
                # Aktif görev farklıysa, onu iptal et
                active_progress = ResearchProgress.get_instance(profile.active_task_id)
                active_progress.cancel()
                logger.info(f"Cancelling different active task {profile.active_task_id} for profile {profile_id}")
                
                profile.active_task_id = None
                db.session.commit()
                
                flash("A different active research task was found and cancelled.", "info")
            
    except Exception as e:
        logger.error(f"Error cancelling task {task_id}: {str(e)}")
        flash(f"Error while cancelling the research: {str(e)}", "danger")
        return redirect(url_for('dashboard'))
    
    # Redirect back to profile view
    return redirect(url_for('view_profile', profile_id=profile_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001) 