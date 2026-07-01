from typing import Dict, Optional


COLUMN_CANDIDATES = {
    "sample": ["sample", "sample_id", "donor", "donor_id", "individual", "replicate", "batch_sample"],
    "condition": ["condition", "group", "treatment", "disease", "status", "genotype", "phenotype"],
    "cell_type": ["cell_type", "celltype", "cell type", "annotation", "cluster_annotation", "cell_label"],
    "batch": ["batch", "library", "lane", "chemistry", "dataset", "study"],
}


def infer_metadata_columns(adata) -> Dict[str, Optional[str]]:
    """
    Try to infer important metadata columns from adata.obs.

    This is intentionally simple for v0. Later, this can be replaced by
    an LLM-assisted schema-mapping step with human confirmation.
    """
    obs_cols = list(adata.obs.columns)
    obs_lower = {col.lower(): col for col in obs_cols}

    inferred = {}

    for role, candidates in COLUMN_CANDIDATES.items():
        match = None

        # Exact case-insensitive match
        for candidate in candidates:
            if candidate.lower() in obs_lower:
                match = obs_lower[candidate.lower()]
                break

        # Partial match fallback
        if match is None:
            for col in obs_cols:
                col_lower = col.lower()
                if any(candidate.lower() in col_lower for candidate in candidates):
                    match = col
                    break

        inferred[role] = match

    return inferred


def summarize_metadata(adata) -> dict:
    """
    Summarize obs metadata columns and likely key fields.
    """
    inferred = infer_metadata_columns(adata)

    summary = {
        "n_cells": int(adata.n_obs),
        "n_genes": int(adata.n_vars),
        "obs_columns": list(adata.obs.columns),
        "inferred_columns": inferred,
    }

    for role, column in inferred.items():
        if column is not None:
            value_counts = adata.obs[column].value_counts(dropna=False).head(20)
            summary[f"{role}_values"] = value_counts.to_dict()

    return summary
