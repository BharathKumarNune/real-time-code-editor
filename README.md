# Real-time Code Editor with AI-assisted Debugging

## Overview
This is a real-time collaborative code editor that allows multiple users to edit and debug code together. It includes AI-assisted debugging using OpenAI, role-based access control (RBAC), authentication with JWT tokens, and real-time conflict resolution via WebSockets.

## Features
- **User Authentication** (Signup, Login, JWT-based authentication)
- **Role-Based Access Control** (Owner, Collaborator, Viewer)
- **AI-powered Code Debugging** (via OpenAI API)
- **Real-time Collaborative Editing** (via Socket.IO)
- **Rate Limiting & Security Measures**
- **Database Persistence with SQLAlchemy**
- **Dockerized for Easy Deployment**

## Project Structure
```
/real-time-code-editor  
│── /app  
│   │── __init__.py  
│   │── main.py          # FastAPI entry point  
│   │── auth.py          # Authentication & authorization (JWT, RBAC)  
│   │── db.py            # Database models & session (SQLAlchemy)  
│   │── sockets.py       # Socket.IO event handling  
│   │── ai.py            # AI debugging (OpenAI Codex)  
│   │── editor.py        # Code editor logic & API routes  
│   │── config.py        # Configuration settings (environment variables)  
│── /tests               # Unit & integration tests   
│── .env.example         # Environment variables template  
│── requirements.txt     # Python dependencies  
│── README.md            # Project documentation  
│── .gitignore           # Ignore unnecessary files   
│── postman_collection.json # API testing collection  
```

## Setup Instructions
### Prerequisites
- Python 3.8+

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/BharathKumarNune/real-time-code-editor.git
cd real-time-code-editor
```

### 2️⃣ Set Up Environment Variables
Copy `.env.example` to `.env` and update values:
```bash
cp .env.example .env
```
Edit `.env` with your preferred values:
```
DATABASE_URL="sqlite+aiosqlite:///./yourbatabasename.db"
SECRET_KEY=your_secret_key
ALGORITHM=HS256
OPENAI_API_KEY=your_openai_key
```

### 3️⃣ Install Dependencies
Using pip:
```bash
pip install -r requirements.txt
```

### 4️⃣ Run Database Migrations
```bash
alembic upgrade head
```

### 5️⃣ Start the Application
Using FastAPI directly:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
## API Documentation
Once the server is running, access:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc UI:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Raw OpenAPI JSON:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## Postman Collection
To test the API, import `postman_collection.json` into Postman.

## WebSockets (Real-time Editing)
### Events
- `connect`: User joins session
- `disconnect`: User leaves session
- `edit_code`: Broadcasts real-time code changes
- `request_suggestion`: Requests AI debugging assistance
- `apply_suggestion`: Accepts or rejects AI suggestions

## Running Tests
To run unit tests:
```bash
pytest tests/
```

## Contributors
- **Your Name** - Bharath Kumar Nune
