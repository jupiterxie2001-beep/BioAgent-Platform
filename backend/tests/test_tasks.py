import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from unittest.mock import Mock, patch, MagicMock
from app.tasks.analysis_tasks import run_deg_analysis
from app.workflows.engine import WorkflowEngine

def test_deg_analysis_task():
    print("Testing DEG analysis task...")
    
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
    
    with patch('app.tasks.analysis_tasks.SessionLocal') as mock_session:
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        
        mock_job = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_job
        
        task = MagicMock()
        task.update_state = Mock()
        
        try:
            result = run_deg_analysis(task, test_file_path, 1)
            print(f"Task completed successfully!")
            print(f"Result keys: {list(result.keys())}")
            print(f"Status: {result.get('status')}")
            print(f"Summary: {result.get('summary')}")
            return True
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_workflow_engine():
    print("\nTesting Workflow Engine...")
    engine = WorkflowEngine()
    
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
    
    workflow_json = f'''
    {{
        "workflow_name": "bulk_deg_analysis",
        "steps": [
            {{"tool": "deseq2_analysis", "params": {{"file_path": "{test_file_path}"}}}}
        ]
    }}
    '''
    
    try:
        result = engine.execute_workflow(workflow_json)
        print(f"Workflow executed successfully!")
        print(f"Workflow name: {result.get('workflow_name')}")
        print(f"Summary: {result.get('summary')}")
        print(f"Results: {list(result.get('results', {}).keys())}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Testing BioAgent Async Task System")
    print("=" * 50)
    
    tests = [
        ("Workflow Engine", test_workflow_engine),
        ("DEG Analysis Task", test_deg_analysis_task),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\nRunning: {name}")
        print("-" * 30)
        try:
            if test_func():
                print(f"✓ {name} PASSED")
                passed += 1
            else:
                print(f"✗ {name} FAILED")
                failed += 1
        except Exception as e:
            print(f"✗ {name} ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    sys.exit(0 if failed == 0 else 1)
