from flask import request, render_template, jsonify
from app.models import db, Resource, GitHubRepo, Bookmark
from sqlalchemy import or_
from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from app.chatbot import chatbot_service
from app import app
#chatbot_instance = Chatbot()  # Initialize the chatbot instance


@app.route('/')
def index():
    return render_template('base-template.html')


@app.route('/search')
def search():
    query = request.args.get('q', '')
    resource_type = request.args.get('type', '')
    category = request.args.get('category', '')
    
    # Base query
    results = Resource.query.filter(
        Resource.approved == True,
        or_(
            Resource.title.ilike(f'%{query}%'),
            Resource.description.ilike(f'%{query}%')
        )
    )
    
    # Apply filters
    if resource_type:
        results = results.filter(Resource.resource_type == resource_type)
    if category:
        results = results.filter(Resource.category == category)
        
    # Get GitHub results if requested
    github_results = []
    if not resource_type or resource_type == 'GitHub':
        github_results = GitHubRepo.query.filter(
            or_(
                GitHubRepo.name.ilike(f'%{query}%'),
                GitHubRepo.description.ilike(f'%{query}%')
            )
        ).all()
    
    return render_template('search_results.html', 
                          resources=results.all(),
                          github_repos=github_results,
                          query=query)

@app.route('/github-explorer')
def github_explorer():
    # Optionally refresh repos first (can also be done via scheduled task)
    # fetch_trending_ai_repos()
    
    repos = GitHubRepo.query.order_by(GitHubRepo.stars.desc()).limit(50).all()
    return render_template('github_explorer.html', repos=repos)


@app.route('/bookmark/<int:resource_id>', methods=['POST'])
@login_required
def bookmark_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    
    # Check if already bookmarked
    existing_bookmark = Bookmark.query.filter_by(
        user_id=current_user.id,
        resource_id=resource_id
    ).first()
    
    if existing_bookmark:
        flash('This resource is already in your bookmarks.')
        return redirect(url_for('resource_detail', id=resource_id))
    
    bookmark = Bookmark(user_id=current_user.id, resource_id=resource_id)
    db.session.add(bookmark)
    db.session.commit()
    
    flash('Resource bookmarked successfully!')
    return redirect(url_for('resource_detail', id=resource_id))

@app.route('/dashboard')
@login_required
def dashboard():
    user_bookmarks = Bookmark.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', bookmarks=user_bookmarks)

'''
@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        message = request.form['message']
        response = chatbot_instance.chatbot_response(message)
        return jsonify({'response': response})
    return render_template('chatbot.html')'
'''

@app.route('/submit-resource', methods=['GET', 'POST'])
@login_required
def submit_resource():
    if request.method == 'POST':
        # Extract form data
        title = request.form['title']
        description = request.form['description']
        url = request.form['url']
        resource_type = request.form['resource_type']
        category = request.form['category']
        
        # Create new resource (pending approval)
        new_resource = Resource(
            title=title,
            description=description,
            url=url,
            resource_type=resource_type,
            category=category,
            approved=False,
            user_submitted=True,
            submitter_id=current_user.id
        )
        
        db.session.add(new_resource)
        db.session.commit()
        
        flash('Resource submitted successfully! It will be reviewed by an admin.')
        return redirect(url_for('dashboard'))
        
    return render_template('submit_resource.html')

@app.route('/admin/pending-resources')
@login_required
def pending_resources():
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))
        
    pending = Resource.query.filter_by(approved=False).all()
    return render_template('admin/pending_resources.html', resources=pending)

@app.route('/admin/approve-resource/<int:id>', methods=['POST'])
@login_required
def approve_resource(id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.')
        return redirect(url_for('index'))
        
    resource = Resource.query.get_or_404(id)
    resource.approved = True
    db.session.commit()
    
    flash('Resource approved successfully!')
    return redirect(url_for('pending_resources'))



@app.before_request
def before_request():
    """Initialize Gemini API before handling requests"""
    if request.endpoint == 'chatbot' and request.method == 'POST':
        if not chatbot_service.conversation:
            chatbot_service.initialize_api()

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    """Chatbot interface and API endpoint"""
    if request.method == 'POST':
        if request.is_json:
            # Handle API request (from AJAX)
            data = request.get_json()
            message = data.get('message', '')
            response = chatbot_service.get_response(message)
            return jsonify({'response': response})
        else:
            # Handle form submission
            message = request.form.get('message', '')
            response = chatbot_service.get_response(message)
            return jsonify({'response': response})
    
    # GET request displays the chatbot interface
    return render_template('chatbot.html')

@app.route('/chatbot/clear', methods=['POST'])
def clear_chat_history():
    """Clear the chatbot conversation history"""
    chatbot_service.clear_history()
    return jsonify({'status': 'success', 'message': 'Conversation history cleared'})
