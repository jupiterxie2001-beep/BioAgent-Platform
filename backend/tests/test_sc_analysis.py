import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_scanpy_pipeline():
    print("Testing Scanpy Pipeline...")
    
    result_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(result_dir, exist_ok=True)
    
    import scanpy as sc
    import numpy as np
    import pandas as pd
    
    np.random.seed(42)
    n_cells = 100
    n_genes = 500
    genes = [f'Gene_{i}' for i in range(n_genes)]
    cells = [f'Cell_{i}' for i in range(n_cells)]
    
    data = np.random.poisson(lam=5, size=(n_genes, n_cells))
    adata = sc.AnnData(data.T)
    adata.var_names = genes
    adata.obs_names = cells
    
    test_file = os.path.join(result_dir, 'test_sc_data.h5ad')
    adata.write_h5ad(test_file)
    
    from app.tools.sc_analysis import ScanpyPipelineTool
    
    tool = ScanpyPipelineTool()
    
    try:
        result = tool.run({
            "file_path": test_file,
            "result_dir": result_dir,
            "min_cells": 1,
            "min_genes": 10,
            "n_top_genes": 100,
            "n_pcs": 20,
            "resolution": 0.5
        })
        print(f"✓ Scanpy pipeline executed successfully!")
        print(f"  Result path: {result.get('result_path')}")
        print(f"  Number of cells: {result.get('n_cells')}")
        print(f"  Number of genes: {result.get('n_genes')}")
        print(f"  Number of clusters: {result.get('n_clusters')}")
        print(f"  Summary: {result.get('summary')}")
        
        if os.path.exists(result['result_path']):
            print(f"  ✓ Result file created successfully")
        else:
            print(f"  ✗ Result file not found")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cell_type_annotation():
    print("\nTesting Cell Type Annotation...")
    
    result_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(result_dir, exist_ok=True)
    
    cluster_info = {
        "0": {
            "n_cells": 30,
            "marker_genes": ["CD3D", "CD3E", "CD8A", "TRAC", "GAPDH"]
        },
        "1": {
            "n_cells": 25,
            "marker_genes": ["CD19", "MS4A1", "CD79A", "IGHM", "ACTB"]
        },
        "2": {
            "n_cells": 45,
            "marker_genes": ["COL1A1", "COL1A2", "DCN", "POSTN", "VIM"]
        }
    }
    
    cluster_file = os.path.join(result_dir, 'test_clusters.json')
    with open(cluster_file, 'w') as f:
        json.dump(cluster_info, f)
    
    from app.tools.sc_analysis import CellTypeAnnotationTool
    
    tool = CellTypeAnnotationTool()
    
    try:
        result = tool.run({
            "cluster_info_path": cluster_file,
            "result_dir": result_dir
        })
        print(f"✓ Cell type annotation executed successfully!")
        print(f"  Annotation path: {result.get('annotation_path')}")
        print(f"  Summary:")
        for cluster_id, ann in result['annotations'].items():
            print(f"    Cluster {cluster_id}: {ann['cell_type']} (置信度: {ann['confidence']:.2f})")
        
        if os.path.exists(result['annotation_path']):
            print(f"  ✓ Annotation file created successfully")
        else:
            print(f"  ✗ Annotation file not found")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sc_visualization():
    print("\nTesting Single-cell Visualization Tools...")
    
    result_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(result_dir, exist_ok=True)
    
    import scanpy as sc
    import numpy as np
    
    np.random.seed(42)
    n_cells = 100
    n_genes = 200
    genes = [f'Gene_{i}' for i in range(n_genes)]
    cells = [f'Cell_{i}' for i in range(n_cells)]
    
    data = np.random.poisson(lam=5, size=(n_genes, n_cells))
    adata = sc.AnnData(data.T)
    adata.var_names = genes
    adata.obs_names = cells
    
    sc.pp.filter_cells(adata, min_genes=10)
    sc.pp.filter_genes(adata, min_cells=1)
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=50)
    adata = adata[:, adata.var.highly_variable]
    sc.pp.scale(adata, max_value=10)
    sc.tl.pca(adata, n_comps=10)
    sc.pp.neighbors(adata, n_neighbors=5, n_pcs=10)
    sc.tl.umap(adata)
    sc.tl.leiden(adata, resolution=0.5)
    sc.tl.rank_genes_groups(adata, 'leiden', method='t-test')
    
    test_file = os.path.join(result_dir, 'test_sc_vis.h5ad')
    adata.write_h5ad(test_file)
    
    cluster_info = {
        "0": {
            "n_cells": 50,
            "marker_genes": ["Gene_0", "Gene_1", "Gene_2", "Gene_3", "Gene_4"]
        },
        "1": {
            "n_cells": 50,
            "marker_genes": ["Gene_5", "Gene_6", "Gene_7", "Gene_8", "Gene_9"]
        }
    }
    
    cluster_file = os.path.join(result_dir, 'test_clusters_vis.json')
    with open(cluster_file, 'w') as f:
        json.dump(cluster_info, f)
    
    from app.tools.sc_visualization import UMAPPlotTool, MarkerGenePlotTool, QCPlotTool
    
    tests = [
        ("UMAP Plot", UMAPPlotTool, {"h5ad_file": test_file}),
        ("Marker Gene Plot", MarkerGenePlotTool, {"h5ad_file": test_file, "cluster_info_path": cluster_file}),
        ("QC Plot", QCPlotTool, {"h5ad_file": test_file}),
    ]
    
    all_passed = True
    for name, tool_class, params in tests:
        try:
            tool = tool_class()
            result = tool.run(params)
            print(f"✓ {name} executed successfully!")
            print(f"  Number of plots: {result.get('n_plots')}")
            
            for plot in result.get('plots', []):
                plot_path = plot.get('path') or plot.get('path')
                if plot_path and os.path.exists(plot_path):
                    print(f"    ✓ Plot created: {os.path.basename(plot_path)}")
                else:
                    print(f"    ✗ Plot file not found")
                    all_passed = False
        except Exception as e:
            print(f"✗ {name} failed: {e}")
            all_passed = False
    
    return all_passed

def test_tool_registry():
    print("\nTesting Tool Registry with SC Tools...")
    
    from app.tools.registry import list_tools, get_tool
    
    try:
        tools = list_tools()
        sc_tools = ['scanpy_pipeline', 'cell_type_annotation', 'plot_umap', 'plot_marker_genes', 'plot_qc']
        
        print("Available tools:")
        for tool_name in sc_tools:
            if tool_name in tools:
                print(f"  ✓ {tool_name}: {tools[tool_name]}")
                tool = get_tool(tool_name)
                assert tool.name == tool_name
            else:
                print(f"  ✗ {tool_name} not found")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Single-Cell Analysis Module")
    print("=" * 60)
    
    tests = [
        ("Scanpy Pipeline", test_scanpy_pipeline),
        ("Cell Type Annotation", test_cell_type_annotation),
        ("SC Visualization Tools", test_sc_visualization),
        ("Tool Registry", test_tool_registry),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\nRunning: {name}")
        print("-" * 40)
        try:
            if test_func():
                print(f"\n✓ {name} PASSED")
                passed += 1
            else:
                print(f"\n✗ {name} FAILED")
                failed += 1
        except Exception as e:
            print(f"\n✗ {name} ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    sys.exit(0 if failed == 0 else 1)
