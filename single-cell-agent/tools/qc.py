import pandas as pd


def summarize_qc(adata) -> pd.DataFrame:
    """
    Generate a lightweight QC summary from an AnnData object.

    This does not modify the object.
    """
    qc = {
        "n_cells": adata.n_obs,
        "n_genes": adata.n_vars,
        "obs_columns": len(adata.obs.columns),
        "var_columns": len(adata.var.columns),
    }

    common_qc_cols = [
        "n_genes_by_counts",
        "total_counts",
        "pct_counts_mt",
        "pct_counts_ribo",
    ]

    for col in common_qc_cols:
        if col in adata.obs.columns:
            qc[f"{col}_median"] = float(adata.obs[col].median())
            qc[f"{col}_min"] = float(adata.obs[col].min())
            qc[f"{col}_max"] = float(adata.obs[col].max())

    return pd.DataFrame([qc])
