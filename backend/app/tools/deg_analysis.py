from typing import Dict, Any
import pandas as pd
import numpy as np
from scipy.special import erf
import os
import json

from app.tools.base import BaseTool
from app.services.data_service import load_expression_matrix

class DESeq2Tool(BaseTool):
    name = "deseq2_analysis"
    description = "Perform differential expression analysis using DESeq2-like approach"
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        file_path = input_data.get("file_path")
        group1 = input_data.get("group1", "control")
        group2 = input_data.get("group2", "treatment")
        
        if not file_path:
            raise ValueError("file_path is required")
        
        df = load_expression_matrix(file_path)
        
        group_info = input_data.get("group_info")
        if group_info is None:
            n_samples = df.shape[1]
            half = n_samples // 2
            group_info = {col: group1 if i < half else group2 for i, col in enumerate(df.columns)}
        
        control_samples = [k for k, v in group_info.items() if v == group1]
        treatment_samples = [k for k, v in group_info.items() if v == group2]
        
        control_data = df[control_samples]
        treatment_data = df[treatment_samples]
        
        control_mean = control_data.mean(axis=1)
        treatment_mean = treatment_data.mean(axis=1)
        
        control_var = control_data.var(axis=1)
        treatment_var = treatment_data.var(axis=1)
        
        n_control = len(control_samples)
        n_treatment = len(treatment_samples)
        
        pooled_var = ((n_control - 1) * control_var + (n_treatment - 1) * treatment_var) / (n_control + n_treatment - 2)
        se = np.sqrt(pooled_var * (1/n_control + 1/n_treatment))
        
        log2_fold_change = np.log2((treatment_mean + 1e-6) / (control_mean + 1e-6))
        t_stat = (treatment_mean - control_mean) / se
        p_value = 2 * (1 - self._norm_cdf(np.abs(t_stat)))
        
        deg_df = pd.DataFrame({
            'baseMean': (control_mean + treatment_mean) / 2,
            'log2FoldChange': log2_fold_change,
            'lfcSE': se,
            't': t_stat,
            'pvalue': p_value,
            'padj': self._fdr_correct(p_value)
        })
        
        result_dir = os.path.join(os.path.dirname(file_path), 'results')
        os.makedirs(result_dir, exist_ok=True)
        
        result_file = os.path.join(result_dir, 'deg_results.csv')
        deg_df.to_csv(result_file)
        
        return {
            "result_path": result_file,
            "n_genes": len(deg_df),
            "n_significant": len(deg_df[deg_df['padj'] < 0.05]),
            "summary": f"DEG analysis completed. Found {len(deg_df[deg_df['padj'] < 0.05])} significant genes out of {len(deg_df)} total genes."
        }
    
    def _norm_cdf(self, x):
        return (1 + erf(x / np.sqrt(2))) / 2
    
    def _fdr_correct(self, p_values):
        if hasattr(p_values, 'values'):
            p_values = p_values.values
        
        sorted_indices = np.argsort(p_values)
        sorted_p = p_values[sorted_indices]
        n = len(p_values)
        adjusted = np.minimum(1, sorted_p * n / (np.arange(n) + 1))
        adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
        result = np.zeros(n)
        result[sorted_indices] = adjusted
        return result
