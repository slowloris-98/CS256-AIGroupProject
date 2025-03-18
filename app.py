from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
import os
from models import db, Course, Handbook, GitHubProject, ResearchPaper, Blog, User
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "YOUR_GOOGLE_API_KEY")
CSE_ID = os.environ.get("CSE_ID", "YOUR_CSE_ID")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///knowledge_base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # Required for session management

# Initialize the database
db.init_app(app)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Create database tables
with app.app_context():
    db.create_all()
    # Add some sample data if the database is empty
    if not Course.query.first():
        sample_courses = [
            Course(title="Coursera Machine Learning", url="#", platform="Coursera", description="Stanford's Machine Learning course"),
            Course(title="Fast.ai Deep Learning", url="#", platform="Fast.ai", description="Practical deep learning course"),
            Course(title="MIT AI Course", url="#", platform="MIT OCW", description="MIT's Introduction to AI")
        ]
        db.session.add_all(sample_courses)
        db.session.commit()

    if not Handbook.query.first():
        sample_handbooks = [
            Handbook(title="Deep Learning Book", url="#", author="Ian Goodfellow et al.", description="Comprehensive guide to deep learning"),
            Handbook(title="Stanford CS229 Notes", url="#", author="Stanford University", description="Machine learning course notes")
        ]
        db.session.add_all(sample_handbooks)
        db.session.commit()

    if not GitHubProject.query.first():
        sample_projects = [
            GitHubProject(title="Transformers", url="#", stars=50000, description="State-of-the-art NLP"),
            GitHubProject(title="PyTorch", url="#", stars=45000, description="Deep learning framework")
        ]
        db.session.add_all(sample_projects)
        db.session.commit()

    if not ResearchPaper.query.first():
        sample_papers = [
            ResearchPaper(title="Attention Is All You Need", url="#", source="arXiv", description="Transformer architecture paper"),
            ResearchPaper(title="BERT", url="#", source="Google Research", description="Bidirectional Encoder Representations from Transformers")
        ]
        db.session.add_all(sample_papers)
        db.session.commit()

    if not Blog.query.first():
        sample_blogs = [
            Blog(title="Towards Data Science", url="#", platform="Medium", description="Data science articles and tutorials"),
            Blog(title="OpenAI Blog", url="#", platform="OpenAI", description="Latest AI research and developments")
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
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!')
            return redirect(url_for('index'))
        
        return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
def logout():
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
    
    return render_template('knowledge_base.html', categories=categories, active_tab=active_tab)

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

@app.route('/db-view')
@login_required
def db_view():
    return render_template('db_view.html',
                         courses=Course.query.all(),
                         handbooks=Handbook.query.all(),
                         github_projects=GitHubProject.query.all(),
                         research_papers=ResearchPaper.query.all(),
                         blogs=Blog.query.all())

if __name__ == '__main__':
    app.run(debug=True)