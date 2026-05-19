from typing import Dict, Any
import os
import json

from app.tools.base import BaseTool

class ScanpyPipelineTool(BaseTool):
    name = "scanpy_pipeline"
    description = "Run standard Scanpy single-cell RNA-seq analysis pipeline"
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        import scanpy as sc
        
        file_path = input_data.get("file_path")
        result_dir = input_data.get("result_dir", os.path.dirname(file_path))
        min_cells = input_data.get("min_cells", 3)
        min_genes = input_data.get("min_genes", 200)
        n_top_genes = input_data.get("n_top_genes", 2000)
        n_pcs = input_data.get("n_pcs", 50)
        resolution = input_data.get("resolution", 0.5)
        
        if not file_path:
            raise ValueError("file_path is required")
        
        os.makedirs(result_dir, exist_ok=True)
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.h5ad':
            adata = sc.read_h5ad(file_path)
        elif ext == '.mtx':
            adata = sc.read_mtx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
        
        sc.pp.filter_cells(adata, min_genes=min_genes)
        sc.pp.filter_genes(adata, min_cells=min_cells)
        
        adata.var['mt'] = adata.var_names.str.startswith('MT-')
        sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None, log1p=False, inplace=True)
        
        sc.pp.normalize_total(adata, target_sum=1e4)
        sc.pp.log1p(adata)
        
        sc.pp.highly_variable_genes(adata, min_mean=0.0125, max_mean=3, min_disp=0.5, n_top_genes=n_top_genes)
        adata.raw = adata
        adata = adata[:, adata.var.highly_variable]
        
        sc.pp.scale(adata, max_value=10)
        sc.tl.pca(adata, svd_solver='arpack', n_comps=n_pcs)
        
        sc.pp.neighbors(adata, n_neighbors=10, n_pcs=n_pcs)
        sc.tl.umap(adata)
        
        sc.tl.leiden(adata, resolution=resolution)
        
        sc.tl.rank_genes_groups(adata, 'leiden', method='t-test')
        
        result_file = os.path.join(result_dir, 'sc_analysis.h5ad')
        adata.write_h5ad(result_file)
        
        cluster_info = {}
        for cluster in adata.obs['leiden'].cat.categories:
            marker_genes = adata.uns['rank_genes_groups']['names'][cluster][:10].tolist()
            cluster_info[str(cluster)] = {
                'n_cells': int((adata.obs['leiden'] == cluster).sum()),
                'marker_genes': marker_genes
            }
        
        cluster_file = os.path.join(result_dir, 'cluster_info.json')
        with open(cluster_file, 'w') as f:
            json.dump(cluster_info, f, indent=2)
        
        return {
            "result_path": result_file,
            "cluster_info_path": cluster_file,
            "n_cells": adata.n_obs,
            "n_genes": adata.n_vars,
            "n_clusters": len(adata.obs['leiden'].cat.categories),
            "cluster_info": cluster_info,
            "summary": f"单细胞分析完成。共 {adata.n_obs} 个细胞，识别到 {len(adata.obs['leiden'].cat.categories)} 个细胞群。"
        }

class CellTypeAnnotationTool(BaseTool):
    name = "cell_type_annotation"
    description = "Automatically annotate cell types using marker genes and AI"
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        import pandas as pd
        import json
        
        cluster_info_path = input_data.get("cluster_info_path")
        result_dir = input_data.get("result_dir", os.path.dirname(cluster_info_path))
        
        if not cluster_info_path:
            raise ValueError("cluster_info_path is required")
        
        with open(cluster_info_path, 'r') as f:
            cluster_info = json.load(f)
        
        marker_database = {
            'T cells': ['CD3D', 'CD3E', 'CD8A', 'CD4', 'TRAC', 'TRBC1', 'TRBC2'],
            'B cells': ['CD19', 'MS4A1', 'CD79A', 'CD79B', 'IGHM', 'IGHD'],
            'Macrophages': ['CD68', 'CD14', 'CSF1R', 'FCGR1A', 'LYZ', 'MRC1'],
            'Neutrophils': ['S100A8', 'S100A9', 'CSF3R', 'ELANE', 'MPO'],
            'Endothelial cells': ['PECAM1', 'CD31', 'VWF', 'SOX9'],
            'Fibroblasts': ['COL1A1', 'COL1A2', 'COL3A1', 'DCN', 'POSTN'],
            'Epithelial cells': ['EPCAM', 'KRT8', 'KRT18', 'KRT19'],
            'NK cells': ['NCAM1', 'KLRD1', 'NKG7', 'GZMB', 'PRF1'],
            'Monocytes': ['CD14', 'FCGR3A', 'LYZ', 'S100A8'],
            'Dendritic cells': ['CD1C', 'CD1A', 'CLEC9A', 'FCER1A'],
            'Plasma cells': ['IGHG1', 'IGHG2', 'IGHG3', 'IGHA1', 'SDC1'],
            'Stem cells': ['POU5F1', 'NANOG', 'SOX2', 'LIN28A'],
        }
        
        annotations = {}
        for cluster_id, info in cluster_info.items():
            marker_genes = info['marker_genes']
            scores = {}
            
            for cell_type, markers in marker_database.items():
                score = sum(1 for gene in marker_genes if gene in markers)
                scores[cell_type] = score
            
            if scores:
                best_match = max(scores, key=scores.get)
                confidence = scores[best_match] / len(marker_database[best_match])
                
                annotations[cluster_id] = {
                    'cell_type': best_match if confidence > 0.2 else 'Unknown',
                    'confidence': float(confidence),
                    'marker_genes': marker_genes,
                    'matching_markers': [g for g in marker_genes if g in marker_database.get(best_match, [])]
                }
            else:
                annotations[cluster_id] = {
                    'cell_type': 'Unknown',
                    'confidence': 0.0,
                    'marker_genes': marker_genes,
                    'matching_markers': []
                }
        
        annotation_file = os.path.join(result_dir, 'cell_type_annotations.json')
        with open(annotation_file, 'w') as f:
            json.dump(annotations, f, indent=2)
        
        summary = []
        for cluster_id, ann in annotations.items():
            if ann['cell_type'] != 'Unknown':
                summary.append(f"Cluster {cluster_id}: {ann['cell_type']} (置信度: {ann['confidence']:.2f})")
        
        return {
            "annotation_path": annotation_file,
            "annotations": annotations,
            "summary": "\n".join(summary) if summary else "未能识别任何已知细胞类型。"
        }
