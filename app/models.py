from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
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
