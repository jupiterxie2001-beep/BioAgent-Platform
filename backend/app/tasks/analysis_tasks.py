from celery import shared_task
from app.workflows.engine import WorkflowEngine, generate_deg_workflow
from app.agents.llm_provider import LLMProvider
from app.database.base import SessionLocal
from app.database import models
from datetime import datetime
import json

workflow_engine = WorkflowEngine()
llm_provider = LLMProvider()

@shared_task(bind=True, track_started=True)
def run_deg_analysis(self, file_path: str, task_id: int, group_info: dict = None):
    db = SessionLocal()
    
    try:
        job = db.query(models.AnalysisJob).filter(models.AnalysisJob.id == task_id).first()
        if job:
            job.status = "running"
            job.updated_at = datetime.utcnow()
            db.commit()
        
        self.update_state(state='PROGRESS', meta={'status': 'Starting DEG analysis...', 'progress': 10})
        
        workflow_json = generate_deg_workflow(file_path, group_info)
        
        self.update_state(state='PROGRESS', meta={'status': 'Running DESeq2 analysis...', 'progress': 25})
        
        workflow_result = workflow_engine.execute_workflow(workflow_json)
        
        self.update_state(state='PROGRESS', meta={'status': 'Generating visualizations...', 'progress': 50})
        
        self.update_state(state='PROGRESS', meta={'status': 'Running enrichment analysis...', 'progress': 75})
        
        self.update_state(state='PROGRESS', meta={'status': 'Interpreting results...', 'progress': 90})
        
        interpretation = llm_provider.interpret_results(workflow_result["results"], "差异分析")
        
        result_data = {
            "workflow_result": workflow_result,
            "interpretation": interpretation,
            "data_type": "bulk_rna"
        }
        
        result_path = file_path.replace('.csv', '_results.json').replace('.tsv', '_results.json')
        with open(result_path, 'w') as f:
            json.dump(result_data, f)
        
        if job:
            job.status = "completed"
            job.result_path = result_path
            job.updated_at = datetime.utcnow()
            db.commit()
        
        self.update_state(state='PROGRESS', meta={'status': 'Analysis complete', 'progress': 100})
        
        return {
            'status': 'completed',
            'result_path': result_path,
            'interpretation': interpretation,
            'summary': workflow_result['summary']
        }
    
    except Exception as e:
        if job:
            job.status = "failed"
            job.updated_at = datetime.utcnow()
            db.commit()
        
        self.update_state(state='FAILURE', meta={'status': str(e)})
        raise
    
    finally:
        db.close()

@shared_task(bind=True, track_started=True)
def run_gsea_analysis(self, deg_file: str, task_id: int):
    from app.tools.enrichment import GSEATool
    from app.tools.visualization import HeatmapTool
    
    db = SessionLocal()
    
    try:
        job = db.query(models.AnalysisJob).filter(models.AnalysisJob.id == task_id).first()
        if job:
            job.status = "running"
            job.updated_at = datetime.utcnow()
            db.commit()
        
        self.update_state(state='PROGRESS', meta={'status': 'Starting GSEA analysis...', 'progress': 10})
        
        gsea_tool = GSEATool()
        result = gsea_tool.run({"deg_file": deg_file})
        
        self.update_state(state='PROGRESS', meta={'status': 'GSEA analysis complete', 'progress': 100})
        
        if job:
            job.status = "completed"
            job.result_path = result['result_path']
            job.updated_at = datetime.utcnow()
            db.commit()
        
        return result
    
    except Exception as e:
        if job:
            job.status = "failed"
            job.updated_at = datetime.utcnow()
            db.commit()
        
        self.update_state(state='FAILURE', meta={'status': str(e)})
        raise
    
    finally:
        db.close()

@shared_task(bind=True, track_started=True)
def run_sc_analysis(self, file_path: str, task_id: int, params: dict = None):
    from app.tools.sc_analysis import ScanpyPipelineTool, CellTypeAnnotationTool
    from app.tools.sc_visualization import UMAPPlotTool, MarkerGenePlotTool, QCPlotTool
    
    db = SessionLocal()
    
    try:
        job = db.query(models.AnalysisJob).filter(models.AnalysisJob.id == task_id).first()
        if job:
            job.status = "running"
            job.updated_at = datetime.utcnow()
            db.commit()
        
        self.update_state(state='PROGRESS', meta={'status': 'Starting single-cell analysis...', 'progress': 5})
        
        scanpy_tool = ScanpyPipelineTool()
        pipeline_result = scanpy_tool.run({"file_path": file_path, **(params or {})})
        
        self.update_state(state='PROGRESS', meta={'status': 'Cell clustering complete...', 'progress': 30})
        
        annotation_tool = CellTypeAnnotationTool()
        annotation_result = annotation_tool.run({
            "cluster_info_path": pipeline_result['cluster_info_path']
        })
        
        self.update_state(state='PROGRESS', meta={'status': 'Cell type annotation complete...', 'progress': 50})
        
        umap_tool = UMAPPlotTool()
        umap_result = umap_tool.run({
            "h5ad_file": pipeline_result['result_path'],
            "annotation_file": annotation_result['annotation_path']
        })
        
        self.update_state(state='PROGRESS', meta={'status': 'Generating UMAP visualization...', 'progress': 70})
        
        marker_tool = MarkerGenePlotTool()
        marker_result = marker_tool.run({
            "h5ad_file": pipeline_result['result_path'],
            "cluster_info_path": pipeline_result['cluster_info_path']
        })
        
        self.update_state(state='PROGRESS', meta={'status': 'Generating marker gene plots...', 'progress': 85})
        
        qc_tool = QCPlotTool()
        qc_result = qc_tool.run({
            "h5ad_file": pipeline_result['result_path']
        })
        
        self.update_state(state='PROGRESS', meta={'status': 'Generating QC plots...', 'progress': 95})
        
        all_results = {
            "pipeline": pipeline_result,
            "annotation": annotation_result,
            "umap": umap_result,
            "markers": marker_result,
            "qc": qc_result
        }
        
        result_path = file_path.replace('.h5ad', '_results.json').replace('.mtx', '_results.json')
        with open(result_path, 'w') as f:
            json.dump(all_results, f)
        
        if job:
            job.status = "completed"
            job.result_path = result_path
            job.updated_at = datetime.utcnow()
            db.commit()
        
        self.update_state(state='PROGRESS', meta={'status': 'Analysis complete', 'progress': 100})
        
        return {
            'status': 'completed',
            'result_path': result_path,
            'summary': pipeline_result['summary'],
            'annotation_summary': annotation_result['summary'],
            'n_clusters': pipeline_result['n_clusters'],
            'n_cells': pipeline_result['n_cells']
        }
    
    except Exception as e:
        if job:
            job.status = "failed"
            job.updated_at = datetime.utcnow()
            db.commit()
        
        self.update_state(state='FAILURE', meta={'status': str(e)})
        raise
    
    finally:
        db.close()
