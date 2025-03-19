from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, current_user, login_user, logout_user
import requests
import os
from models import db, Course, Handbook, GitHubProject, ResearchPaper, Blog, User, ResourceRequest, Bookmark
from dotenv import load_dotenv
from functools import wraps
from datetime import datetime

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "YOUR_GOOGLE_API_KEY")
CSE_ID = os.environ.get("CSE_ID", "YOUR_CSE_ID")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///knowledge_base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # Required for session management

# Initialize the database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('You need admin privileges to access this page.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Create database tables
with app.app_context():
    db.create_all()
    # Create admin user if none exists
    if not User.query.filter_by(is_admin=True).first():
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('admin123')  # Change this in production!
        db.session.add(admin)
        db.session.commit()
    
    # Add some sample data if the database is empty
    if not Course.query.first():
        sample_courses = [
            Course(title="Coursera Machine Learning", 
                  url="https://www.coursera.org/learn/machine-learning", 
                  platform="Coursera", 
                  description="Stanford's Machine Learning course by Andrew Ng"),
            Course(title="Fast.ai Deep Learning", 
                  url="https://course.fast.ai/", 
                  platform="Fast.ai", 
                  description="Practical Deep Learning for Coders"),
            Course(title="MIT Introduction to Deep Learning", 
                  url="http://introtodeeplearning.com/", 
                  platform="MIT OCW", 
                  description="MIT's introductory course to deep learning methods") 
        ]
        db.session.add_all(sample_courses)
        db.session.commit()

    if not Handbook.query.first():
        sample_handbooks = [
            Handbook(title="Deep Learning Book", 
                    url="https://www.deeplearningbook.org/", 
                    author="Ian Goodfellow et al.", 
                    description="Comprehensive guide to deep learning fundamentals"),
            Handbook(title="Stanford CS229 Notes", 
                    url="https://cs229.stanford.edu/notes2022fall/main_notes.pdf", 
                    author="Stanford University", 
                    description="Stanford's machine learning course notes")
        ]
        db.session.add_all(sample_handbooks)
        db.session.commit()

    if not GitHubProject.query.first():
        sample_projects = [
            GitHubProject(title="Transformers", 
                         url="https://github.com/huggingface/transformers", 
                         stars=50000, 
                         description="State-of-the-art Natural Language Processing by Hugging Face"),
            GitHubProject(title="PyTorch", 
                         url="https://github.com/pytorch/pytorch", 
                         stars=45000, 
                         description="Open source machine learning framework")
        ]
        db.session.add_all(sample_projects)
        db.session.commit()

    if not ResearchPaper.query.first():
        sample_papers = [
            ResearchPaper(title="Attention Is All You Need", 
                         url="https://arxiv.org/abs/1706.03762", 
                         source="arXiv", 
                         description="Original transformer architecture paper that revolutionized NLP"),
            ResearchPaper(title="BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding", 
                         url="https://arxiv.org/abs/1810.04805", 
                         source="Google Research", 
                         description="Breakthrough paper introducing BERT model")
        ]
        db.session.add_all(sample_papers)
        db.session.commit()

    if not Blog.query.first():
        sample_blogs = [
            Blog(title="Towards Data Science", 
                 url="https://towardsdatascience.com/", 
                 platform="Medium", 
                 description="Community of data science enthusiasts sharing insights and tutorials"),
            Blog(title="OpenAI Blog", 
                 url="https://openai.com/blog", 
                 platform="OpenAI", 
                 description="Latest research and developments from OpenAI")
        ]
        db.session.add_all(sample_blogs)
        db.session.commit()

# Sample data - in a real app, you would connect to APIs or databases
resources = {
    "tutorials": [
        {"title": "Flask Web Development", "url": "#", "category": "Tutorials", "description": "Learn Flask from scratch"},
        {"title": "Python for Data Science", "url": "#", "category": "Tutorials", "description": "Python basics for DS"}
    ],
    "github": [
        {"title": "Flask-SQLAlchemy", "url": "#", "category": "GitHub", "description": "ORM for Flask"},
        {"title": "TensorFlow", "url": "#", "category": "GitHub", "description": "Machine learning framework"}
    ],
    "research": [
        {"title": "Deep Learning Advances", "url": "#", "category": "Research", "description": "Latest research in DL"},
        {"title": "NLP Techniques", "url": "#", "category": "Research", "description": "Natural language processing papers"}
    ]
}

CATEGORY_FILTERS = {
    "all": "",  # No filter - search the entire web
    "tutorials": "site:tutorialspoint.com OR site:w3schools.com OR site:freecodecamp.org OR site:realpython.com OR site:geeksforgeeks.org OR site:developer.mozilla.org",
    "research": "site:ieeexplore.ieee.org OR site:arxiv.org OR site:scholar.google.com OR site:researchgate.net OR site:jstor.org",
    "github": "site:github.com",
    "courses": "site:coursera.org OR site:udemy.com OR site:edx.org OR site:futurelearn.com OR site:khanacademy.org",
    "blogs": "site:medium.com OR site:dev.to OR site:techcrunch.com OR site:towardsdatascience.com OR site:openai.com/blog"
}


def search_google(query, category):
    # Append site filter to query if one exists for the category.
    filter_query = CATEGORY_FILTERS.get(category, "")
    if filter_query:
        query = f"{query} {filter_query}"
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": GOOGLE_API_KEY,
        "cx": CSE_ID,
        "num": 10  # number of results
    }
    response = requests.get(url, params=params)
    data = response.json()
    results = []
    for item in data.get("items", []):
        results.append({
            "title": item.get("title"),
            "url": item.get("link"),
            "description": item.get("snippet")
        })
    return results

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate input
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')
        
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already registered')

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!')
            return redirect(url_for('index'))
        
        return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/')
@login_required
def index():
    query = request.args.get("query", "")
    # Default category set to "tutorials" (adjust as needed)
    category = request.args.get("category", "all").lower()
    results = []
    if query:
        results = search_google(query, category)
    return render_template("index.html", query=query, category=category, results=results)


@app.route('/knowledge-base')
@login_required
def knowledge_base():
    # Get the active tab from the query parameter, default to 'courses'
    active_tab = request.args.get('tab', 'courses')
    
    # Get data from database based on active tab
    categories = {
        "courses": Course.query.all(),
        "handbooks": Handbook.query.all(),
        "github_projects": GitHubProject.query.all(),
        "research_papers": ResearchPaper.query.all(),
        "blogs": Blog.query.all()
    }
    
    # Get bookmarked resource IDs for the current user, filtered by resource type
    bookmarks = Bookmark.query.filter_by(
        user_id=current_user.id,
        resource_type=active_tab
    ).all()
    bookmarked_ids = [bookmark.resource_id for bookmark in bookmarks]
    
    return render_template('knowledge_base.html', 
                         categories=categories, 
                         active_tab=active_tab,
                         bookmarked_ids=bookmarked_ids)

@app.route('/github-trending')
@login_required
def github_trending():
    try:
        response = requests.get('https://api.github.com/search/repositories', 
                               params={'q': 'stars:>1000', 'sort': 'stars', 'order': 'desc'})
        data = response.json()
        
        # Extract relevant information
        repos = []
        for item in data.get('items', [])[:10]:  # Get top 10 repos
            repos.append({
                'name': item['name'],
                'description': item['description'],
                'url': item['html_url'],
                'stars': item['stargazers_count'],
                'owner': item['owner']['login']
            })
        
        return render_template('github_trending.html', repos=repos)
    except Exception as e:
        error_message = str(e)
        return render_template('github_trending.html', error=error_message)

@app.route('/db_view')
@login_required
def db_view():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    # Get all resources
    courses = Course.query.all()
    handbooks = Handbook.query.all()
    github_projects = GitHubProject.query.all()
    research_papers = ResearchPaper.query.all()
    blogs = Blog.query.all()
    users = User.query.all()
    resource_requests = ResourceRequest.query.all()
    bookmarks = Bookmark.query.all()
    
    return render_template('db_view.html',
                         courses=courses,
                         handbooks=handbooks,
                         github_projects=github_projects,
                         research_papers=research_papers,
                         blogs=blogs,
                         users=users,
                         resource_requests=resource_requests,
                         bookmarks=bookmarks)

@app.route('/submit_resource', methods=['GET', 'POST'])
@login_required
def submit_resource():
    if request.method == 'POST':
        title = request.form['title']
        url = request.form['url']
        description = request.form['description']
        resource_type = request.form['resource_type']

        # Create new resource request
        resource_request  = ResourceRequest(
            title=title,
            url=url,
            description=description,
            resource_type=resource_type,
            submitted_by=session['user_id']
        )
        db.session.add(resource_request)
        db.session.commit()

        flash('Resource submitted successfully! Waiting for admin approval.')
        return redirect(url_for('knowledge_base'))

    return render_template('submit_resource.html')

@app.route('/review-requests')
@admin_required
def review_requests():
    requests = ResourceRequest.query.order_by(ResourceRequest.submitted_at.desc()).all()
    return render_template('review_requests.html', requests=requests)

@app.route('/review-request/<int:request_id>', methods=['POST'])
@admin_required
def review_request(request_id):
    resource_request = ResourceRequest.query.get_or_404(request_id)
    action = request.form.get('action')
    review_notes = request.form.get('review_notes')

    if action == 'approve':
        # Create the appropriate resource based on type
        if resource_request.resource_type == 'course':
            resource = Course(
                title=resource_request.title,
                url=resource_request.url,
                description=resource_request.description
            )
        elif resource_request.resource_type == 'handbook':
            resource = Handbook(
                title=resource_request.title,
                url=resource_request.url,
                description=resource_request.description
            )
        elif resource_request.resource_type == 'github_project':
            resource = GitHubProject(
                title=resource_request.title,
                url=resource_request.url,
                description=resource_request.description
            )
        elif resource_request.resource_type == 'research_paper':
            resource = ResearchPaper(
                title=resource_request.title,
                url=resource_request.url,
                description=resource_request.description
            )
        elif resource_request.resource_type == 'blog':
            resource = Blog(
                title=resource_request.title,
                url=resource_request.url,
                description=resource_request.description
            )
        
        db.session.add(resource)
        resource_request.status = 'approved'
        flash('Resource approved and added to knowledge base!')
    
    elif action == 'reject':
        resource_request.status = 'rejected'
        flash('Resource request rejected.')
    
    resource_request.reviewed_by = session['user_id']
    resource_request.reviewed_at = datetime.utcnow()
    resource_request.review_notes = review_notes
    db.session.commit()

    return redirect(url_for('review_requests'))

@app.route('/bookmark/<resource_type>/<int:resource_id>', methods=['POST'])
@login_required
def add_bookmark(resource_type, resource_id):
    try:
        # Check if bookmark already exists
        existing_bookmark = Bookmark.query.filter_by(
            user_id=current_user.id,
            resource_type=resource_type,
            resource_id=resource_id
        ).first()
        
        if existing_bookmark:
            flash('This resource is already bookmarked.', 'error')
            return redirect(request.referrer or url_for('index'))
        
        bookmark = Bookmark(
            user_id=current_user.id,
            resource_type=resource_type,
            resource_id=resource_id
        )
        db.session.add(bookmark)
        db.session.commit()
        flash('Resource bookmarked successfully!', 'success')
        print(f"Added bookmark: type={resource_type}, id={resource_id}")  # Debug log
    except Exception as e:
        db.session.rollback()
        flash('Error bookmarking resource.', 'error')
        print(f"Error adding bookmark: {str(e)}")  # Debug log
    return redirect(request.referrer or url_for('index'))

@app.route('/remove-bookmark/<resource_type>/<int:resource_id>', methods=['POST'])
@login_required
def remove_bookmark(resource_type, resource_id):
    bookmark = Bookmark.query.filter_by(
        user_id=current_user.id,
        resource_type=resource_type,
        resource_id=resource_id
    ).first()
    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
        flash('Bookmark removed successfully!', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/bookmarks')
@login_required
def view_bookmarks():
    # Get all bookmarks for the current user
    bookmarks = Bookmark.query.filter_by(user_id=current_user.id).order_by(Bookmark.created_at.desc()).all()
    print(f"Found {len(bookmarks)} bookmarks for user {current_user.id}")  # Debug log
    
    # Get the actual resources for each bookmark
    resources = []
    for bookmark in bookmarks:
        resource = None
        try:
            if bookmark.resource_type == 'courses':
                resource = Course.query.get(bookmark.resource_id)
            elif bookmark.resource_type == 'handbooks':
                resource = Handbook.query.get(bookmark.resource_id)
            elif bookmark.resource_type == 'github_projects':
                resource = GitHubProject.query.get(bookmark.resource_id)
            elif bookmark.resource_type == 'research_papers':
                resource = ResearchPaper.query.get(bookmark.resource_id)
            elif bookmark.resource_type == 'blogs':
                resource = Blog.query.get(bookmark.resource_id)
            
            if resource:
                resources.append({
                    'type': bookmark.resource_type,
                    'resource': resource,
                    'bookmark_id': bookmark.id,
                    'created_at': bookmark.created_at
                })
                print(f"Added resource: {resource.title} of type {bookmark.resource_type}")  # Debug log
            else:
                print(f"Resource not found for bookmark {bookmark.id} of type {bookmark.resource_type}")  # Debug log
        except Exception as e:
            print(f"Error processing bookmark {bookmark.id}: {str(e)}")  # Debug log
    
    print(f"Total resources to display: {len(resources)}")  # Debug log
    return render_template('bookmarks.html', resources=resources)

if __name__ == '__main__':
    app.run(debug=True)