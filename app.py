from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import requests
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key-for-now'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ailearninghub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['GITHUB_TOKEN'] = os.environ.get('GITHUB_TOKEN')
app.config['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY')

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    bookmarks = db.relationship('Bookmark', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)  # Tutorial, Course, Paper, GitHub, Blog
    category = db.Column(db.String(50))  # ML, NLP, CV, RL, etc.
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False)
    user_submitted = db.Column(db.Boolean, default=False)
    submitter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    submitter = db.relationship('User')
    bookmarks = db.relationship('Bookmark', backref='resource', lazy='dynamic')

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'), nullable=False)
    date_bookmarked = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)  # User's personal notes about the resource

class GitHubRepo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    github_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500), nullable=False)
    stars = db.Column(db.Integer, default=0)
    forks = db.Column(db.Integer, default=0)
    language = db.Column(db.String(50))
    last_updated = db.Column(db.DateTime)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    # For simplicity, just display a message for now
    return render_template('index.html')

@app.route('/search')
def search():
    # Placeholder function for now
    return render_template('search_results.html')

@app.route('/categories')
def categories():
    # Placeholder function for now
    return "Categories page"

@app.route('/github_explorer')
def github_explorer():
    # Placeholder function for now
    return render_template('github_explorer.html')

@app.route('/chatbot')
def chatbot():
    # Placeholder function for now
    return "Chatbot page"

@app.route('/login')
def login():
    # Placeholder function for now
    return "Login page"

@app.route('/register')
def register():
    # Placeholder function for now
    return "Register page"

@app.route('/dashboard')
def dashboard():
    # Placeholder function for now
    return "Dashboard page"

@app.route('/logout')
def logout():
    # Placeholder function for now
    return "Logout page"

@app.route('/submit_resource')
def submit_resource():
    # Placeholder function for now
    return "Submit resource page"

@app.route('/pending_resources')
def pending_resources():
    # Placeholder function for now
    return "Pending resources page"

# Create database tables
with app.app_context():
    db.create_all()

# If this file is run directly, start the development server
if __name__ == '__main__':
    app.run(debug=True)
