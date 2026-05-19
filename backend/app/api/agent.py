from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database.base import get_db
from app.database import models
from app.api.dependencies import get_current_user
from app.agents.bio_agent import BioAgent

router = APIRouter()
bio_agent = BioAgent()

@router.post("/chat")
async def chat_with_agent(
    query: str,
    project_id: int = None,
    dataset_id: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    file_path = None
    
    if dataset_id:
        dataset = db.query(models.Dataset).filter(
            models.Dataset.id == dataset_id
        ).join(models.Project).filter(
            models.Project.user_id == current_user.id
        ).first()
        if dataset:
            file_path = dataset.file_path
        else:
            raise HTTPException(status_code=404, detail="Dataset not found")
    
    result = bio_agent.process_query(query, file_path)
    return result

@router.get("/tools")
async def list_available_tools():
    from app.tools.registry import list_tools
    return list_tools()
