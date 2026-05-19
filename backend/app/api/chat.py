from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database.base import get_db
from app.database import models
from app.api.dependencies import get_current_user
from app.agents.llm_provider import LLMProvider
from app.workflows.engine import WorkflowEngine, generate_deg_workflow, generate_sc_workflow

router = APIRouter()
llm_provider = LLMProvider()
workflow_engine = WorkflowEngine()

@router.post("/chat", response_model=Dict[str, Any])
async def chat(
    message: str,
    project_id: int = None,
    dataset_id: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    parsed = llm_provider.parse_user_query(message)
    task_type = parsed.get("task", "unknown")
    
    if task_type == "unknown":
        response = llm_provider.chat_completion([{"role": "user", "content": message}])
        return {
            "type": "chat",
            "response": response,
            "parsed_task": parsed
        }
    
    if not project_id or not dataset_id:
        return {
            "type": "requires_data",
            "message": "请选择项目和数据集进行分析",
            "parsed_task": parsed
        }
    
    dataset = db.query(models.Dataset).filter(
        models.Dataset.id == dataset_id
    ).join(models.Project).filter(
        models.Project.user_id == current_user.id
    ).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if task_type in ["deg_analysis", "bulk_rna_seq"]:
        workflow_json = generate_deg_workflow(dataset.file_path)
        result = workflow_engine.execute_workflow(workflow_json)
        interpretation = llm_provider.interpret_results(result["results"], message)
        
        return {
            "type": "analysis_result",
            "task_type": "deg_analysis",
            "result": result,
            "interpretation": interpretation,
            "parsed_task": parsed
        }
    
    elif task_type == "sc_rna_seq":
        workflow_json = generate_sc_workflow(dataset.file_path)
        result = workflow_engine.execute_workflow(workflow_json)
        interpretation = llm_provider.interpret_results(result["results"], message)
        
        return {
            "type": "analysis_result",
            "task_type": "sc_rna_seq",
            "result": result,
            "interpretation": interpretation,
            "parsed_task": parsed
        }
    
    else:
        response = llm_provider.chat_completion([{"role": "user", "content": message}])
        return {
            "type": "chat",
            "response": response,
            "parsed_task": parsed
        }

@router.post("/interpret", response_model=Dict[str, Any])
async def interpret_results(
    results: Dict[str, Any],
    query: str = "",
    current_user = Depends(get_current_user)
):
    interpretation = llm_provider.interpret_results(results, query)
    
    return {
        "interpretation": interpretation,
        "summary": interpretation.split('\n')[0] if interpretation else ""
    }

@router.post("/report", response_model=Dict[str, Any])
async def generate_report(
    results: Dict[str, Any],
    query: str = "",
    current_user = Depends(get_current_user)
):
    report = llm_provider.generate_report(results, query)
    
    return {
        "report": report,
        "format": "markdown"
    }

@router.get("/tasks", response_model=List[Dict[str, str]])
async def get_available_tasks():
    tasks = [
        {"name": "deg_analysis", "description": "差异表达分析"},
        {"name": "sc_rna_seq", "description": "单细胞RNA-seq分析"},
        {"name": "go_enrichment", "description": "GO富集分析"},
        {"name": "gsea_analysis", "description": "GSEA通路分析"},
        {"name": "visualization", "description": "可视化分析"},
    ]
    return tasks