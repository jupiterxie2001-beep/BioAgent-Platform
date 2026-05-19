import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_deg_tool():
    print("Testing DESeq2 Tool...")
    
    test_file_path = os.path.join(os.path.dirname(__file__), 'test_data.csv')
    
    if not os.path.exists(test_file_path):
        print("Creating test data...")
        import pandas as pd
        import numpy as np
        np.random.seed(42)
        genes = [f'Gene_{i}' for i in range(100)]
        control_samples = [f'Control_{i}' for i in range(3)]
        treatment_samples = [f'Treatment_{i}' for i in range(3)]
        data = np.random.poisson(lam=50, size=(100, 6))
        df = pd.DataFrame(data, index=genes, columns=control_samples + treatment_samples)
        df.to_csv(test_file_path)
    
    from app.tools.deg_analysis import DESeq2Tool
    
    tool = DESeq2Tool()
    
    try:
        result = tool.run({"file_path": test_file_path})
        print(f"✓ DESeq2 tool executed successfully!")
        print(f"  Result path: {result.get('result_path')}")
        print(f"  Number of genes: {result.get('n_genes')}")
        print(f"  Significant genes: {result.get('n_significant')}")
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

def test_workflow_engine():
    print("\nTesting Workflow Engine...")
    
    test_file_path = os.path.join(os.path.dirname(__file__), 'test_data.csv')
    
    if not os.path.exists(test_file_path):
        print("Creating test data...")
        import pandas as pd
        import numpy as np
        np.random.seed(42)
        genes = [f'Gene_{i}' for i in range(100)]
        control_samples = [f'Control_{i}' for i in range(3)]
        treatment_samples = [f'Treatment_{i}' for i in range(3)]
        data = np.random.poisson(lam=50, size=(100, 6))
        df = pd.DataFrame(data, index=genes, columns=control_samples + treatment_samples)
        df.to_csv(test_file_path)
    
    from app.workflows.engine import WorkflowEngine
    
    engine = WorkflowEngine()
    
    workflow_dict = {
        "workflow_name": "bulk_deg_analysis",
        "steps": [
            {"tool": "deseq2_analysis", "params": {"file_path": test_file_path}}
        ]
    }
    workflow_json = json.dumps(workflow_dict)
    
    try:
        result = engine.execute_workflow(workflow_json)
        print(f"✓ Workflow executed successfully!")
        print(f"  Workflow name: {result.get('workflow_name')}")
        print(f"  Summary: {result.get('summary')}")
        print(f"  Results: {list(result.get('results', {}).keys())}")
        
        if 'deseq2_analysis' in result['results']:
            deg_result = result['results']['deseq2_analysis']
            print(f"  DEG analysis result:")
            print(f"    - Result path: {deg_result.get('result_path')}")
            print(f"    - Number of genes: {deg_result.get('n_genes')}")
            print(f"    - Significant genes: {deg_result.get('n_significant')}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_visualization_tools():
    print("\nTesting Visualization Tools...")
    
    test_file_path = os.path.join(os.path.dirname(__file__), 'test_data.csv')
    
    if not os.path.exists(test_file_path):
        print("Creating test data...")
        import pandas as pd
        import numpy as np
        np.random.seed(42)
        genes = [f'Gene_{i}' for i in range(100)]
        control_samples = [f'Control_{i}' for i in range(3)]
        treatment_samples = [f'Treatment_{i}' for i in range(3)]
        data = np.random.poisson(lam=50, size=(100, 6))
        df = pd.DataFrame(data, index=genes, columns=control_samples + treatment_samples)
        df.to_csv(test_file_path)
    
    from app.tools.deg_analysis import DESeq2Tool
    from app.tools.visualization import VolcanoPlotTool, HeatmapTool
    
    deseq_tool = DESeq2Tool()
    deg_result = deseq_tool.run({"file_path": test_file_path})
    
    tests = [
        ("Volcano Plot", VolcanoPlotTool, {"deg_file": deg_result['result_path']}),
        ("Heatmap", HeatmapTool, {"deg_file": deg_result['result_path'], "expression_file": test_file_path}),
    ]
    
    all_passed = True
    for name, tool_class, params in tests:
        try:
            tool = tool_class()
            result = tool.run(params)
            print(f"✓ {name} executed successfully!")
            print(f"  Plot path: {result.get('plot_path')}")
            
            if os.path.exists(result['plot_path']):
                print(f"  ✓ Plot file created successfully")
            else:
                print(f"  ✗ Plot file not found")
                all_passed = False
        except Exception as e:
            print(f"✗ {name} failed: {e}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("=" * 60)
    print("Testing BioAgent Workflow System")
    print("=" * 60)
    
    tests = [
        ("DESeq2 Tool", test_deg_tool),
        ("Workflow Engine", test_workflow_engine),
        ("Visualization Tools", test_visualization_tools),
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
