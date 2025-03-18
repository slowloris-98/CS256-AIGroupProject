import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-now'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    # Add Gemini API key configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
