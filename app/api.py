import requests
import datetime
from app.models import db, GitHubRepo

def fetch_trending_ai_repos():
    # GitHub API endpoints
    url = "https://api.github.com/search/repositories"
    
    # Parameters for AI/ML repositories
    params = {
        "q": "topic:artificial-intelligence OR topic:machine-learning",
        "sort": "stars",
        "order": "desc",
        "per_page": 30
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        repos = response.json()["items"]
        
        for repo in repos:
            # Check if repo already exists
            existing_repo = GitHubRepo.query.filter_by(github_id=repo["id"]).first()
            
            if existing_repo:
                # Update existing repo
                existing_repo.stars = repo["stargazers_count"]
                existing_repo.forks = repo["forks_count"]
                existing_repo.last_updated = datetime.datetime.strptime(
                    repo["updated_at"], "%Y-%m-%dT%H:%M:%SZ"
                )
            else:
                # Create new repo
                new_repo = GitHubRepo(
                    github_id=repo["id"],
                    name=repo["name"],
                    description=repo["description"],
                    url=repo["html_url"],
                    stars=repo["stargazers_count"],
                    forks=repo["forks_count"],
                    language=repo["language"],
                    last_updated=datetime.datetime.strptime(
                        repo["updated_at"], "%Y-%m-%dT%H:%M:%SZ"
                    )
                )
                db.session.add(new_repo)
                
        db.session.commit()
        return True
    else:
        print(f"Error fetching GitHub repos: {response.status_code}")
        return False
