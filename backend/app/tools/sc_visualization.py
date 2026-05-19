from typing import Dict, Any
import os
import json

from app.tools.base import BaseTool

class UMAPPlotTool(BaseTool):
    name = "plot_umap"
    description = "Generate UMAP visualization for single-cell data"
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        import scanpy as sc
        import matplotlib.pyplot as plt
        
        h5ad_file = input_data.get("h5ad_file")
        annotation_file = input_data.get("annotation_file")
        result_dir = input_data.get("result_dir", os.path.dirname(h5ad_file))
        
        if not h5ad_file:
            raise ValueError("h5ad_file is required")
        
        os.makedirs(result_dir, exist_ok=True)
        
        adata = sc.read_h5ad(h5ad_file)
        
        plots = []
        
        plt.figure(figsize=(8, 6))
        sc.pl.umap(adata, color='leiden', title='Clusters', show=False)
        cluster_plot = os.path.join(result_dir, 'umap_clusters.png')
        plt.savefig(cluster_plot, dpi=300, bbox_inches='tight')
        plt.close()
        plots.append({"name": "clusters", "path": cluster_plot})
        
        if annotation_file and os.path.exists(annotation_file):
            with open(annotation_file, 'r') as f:
                annotations = json.load(f)
            
            cell_type_map = {k: v['cell_type'] for k, v in annotations.items()}
            adata.obs['cell_type'] = adata.obs['leiden'].map(cell_type_map)
            
            plt.figure(figsize=(8, 6))
            sc.pl.umap(adata, color='cell_type', title='Cell Types', show=False, legend_loc='on data')
            celltype_plot = os.path.join(result_dir, 'umap_celltypes.png')
            plt.savefig(celltype_plot, dpi=300, bbox_inches='tight')
            plt.close()
            plots.append({"name": "cell_types", "path": celltype_plot})
        
        if 'pca' in adata.obsm:
            plt.figure(figsize=(8, 6))
            sc.pl.pca(adata, color='leiden', title='PCA', show=False)
            pca_plot = os.path.join(result_dir, 'pca_plot.png')
            plt.savefig(pca_plot, dpi=300, bbox_inches='tight')
            plt.close()
            plots.append({"name": "pca", "path": pca_plot})
        
        return {
            "plots": plots,
            "n_plots": len(plots),
            "summary": f"UMAP可视化完成，生成了 {len(plots)} 张图。"
        }

class MarkerGenePlotTool(BaseTool):
    name = "plot_marker_genes"
    description = "Generate marker gene expression plots"
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        import scanpy as sc
        import matplotlib.pyplot as plt
        
        h5ad_file = input_data.get("h5ad_file")
        cluster_info_path = input_data.get("cluster_info_path")
        result_dir = input_data.get("result_dir", os.path.dirname(h5ad_file))
        n_markers = input_data.get("n_markers", 5)
        
        if not h5ad_file:
            raise ValueError("h5ad_file is required")
        
        os.makedirs(result_dir, exist_ok=True)
        
        adata = sc.read_h5ad(h5ad_file)
        
        plots = []
        
        if cluster_info_path and os.path.exists(cluster_info_path):
            with open(cluster_info_path, 'r') as f:
                cluster_info = json.load(f)
            
            all_markers = []
            for cluster_id, info in cluster_info.items():
                all_markers.extend(info['marker_genes'][:n_markers])
            
            top_markers = list(set(all_markers))[:10]
            
            for gene in top_markers:
                if gene in adata.var_names:
                    plt.figure(figsize=(8, 6))
                    sc.pl.umap(adata, color=gene, title=f'{gene} Expression', show=False, color_map='viridis')
                    gene_plot = os.path.join(result_dir, f'marker_{gene}.png')
                    plt.savefig(gene_plot, dpi=300, bbox_inches='tight')
                    plt.close()
                    plots.append({"gene": gene, "path": gene_plot})
        
        plt.figure(figsize=(12, 8))
        sc.pl.rank_genes_groups_heatmap(adata, n_genes=3, groupby='leiden', show=False)
        heatmap_plot = os.path.join(result_dir, 'marker_heatmap.png')
        plt.savefig(heatmap_plot, dpi=300, bbox_inches='tight')
        plt.close()
        plots.append({"name": "heatmap", "path": heatmap_plot})
        
        return {
            "plots": plots,
            "n_plots": len(plots),
            "summary": f"Marker基因可视化完成，生成了 {len(plots)} 张图。"
        }

class QCPlotTool(BaseTool):
    name = "plot_qc"
    description = "Generate QC metrics plots"
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        import scanpy as sc
        import matplotlib.pyplot as plt
        
        h5ad_file = input_data.get("h5ad_file")
        result_dir = input_data.get("result_dir", os.path.dirname(h5ad_file))
        
        if not h5ad_file:
            raise ValueError("h5ad_file is required")
        
        os.makedirs(result_dir, exist_ok=True)
        
        adata = sc.read_h5ad(h5ad_file)
        
        plots = []
        
        if 'total_counts' in adata.obs:
            plt.figure(figsize=(8, 6))
            sc.pl.violin(adata, keys='total_counts', groupby='leiden', show=False)
            violin_plot = os.path.join(result_dir, 'qc_violin.png')
            plt.savefig(violin_plot, dpi=300, bbox_inches='tight')
            plt.close()
            plots.append({"name": "violin", "path": violin_plot})
        
        if 'pct_counts_mt' in adata.obs:
            plt.figure(figsize=(8, 6))
            sc.pl.scatter(adata, x='total_counts', y='pct_counts_mt', color='leiden', show=False)
            scatter_plot = os.path.join(result_dir, 'qc_scatter.png')
            plt.savefig(scatter_plot, dpi=300, bbox_inches='tight')
            plt.close()
            plots.append({"name": "scatter", "path": scatter_plot})
        
        plt.figure(figsize=(8, 6))
        sc.pl.highest_expr_genes(adata, n_top=20, show=False)
        expr_plot = os.path.join(result_dir, 'highest_expr.png')
        plt.savefig(expr_plot, dpi=300, bbox_inches='tight')
        plt.close()
        plots.append({"name": "highest_expr", "path": expr_plot})
        
        return {
            "plots": plots,
            "n_plots": len(plots),
            "summary": f"QC可视化完成，生成了 {len(plots)} 张图。"
        }
