import pandas as pd
import os

def detect_data_type(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in ['.h5ad', '.loom', '.rds']:
        return "sc_rna"
    elif ext in ['.mtx']:
        return "sc_rna_mtx"
    elif ext in ['.csv', '.tsv', '.txt', '.xlsx']:
        try:
            if ext == '.xlsx':
                df = pd.read_excel(file_path, nrows=100)
            elif ext == '.tsv':
                df = pd.read_csv(file_path, sep='\t', nrows=100)
            else:
                df = pd.read_csv(file_path, nrows=100)
            
            if df.shape[0] < df.shape[1]:
                return "bulk_rna"
            else:
                return "bulk_rna"
        except Exception:
            return "unknown"
    else:
        return "unknown"

def load_expression_matrix(file_path: str) -> pd.DataFrame:
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.xlsx':
        return pd.read_excel(file_path, index_col=0)
    elif ext == '.tsv':
        return pd.read_csv(file_path, sep='\t', index_col=0)
    else:
        return pd.read_csv(file_path, index_col=0)
