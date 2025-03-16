from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
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

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# LazyScholar wrapper function
def run_research(problem_statement, output_dir, max_pdfs=10, academic_format=True, 
                language='en', search_suffix=None, headless=True):
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
        
    Returns:
        bool: True if research completed successfully, False otherwise
    """
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Prepare search query
        search_query = problem_statement.strip()
        if search_suffix:
            search_query = f"{search_query} {search_suffix}"
            
        # Add filters to search query
        if "filetype:pdf" not in search_query.lower():
            search_query = f"{search_query} filetype:pdf"
        
        if academic_format and "site:edu" not in search_query.lower():
            search_query = f"{search_query} site:edu"
            
        logger.info(f"Starting research with query: {search_query}")
        
        # Initialize LazyScholar with search_query as first positional argument
        # and all other parameters as keyword arguments
        scholar = LazyScholar(
            headless=headless,
            output_dir=output_dir,
            timeout=10,
            max_pdfs_per_topic=max_pdfs,
            search_suffix=search_suffix,
            focus='pdf',
            academic_format=academic_format,
            language=language
        )
        
        # Execute research
        result = scholar.conduct_research(problem_statement, "https://duckduckgo.com")
        
        if result:
            logger.info("Research completed successfully")
        else:
            logger.error("Research process failed")
            
        return result
        
    except Exception as e:
        logger.error(f"Error during research: {str(e)}")
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
                         final_paper_preview=final_paper_preview)

@app.route('/research/start/<int:profile_id>')
@login_required
def start_research(profile_id):
    profile = ResearchProfile.query.get_or_404(profile_id)
    if profile.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    
    try:
        # Prepare output directory
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id), str(profile_id))
        
        # Use the wrapper function to run research
        result = run_research(
            problem_statement=profile.problem_statement,
            output_dir=output_dir,
            max_pdfs=profile.max_pdfs_per_topic,
            academic_format=profile.academic_format,
            language=profile.language,
            search_suffix=profile.search_suffix,
            headless=True
        )
        
        # Handle result
        if result:
            flash('Research completed successfully')
        else:
            flash('Research process did not complete successfully')
            
    except Exception as e:
        flash(f'Error during research: {str(e)}')
        app.logger.error(f"Research error for profile {profile_id}: {str(e)}")
    
    return redirect(url_for('view_profile', profile_id=profile_id))

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
        'academic_format': template.academic_format
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001) 