from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import os
import shutil
import json

from app.database.base import get_db
from app.database import models
from app.api.dependencies import get_current_user
from app.core.config import settings
from app.services.data_service import detect_data_type

router = APIRouter()

@router.post("/upload")
async def upload_file(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    storage_path = os.path.join(settings.storage_path, str(current_user.id), str(project_id))
    os.makedirs(storage_path, exist_ok=True)
    
    file_path = os.path.join(storage_path, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    data_type = detect_data_type(file_path)
    
    dataset = models.Dataset(
        project_id=project_id,
        dataset_type=data_type,
        file_path=file_path,
        dataset_metadata=json.dumps({"filename": file.filename})
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    
    return {
        "id": dataset.id,
        "dataset_type": dataset.dataset_type,
        "file_path": dataset.file_path,
        "created_at": dataset.created_at
    }

@router.get("/datasets/{project_id}", response_model=list[dict])
async def get_datasets(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    datasets = db.query(models.Dataset).filter(
        models.Dataset.project_id == project_id
    ).join(models.Project).filter(
        models.Project.user_id == current_user.id
    ).all()
    return [
        {
            "id": d.id,
            "dataset_type": d.dataset_type,
            "file_path": d.file_path,
            "metadata": json.loads(d.dataset_metadata) if d.dataset_metadata else {},
            "created_at": d.created_at
        }
        for d in datasets
    ]
