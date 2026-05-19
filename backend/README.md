# BioAgent Backend

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL database and update `.env` file

3. Initialize database:
```bash
python -m scripts.init_db
```

4. Run the server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Auth
- POST /auth/token - Login
- POST /auth/register - Register

### Projects
- GET /api/projects - Get user projects
- POST /api/projects - Create project
- DELETE /api/projects/{id} - Delete project

### Files
- POST /api/upload - Upload file
- GET /api/datasets/{project_id} - Get project datasets

### Agent
- POST /api/agent/chat - Chat with AI agent
- GET /api/agent/tools - List available tools
