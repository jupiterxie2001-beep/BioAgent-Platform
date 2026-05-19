from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.files import router as files_router
from app.api.agent import router as agent_router
from app.api.tasks import router as tasks_router
from app.api.chat import router as chat_router

app = FastAPI(title="BioAgent Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(projects_router, prefix="/api", tags=["projects"])
app.include_router(files_router, prefix="/api", tags=["files"])
app.include_router(agent_router, prefix="/api/agent", tags=["agent"])
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Welcome to BioAgent Platform API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
