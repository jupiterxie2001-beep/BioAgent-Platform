from typing import Dict, Any
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

from app.tools.base import BaseTool

class VolcanoPlotTool(BaseTool):
    name = "plot_volcano"
    description = "Generate volcano plot from DEG results"
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        deg_file = input_data.get("deg_file")
        result_dir = input_data.get("result_dir", os.path.dirname(deg_file))
        
        if not deg_file:
            raise ValueError("deg_file is required")
        
        df = pd.read_csv(deg_file, index_col=0)
        
        plt.figure(figsize=(10, 6))
        
        df['color'] = 'gray'
        df.loc[(df['log2FoldChange'] > 1) & (df['padj'] < 0.05), 'color'] = 'red'
        df.loc[(df['log2FoldChange'] < -1) & (df['padj'] < 0.05), 'color'] = 'blue'
        
        sns.scatterplot(x='log2FoldChange', y=-np.log10(df['padj']), 
                        hue='color', data=df, alpha=0.6)
        
        plt.axvline(x=-1, color='black', linestyle='--')
        plt.axvline(x=1, color='black', linestyle='--')
        plt.axhline(y=-np.log10(0.05), color='black', linestyle='--')
        
        plt.xlabel('log2(Fold Change)')
        plt.ylabel('-log10(Adjusted p-value)')
        plt.title('Volcano Plot')
        
        result_file = os.path.join(result_dir, 'volcano_plot.png')
        plt.savefig(result_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return {
            "plot_path": result_file,
            "n_upregulated": len(df[(df['log2FoldChange'] > 1) & (df['padj'] < 0.05)]),
            "n_downregulated": len(df[(df['log2FoldChange'] < -1) & (df['padj'] < 0.05)])
        }

class HeatmapTool(BaseTool):
    name = "plot_heatmap"
    description = "Generate heatmap of top DEGs"
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        deg_file = input_data.get("deg_file")
        expression_file = input_data.get("expression_file")
        result_dir = input_data.get("result_dir", os.path.dirname(deg_file))
        n_genes = input_data.get("n_genes", 50)
        
        if not deg_file or not expression_file:
            raise ValueError("deg_file and expression_file are required")
        
        deg_df = pd.read_csv(deg_file, index_col=0)
        expr_df = pd.read_csv(expression_file, index_col=0)
        
        deg_df = deg_df.sort_values('padj').head(n_genes)
        top_genes = deg_df.index.tolist()
        
        heatmap_data = expr_df.loc[top_genes]
        
        plt.figure(figsize=(12, 10))
        sns.clustermap(heatmap_data, z_score=0, cmap='RdBu_r', 
                       row_cluster=True, col_cluster=True,
                       figsize=(12, 10))
        
        result_file = os.path.join(result_dir, 'heatmap.png')
        plt.savefig(result_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return {
            "plot_path": result_file,
            "n_genes_plotted": len(top_genes)
        }
