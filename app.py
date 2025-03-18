from flask import Flask, render_template, request, redirect, url_for
import requests
import os

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "YOUR_GOOGLE_API_KEY")
CSE_ID = os.environ.get("CSE_ID", "YOUR_CSE_ID")

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

@app.route('/')
def index():
    query = request.args.get("query", "")
    # Default category set to "tutorials" (adjust as needed)
    category = request.args.get("category", "all").lower()
    results = []
    if query:
        results = search_google(query, category)
    return render_template("index.html", query=query, category=category, results=results)


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