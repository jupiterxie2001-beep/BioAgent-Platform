from typing import Dict, Type
from app.tools.base import BaseTool
from app.tools.deg_analysis import DESeq2Tool
from app.tools.visualization import VolcanoPlotTool, HeatmapTool
from app.tools.enrichment import GSEATool, GOEnrichmentTool
from app.tools.sc_analysis import ScanpyPipelineTool, CellTypeAnnotationTool
from app.tools.sc_visualization import UMAPPlotTool, MarkerGenePlotTool, QCPlotTool

TOOLS: Dict[str, Type[BaseTool]] = {
    "deseq2_analysis": DESeq2Tool,
    "plot_volcano": VolcanoPlotTool,
    "plot_heatmap": HeatmapTool,
    "run_gsea": GSEATool,
    "run_go_enrichment": GOEnrichmentTool,
    "scanpy_pipeline": ScanpyPipelineTool,
    "cell_type_annotation": CellTypeAnnotationTool,
    "plot_umap": UMAPPlotTool,
    "plot_marker_genes": MarkerGenePlotTool,
    "plot_qc": QCPlotTool,
}

def get_tool(tool_name: str) -> BaseTool:
    tool_class = TOOLS.get(tool_name)
    if not tool_class:
        raise ValueError(f"Tool {tool_name} not found")
    return tool_class()

def list_tools() -> Dict[str, str]:
    return {name: tool.description for name, tool in TOOLS.items()}
