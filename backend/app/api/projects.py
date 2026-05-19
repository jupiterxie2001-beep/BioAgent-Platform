from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.base import get_db
from app.database import models
from app.api.dependencies import get_current_user

router = APIRouter()

@router.get("/projects", response_model=List[dict])
async def get_projects(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    projects = db.query(models.Project).filter(models.Project.user_id == current_user.id).all()
    return [
        {
            "id": p.id,
            "project_name": p.project_name,
            "description": p.description,
            "created_at": p.created_at
        }
        for p in projects
    ]

@router.post("/projects", response_model=dict)
async def create_project(
    project_name: str,
    description: str = "",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    project = models.Project(
        user_id=current_user.id,
        project_name=project_name,
        description=description
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return {
        "id": project.id,
        "project_name": project.project_name,
        "description": project.description,
        "created_at": project.created_at
    }

@router.delete("/projects/{project_id}", response_model=dict)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}
