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
        self.status = "initializing"  # initializing, running, completed, failed
        self.progress = 0  # 0-100
        self.current_step = "Starting research..."
        self.details = {}
        self.messages = []
        self.last_update = time.time()
    
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
                "last_update": self.last_update
            }

# LazyScholar wrapper function
def run_research(problem_statement, output_dir, max_pdfs=10, academic_format=True, 
                language='en', search_suffix=None, headless=True, site_tld=None,
                minimum_pdfs=3, crawl_depth=3, max_crawl_pages=20, search_purpose='academic',
                require_pdfs=True, task_id=None, search_engine=None, output_format='md', translate_to=None):
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
        translate_to (str): Target language for translation (if requested)
        
    Returns:
        bool: True if research completed successfully, False otherwise
    """
    # Create or get progress tracker
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
            output_format=output_format,
            translate_to=translate_to
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
        
        # Add a try-except block around the conduct_research call
        try:
            result = scholar.conduct_research(search_query, search_url)
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
            logger.error("Research process failed")
            progress.update(status="failed", current_step="Research failed", 
                           message="Research process did not complete successfully")
            
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
    translate_to = db.Column(db.String(10))  # Target language for translation (if requested)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

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
            translate_to=request.form.get('translate_to'),
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
    profile = ResearchProfile.query.get_or_404(profile_id)
    if profile.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    
    # Get task_id from query parameter if available
    task_id = request.args.get('task_id')
    
    # Get research output directory
    output_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id), str(profile_id))
    
    # Initialize variables
    topics = []
    pdfs = []
    progress = 0
    progress_steps = []
    final_paper = None
    final_paper_preview = None
    
    # Check if research has started
    if os.path.exists(output_dir):
        # Load topics and subtopics
        topics_file = os.path.join(output_dir, 'topics.json')
        if os.path.exists(topics_file):
            with open(topics_file, 'r') as f:
                topics = json.load(f)
        
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
                final_paper_preview = text[:500] + '...' if len(text) > 500 else text
                doc.close()
            except:
                final_paper_preview = "Preview not available. Please download the PDF to view."
        
        # Calculate progress
        total_steps = 4  # Topics, PDFs, Analysis, Final Paper
        completed_steps = 0
        if topics:
            completed_steps += 1
        if pdfs:
            completed_steps += 1
        if os.path.exists(os.path.join(output_dir, 'analysis')):
            completed_steps += 1
        if final_paper:
            completed_steps += 1
        progress = (completed_steps / total_steps) * 100
        
        # Create progress steps
        progress_steps = [
            {
                'name': 'Topic Generation',
                'status': 'completed' if topics else 'pending',
                'details': f"{len(topics)} topics generated" if topics else None
            },
            {
                'name': 'PDF Collection',
                'status': 'completed' if pdfs else 'pending',
                'details': f"{len(pdfs)} PDFs collected" if pdfs else None
            },
            {
                'name': 'Content Analysis',
                'status': 'completed' if os.path.exists(os.path.join(output_dir, 'analysis')) else 'pending'
            },
            {
                'name': 'Final Paper',
                'status': 'completed' if final_paper else 'pending'
            }
        ]
    
    return render_template('profile_view.html',
                         profile=profile,
                         topics=topics,
                         pdfs=pdfs,
                         progress=progress,
                         progress_steps=progress_steps,
                         final_paper=final_paper,
                         final_paper_preview=final_paper_preview,
                         task_id=task_id)

@app.route('/research/start/<int:profile_id>')
@login_required
def start_research(profile_id):
    profile = ResearchProfile.query.get_or_404(profile_id)
    if profile.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    
    # Prepare output directory
    output_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id), str(profile_id))
    
    # Generate a unique task ID
    task_id = f"research_{profile_id}_{int(time.time())}"
    
    # Initialize progress tracker
    progress = ResearchProgress.get_instance(task_id)
    progress.update(status="initializing", progress=0, 
                   current_step="Preparing research", 
                   message=f"Initializing research for: {profile.name}")
    
    # Start research in a background thread
    def run_research_task():
        try:
            # Use the wrapper function to run research
            result = run_research(
                problem_statement=profile.problem_statement,
                output_dir=output_dir,
                max_pdfs=profile.max_pdfs_per_topic,
                academic_format=profile.academic_format,
                language=profile.language,
                search_suffix=profile.search_suffix,
                headless=True,
                site_tld=profile.site_tld,
                minimum_pdfs=profile.minimum_pdfs,
                crawl_depth=profile.crawl_depth,
                max_crawl_pages=profile.max_crawl_pages,
                search_purpose=profile.search_purpose,
                require_pdfs=profile.require_pdfs,
                task_id=task_id,
                search_engine=profile.search_url,  # Pass the search URL from the profile
                output_format=profile.output_format,
                translate_to=profile.translate_to
            )
        except Exception as e:
            app.logger.error(f"Research error for profile {profile_id}: {str(e)}")
            progress = ResearchProgress.get_instance(task_id)
            progress.update(status="failed", current_step="Error occurred", 
                           message=f"Unhandled error: {str(e)}")
    
    # Start the thread
    thread = threading.Thread(target=run_research_task)
    thread.daemon = True
    thread.start()
    
    flash('Research started. You can view the progress on this page.')
    return redirect(url_for('view_profile', profile_id=profile_id, task_id=task_id))

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
        profile.translate_to = request.form.get('translate_to')
        
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
        'output_format': template.output_format,
        'translate_to': template.translate_to
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
            
            # If the task is completed or failed, end the stream after sending the final update
            if progress_data['status'] in ['completed', 'failed']:
                break
                
            time.sleep(1)
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001) 