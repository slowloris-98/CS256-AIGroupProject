# AI Knowledge Hub

A comprehensive web application for discovering, managing, and sharing AI learning resources. This platform helps users find curated content across various categories including courses, handbooks, GitHub projects, research papers, and blogs.

## System Design Document

### Overview

This document outlines the architecture and technology stack used in the project. The system is designed to provide a web-based application with a modern, responsive frontend, a robust backend using Python and Flask, and a persistent storage solution managed through SQLAlchemy with SQLite3. Continuous integration and deployment are facilitated through Render, while Git and GitHub manage source control and repository hosting.

---

## System Architecture

### Frontend
- **Technologies**: HTML, CSS, JavaScript, Tailwind CSS
- **Role**:
  - Provides the user interface and interactive client-side experience.
  - Tailwind CSS is utilized to build responsive and modern designs quickly.
  - JavaScript enhances interactivity and dynamic content rendering.

### Backend
- **Technologies**: Python, Flask
- **Role**:
  - Serves as the core application server.
  - Handles HTTP requests, processes business logic, and manages API endpoints.
  - Implements server-side functionalities like authentication, routing, and data processing.

### Database
- **Technologies**: SQLAlchemy (ORM), SQLite3
- **Role**:
  - SQLAlchemy abstracts the database operations, enabling easier manipulation of data objects.
  - SQLite3 is used as the underlying relational database to persist application data.
  - The database schema includes multiple entities (e.g., User, Course, Handbook, GitHubProject, ResearchPaper, Blog, ResourceRequest, Bookmark) with defined relationships.

#### Database Schema Diagram:
![Database Schema](https://cdn.mathpix.com/cropped/2025_03_22_2d6dabf782b5f1daa283g-2.jpg?height=1121&width=1186&top_left_y=339&top_left_x=298)

### Continuous Integration and Deployment (CI/CD)
- **Technology**: Render
- **Role**:
  - Automates the build, testing, and deployment processes.
  - Ensures that every code change is integrated, tested, and deployed seamlessly.

### Source Control and Repository
- **Technologies**: Git, GitHub  
- **Repository URL**: [CS256-AIGroupProject](https://github.com/slowloris-98/CS256-AIGroupProject)

---

## Features

### Resource Categories
- **Courses**: Online courses from platforms like Coursera, Fast.ai, and MIT OCW.
- **Handbooks**: Comprehensive learning materials and textbooks.
- **GitHub Projects**: Trending and popular AI/ML repositories.
- **Research Papers**: Academic papers and publications.
- **Blogs**: Technical blogs and articles from leading platforms.

### User Features
1. **Account Management**: Register and login to access personalized features.
2. **Resource Search**: Advanced search functionality across different categories.
3. **Bookmarking**: Save and organize favorite resources.
4. **Resource Submission**: Submit new resources for admin review.
5. **AI Chat Assistant**: Get help and recommendations through the chat interface.

### Admin Features
1. **Resource Management**: Review and manage submitted resources.
2. **User Management**: Oversee user accounts and permissions.
3. **Database View**: Access comprehensive database information.

---

## Getting Started

### Prerequisites
1. Python 3.x
2. Flask
3. SQLite
4. Required API Keys:
   - Google API Key
   - Google Custom Search Engine ID
   - Gemini API Key

### Installation

1. Clone the repository:
    ```
    git clone https://github.com/slowloris-98/CS256-AIGroupProject.git
    cd CS256-AIGroupProject
    ```

2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

3. Set up environment variables in a `.env` file:
    ```
    GOOGLE_API_KEY=your_google_api_key
    CSE_ID=your_custom_search_engine_id
    GEMINI_API_KEY=your_gemini_api_key
    SECRET_KEY=your_secret_key
    ```

4. Initialize the database:
    ```
    flask run
    ```

---

## User Guide

### Application URL  
[AI Knowledge Hub](https://example.com)

### Registration and Login  
1. Navigate to `/register` to create a new account.
2. Provide username, email, and password.
3. Login at `/login` with your credentials.

![Registration](https://cdn.mathpix.com/cropped/2025_03_22_0d44b1d86160ffb8cf83g-03.jpg?height=1454&width=1646&top_left_y=712&top_left_x=235)

### Using the Knowledge Base  
1. Access the knowledge base through the main navigation.
2. Browse different categories using tabs such as Courses, Handbooks, GitHub Projects, Research Papers, Blogs.
3. Use filters or search to find specific resources.

![Knowledge Base](https://cdn.mathpix.com/cropped/2025_03_22_0d44b1d86160ffb8cf83g-04.jpg?height=717&width=1642&top_left_y=539&top_left_x=233)

### Bookmarking System  
1. Click the bookmark icon on any resource to save it.
2. Access bookmarks through "My Bookmarks."
3. Remove bookmarks with a single click.

![Bookmarks](https://cdn.mathpix.com/cropped/2025_03_22_0d44b1d86160ffb8cf83g-05.jpg?height=720&width=1630&top_left_y=540&top_left_x=231)

---

## Admin Guide

### Admin Access  
Login with admin credentials to access admin-specific features through the dashboard.

![Admin Dashboard](https://cdn.mathpix.com/cropped/2025_03_22_0d44b1d86160ffb8cf83g-07.jpg?height=722&width=1639&top_left_y=555&top_left_x=235)

### Resource Management  
Review submitted resources at `/review-requests`. Approve or reject submissions after reviewing details.

![Resource Management](https://cdn.mathpix.com/cropped/2025_03_22_0d44b1d86160ffb8cf83g-07.jpg?height=725&width=1649&top_left_y=1714&top_left_x=235)

---

## API Keys Setup

### Google API Key  
1. Visit Google Cloud Console.
2. Create a new project.
3. Enable Custom Search API.
4. Generate API key and add it to `.env`.

### Custom Search Engine ID  
1. Visit Google Programmable Search Engine.
2. Create a new search engine.
3. Get the Search Engine ID and add it to `.env`.

---

## Technical Requirements

### Minimum System Requirements  
1. Python 3.x  
2. 512MB RAM  
3. 1GB storage space  
4. Internet connection for API access  

### Supported Browsers  
Chrome (recommended), Firefox, Safari, Edge  

---

## Security Notes

1. Keep API keys secure; never commit them to version control.
2. Regularly update admin passwords.
3. Use strong passwords for all accounts.

---

## Support  

For additional support or questions:
1. Submit an issue on [GitHub Repository](https://github.com/slowloris-98/CS256-AIGroupProject).
2. Contact the system administrator.

