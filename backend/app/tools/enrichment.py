from typing import Dict, Any
import pandas as pd
import os
import gseapy as gp

from app.tools.base import BaseTool

class GSEATool(BaseTool):
    name = "run_gsea"
    description = "Perform GSEA enrichment analysis"
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        deg_file = input_data.get("deg_file")
        result_dir = input_data.get("result_dir", os.path.dirname(deg_file))
        gene_sets = input_data.get("gene_sets", "GO_Biological_Process_2023")
        
        if not deg_file:
            raise ValueError("deg_file is required")
        
        deg_df = pd.read_csv(deg_file, index_col=0)
        ranked_genes = deg_df['log2FoldChange'].sort_values(ascending=False)
        
        gsea_results = gp.prerank(
            rnk=ranked_genes,
            gene_sets=gene_sets,
            outdir=None
        )
        
        result_df = gsea_results.res2d
        
        result_file = os.path.join(result_dir, 'gsea_results.csv')
        result_df.to_csv(result_file)
        
        return {
            "result_path": result_file,
            "n_significant": len(result_df[result_df['fdr'] < 0.25]),
            "top_pathways": result_df.head(5)['Name'].tolist()
        }

class GOEnrichmentTool(BaseTool):
    name = "run_go_enrichment"
    description = "Perform GO enrichment analysis"
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        deg_file = input_data.get("deg_file")
        result_dir = input_data.get("result_dir", os.path.dirname(deg_file))
        pvalue_cutoff = input_data.get("pvalue_cutoff", 0.05)
        
        if not deg_file:
            raise ValueError("deg_file is required")
        
        deg_df = pd.read_csv(deg_file, index_col=0)
        significant_genes = deg_df[deg_df['padj'] < pvalue_cutoff].index.tolist()
        
        go_results = gp.enrichr(
            gene_list=significant_genes,
            gene_sets='GO_Biological_Process_2023',
            organism='human',
            outdir=None
        )
        
        result_df = go_results.results
        
        result_file = os.path.join(result_dir, 'go_results.csv')
        result_df.to_csv(result_file)
        
        return {
            "result_path": result_file,
            "n_significant_terms": len(result_df[result_df['Adjusted P-value'] < pvalue_cutoff]),
            "top_terms": result_df.head(5)['Term'].tolist()
        }
