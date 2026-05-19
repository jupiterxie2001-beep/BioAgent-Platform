from typing import Dict, Any, List
import json

from app.tools.registry import get_tool

class WorkflowEngine:
    def __init__(self):
        self.tools = {}
    
    def execute_workflow(self, workflow_json: str) -> Dict[str, Any]:
        workflow = json.loads(workflow_json)
        results = {}
        context = {}
        
        for step in workflow.get("steps", []):
            tool_name = step.get("tool")
            params = step.get("params", {})
            
            params.update(context)
            
            tool = get_tool(tool_name)
            result = tool.run(params)
            
            results[tool_name] = result
            context.update(result)
        
        return {
            "workflow_name": workflow.get("workflow_name"),
            "results": results,
            "summary": self._generate_summary(results)
        }
    
    def _generate_summary(self, results: Dict[str, Any]) -> str:
        summary_parts = []
        
        if "deseq2_analysis" in results:
            deg_result = results["deseq2_analysis"]
            summary_parts.append(f"差异分析完成，共识别到 {deg_result['n_significant']} 个显著差异基因。")
        
        if "plot_volcano" in results:
            volcano_result = results["plot_volcano"]
            summary_parts.append(f"火山图已生成，上调基因 {volcano_result['n_upregulated']} 个，下调基因 {volcano_result['n_downregulated']} 个。")
        
        if "run_go_enrichment" in results:
            go_result = results["run_go_enrichment"]
            summary_parts.append(f"GO富集分析完成，发现 {go_result['n_significant_terms']} 个显著富集的生物过程。")
        
        if "run_gsea" in results:
            gsea_result = results["run_gsea"]
            summary_parts.append(f"GSEA分析完成，发现 {gsea_result['n_significant']} 个显著富集的通路。")
        
        return " ".join(summary_parts)

def generate_deg_workflow(file_path: str, group_info: Dict[str, str] = None) -> str:
    workflow = {
        "workflow_name": "bulk_deg_analysis",
        "steps": [
            {
                "tool": "deseq2_analysis",
                "params": {
                    "file_path": file_path,
                    "group_info": group_info
                }
            },
            {
                "tool": "plot_volcano",
                "params": {}
            },
            {
                "tool": "plot_heatmap",
                "params": {
                    "expression_file": file_path
                }
            },
            {
                "tool": "run_go_enrichment",
                "params": {}
            },
            {
                "tool": "run_gsea",
                "params": {}
            }
        ]
    }
    return json.dumps(workflow)

def generate_sc_workflow(file_path: str, params: Dict[str, Any] = None) -> str:
    workflow = {
        "workflow_name": "single_cell_analysis",
        "steps": [
            {
                "tool": "scanpy_pipeline",
                "params": {
                    "file_path": file_path,
                    **(params or {})
                }
            },
            {
                "tool": "cell_type_annotation",
                "params": {}
            },
            {
                "tool": "plot_umap",
                "params": {}
            },
            {
                "tool": "plot_marker_genes",
                "params": {}
            },
            {
                "tool": "plot_qc",
                "params": {}
            }
        ]
    }
    return json.dumps(workflow)
