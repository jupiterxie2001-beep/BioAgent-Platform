from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from celery.result import AsyncResult
from datetime import datetime

from app.database.base import get_db
from app.database import models
from app.api.dependencies import get_current_user
from app.core.celery_config import celery
from app.tasks.analysis_tasks import run_deg_analysis, run_gsea_analysis, run_sc_analysis

router = APIRouter()

@router.post("/tasks/dega", response_model=dict)
async def create_deg_task(
    project_id: int,
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    dataset = db.query(models.Dataset).filter(
        models.Dataset.id == dataset_id
    ).join(models.Project).filter(
        models.Project.user_id == current_user.id
    ).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    workflow_json = {
        "workflow_name": "bulk_deg_analysis",
        "steps": [
            {"tool": "deseq2_analysis", "params": {"file_path": dataset.file_path}}
        ]
    }
    
    job = models.AnalysisJob(
        project_id=project_id,
        workflow_json=str(workflow_json),
        status="pending"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    task = run_deg_analysis.apply_async(
        args=[dataset.file_path, job.id],
        task_id=f"deg_analysis_{job.id}"
    )
    
    return {
        "task_id": task.task_id,
        "job_id": job.id,
        "status": "pending",
        "message": "DEG analysis task submitted successfully"
    }

@router.get("/tasks/{task_id}", response_model=dict)
async def get_task_status(task_id: str):
    result = AsyncResult(task_id, app=celery)
    
    if result.state == 'PENDING':
        return {"task_id": task_id, "status": "pending", "progress": 0}
    
    elif result.state == 'PROGRESS':
        meta = result.info or {}
        return {
            "task_id": task_id,
            "status": "running",
            "progress": meta.get('progress', 0),
            "message": meta.get('status', '')
        }
    
    elif result.state == 'SUCCESS':
        return {
            "task_id": task_id,
            "status": "completed",
            "progress": 100,
            "result": result.info
        }
    
    elif result.state == 'FAILURE':
        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(result.info)
        }
    
    else:
        return {"task_id": task_id, "status": result.state}

@router.get("/jobs/{project_id}", response_model=list)
async def get_project_jobs(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    jobs = db.query(models.AnalysisJob).filter(
        models.AnalysisJob.project_id == project_id
    ).join(models.Project).filter(
        models.Project.user_id == current_user.id
    ).order_by(models.AnalysisJob.created_at.desc()).all()
    
    return [
        {
            "id": job.id,
            "status": job.status,
            "result_path": job.result_path,
            "created_at": job.created_at,
            "updated_at": job.updated_at
        }
        for job in jobs
    ]

@router.delete("/tasks/{task_id}", response_model=dict)
async def revoke_task(task_id: str):
    celery.control.revoke(task_id, terminate=True)
    return {"message": "Task revoked successfully"}

@router.post("/tasks/sca", response_model=dict)
async def create_sc_task(
    project_id: int,
    dataset_id: int,
    params: dict = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    dataset = db.query(models.Dataset).filter(
        models.Dataset.id == dataset_id
    ).join(models.Project).filter(
        models.Project.user_id == current_user.id
    ).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    job = models.AnalysisJob(
        project_id=project_id,
        workflow_json=str({"workflow_name": "single_cell_analysis"}),
        status="pending"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    task = run_sc_analysis.apply_async(
        args=[dataset.file_path, job.id, params or {}],
        task_id=f"sc_analysis_{job.id}"
    )
    
    return {
        "task_id": task.task_id,
        "job_id": job.id,
        "status": "pending",
        "message": "Single-cell analysis task submitted successfully"
    }
