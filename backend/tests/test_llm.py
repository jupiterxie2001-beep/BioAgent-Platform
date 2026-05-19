import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_llm_provider():
    print("Testing LLM Provider...")
    
    from app.agents.llm_provider import LLMProvider
    
    provider = LLMProvider()
    
    print(f"  Using local mode: {provider.use_local}")
    
    test_results = {
        "deseq2_analysis": {
            "n_genes": 1000,
            "n_significant": 150,
            "summary": "DEG analysis completed"
        },
        "run_go_enrichment": {
            "n_bp": 25,
            "n_cc": 15,
            "n_mf": 20,
            "summary": "GO enrichment completed"
        }
    }
    
    try:
        interpretation = provider.interpret_results(test_results, "请解释差异分析结果")
        print(f"✓ Interpretation generated successfully!")
        print(f"  Interpretation:\n{interpretation}\n")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_query_parsing():
    print("Testing Query Parsing...")
    
    from app.agents.llm_provider import LLMProvider
    
    provider = LLMProvider()
    
    test_queries = [
        ("帮我做差异表达分析", "deg_analysis"),
        ("进行单细胞RNA-seq分析", "sc_rna_seq"),
        ("GO富集分析", "go_enrichment"),
        ("GSEA通路分析", "gsea_analysis"),
        ("绘制火山图", "plot_volcano"),
        ("帮我分析数据", "unknown"),
    ]
    
    all_passed = True
    for query, expected_task in test_queries:
        try:
            parsed = provider.parse_user_query(query)
            actual_task = parsed.get("task")
            status = "✓" if actual_task == expected_task else "✗"
            print(f"  {status} '{query}' -> {actual_task} (expected: {expected_task})")
            
            if actual_task != expected_task:
                all_passed = False
                
        except Exception as e:
            print(f"  ✗ '{query}' -> Error: {e}")
            all_passed = False
    
    return all_passed

def test_chat_completion():
    print("Testing Chat Completion...")
    
    from app.agents.llm_provider import LLMProvider
    
    provider = LLMProvider()
    
    test_messages = [
        [{"role": "user", "content": "你好，我需要帮助"}],
        [{"role": "user", "content": "什么是差异分析？"}],
        [{"role": "user", "content": "帮我进行单细胞分析"}],
    ]
    
    all_passed = True
    for messages in test_messages:
        try:
            response = provider.chat_completion(messages)
            print(f"✓ Message: '{messages[-1]['content']}'")
            print(f"  Response: {response[:100]}...\n")
            
            if not response:
                all_passed = False
                
        except Exception as e:
            print(f"✗ Error: {e}")
            all_passed = False
    
    return all_passed

def test_sc_interpretation():
    print("Testing Single-Cell Interpretation...")
    
    from app.agents.llm_provider import LLMProvider
    
    provider = LLMProvider()
    
    test_results = {
        "scanpy_pipeline": {
            "n_cells": 5000,
            "n_genes": 10000,
            "n_clusters": 8,
            "summary": "Single-cell analysis completed"
        },
        "cell_type_annotation": {
            "annotations": {
                "0": {"cell_type": "T cells", "confidence": 0.85},
                "1": {"cell_type": "B cells", "confidence": 0.78},
                "2": {"cell_type": "Macrophages", "confidence": 0.92},
            },
            "summary": "Cell type annotation completed"
        }
    }
    
    try:
        interpretation = provider.interpret_results(test_results, "请解释单细胞分析结果")
        print(f"✓ SC Interpretation generated successfully!")
        print(f"  Interpretation:\n{interpretation}\n")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_report_generation():
    print("Testing Report Generation...")
    
    from app.agents.llm_provider import LLMProvider
    
    provider = LLMProvider()
    
    test_results = {
        "deseq2_analysis": {
            "n_genes": 500,
            "n_significant": 50,
            "summary": "DEG analysis completed"
        }
    }
    
    try:
        report = provider.generate_report(test_results, "测试分析")
        print(f"✓ Report generated successfully!")
        print(f"  Report length: {len(report)} characters")
        print(f"  First 200 chars:\n{report[:200]}...\n")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing LLM Interpretation Module")
    print("=" * 60)
    
    tests = [
        ("LLM Provider", test_llm_provider),
        ("Query Parsing", test_query_parsing),
        ("Chat Completion", test_chat_completion),
        ("SC Interpretation", test_sc_interpretation),
        ("Report Generation", test_report_generation),
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
