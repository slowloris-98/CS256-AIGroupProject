from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

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

@app.route('/')
def index():
    query = request.args.get('query', '')
    category = request.args.get('category', 'all')
    
    results = []
    if query:
        if category == 'all':
            # Search in all categories
            for resource_type in resources.values():
                results.extend([item for item in resource_type 
                              if query.lower() in item['title'].lower() or 
                                 query.lower() in item['description'].lower()])
        else:
            # Search in specific category
            for resource_type, items in resources.items():
                if resource_type == category or any(item['category'] == category for item in items):
                    results.extend([item for item in items 
                                  if query.lower() in item['title'].lower() or 
                                     query.lower() in item['description'].lower()])
    
    return render_template('index.html', results=results, query=query, category=category)


@app.route('/knowledge-base')
def knowledge_base():
    # Get the active tab from the query parameter, default to 'courses'
    active_tab = request.args.get('tab', 'courses')
    
    # Categories for the knowledge base
    categories = {
        "courses": [
            {"title": "Coursera Machine Learning", "url": "#", "platform": "Coursera"},
            {"title": "Fast.ai Deep Learning", "url": "#", "platform": "Fast.ai"},
            {"title": "MIT AI Course", "url": "#", "platform": "MIT OCW"}
        ],
        "handbooks": [
            {"title": "Deep Learning Book", "url": "#", "author": "Ian Goodfellow et al."},
            {"title": "Stanford CS229 Notes", "url": "#", "author": "Stanford University"}
        ],
        "github_projects": [
            {"title": "Transformers", "url": "#", "stars": 50000, "description": "State-of-the-art NLP"},
            {"title": "PyTorch", "url": "#", "stars": 45000, "description": "Deep learning framework"}
        ],
        "research_papers": [
            {"title": "Attention Is All You Need", "url": "#", "source": "arXiv"},
            {"title": "BERT", "url": "#", "source": "Google Research"}
        ],
        "blogs": [
            {"title": "Towards Data Science", "url": "#", "platform": "Medium"},
            {"title": "OpenAI Blog", "url": "#", "platform": "OpenAI"}
        ]
    }
    
    return render_template('knowledge_base.html', categories=categories, active_tab=active_tab)

@app.route('/github-trending')
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



if __name__ == '__main__':
    app.run(debug=True)