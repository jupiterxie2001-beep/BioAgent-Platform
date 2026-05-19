from typing import Dict, Any
import json

from app.agents.llm_provider import LLMProvider
from app.workflows.engine import WorkflowEngine, generate_deg_workflow
from app.services.data_service import detect_data_type

class BioAgent:
    def __init__(self):
        self.llm_provider = LLMProvider()
        self.workflow_engine = WorkflowEngine()
    
    def process_query(self, query: str, file_path: str = None) -> Dict[str, Any]:
        parsed = self.llm_provider.parse_user_query(query)
        task = parsed.get("task", "unknown")
        
        if task == "deg_analysis" or "差异分析" in query.lower():
            return self._run_deg_analysis(file_path, parsed)
        else:
            return self._handle_generic_query(query, parsed)
    
    def _run_deg_analysis(self, file_path: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        if not file_path:
            return {"error": "No data file provided", "suggestion": "Please upload a gene expression matrix first"}
        
        data_type = detect_data_type(file_path)
        
        if data_type != "bulk_rna":
            return {"error": f"Unsupported data type: {data_type}", "suggestion": "Please upload a bulk RNA-seq expression matrix"}
        
        workflow_json = generate_deg_workflow(file_path, parsed.get("parameters", {}).get("group_info"))
        
        workflow_result = self.workflow_engine.execute_workflow(workflow_json)
        
        interpretation = self.llm_provider.interpret_results(workflow_result["results"], "差异分析")
        
        return {
            "task": "deg_analysis",
            "workflow_result": workflow_result,
            "interpretation": interpretation,
            "data_type": data_type
        }
    
    def _handle_generic_query(self, query: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "task": parsed["task"],
            "reasoning": parsed["reasoning"],
            "message": f"I understand you want to perform {parsed['task']} analysis. However, this feature is still under development. Please try: '帮我做差异分析'"
        }
