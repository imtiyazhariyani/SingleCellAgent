from typing import Optional

import pandas as pd
import scanpy as sc


def run_marker_analysis(
    adata,
    groupby: str,
    method: str = "wilcoxon",
    n_genes: int = 20,
) -> Optional[pd.DataFrame]:
    """
    Run basic marker-gene analysis using Scanpy.

    Parameters
    ----------
    adata:
        AnnData object.
    groupby:
        Column in adata.obs defining groups.
    method:
        Scanpy rank_genes_groups method.
    n_genes:
        Number of top genes to return per group.

    Returns
    -------
    DataFrame with marker genes, or None if groupby is invalid.
    """
    if groupby not in adata.obs.columns:
        raise ValueError(f"`{groupby}` is not present in adata.obs.")

    if adata.obs[groupby].nunique() < 2:
        raise ValueError(f"`{groupby}` must contain at least two groups.")

    adata_copy = adata.copy()

    sc.tl.rank_genes_groups(
        adata_copy,
        groupby=groupby,
        method=method,
        n_genes=n_genes,
    )

    result = adata_copy.uns["rank_genes_groups"]
    groups = result["names"].dtype.names

    rows = []

    for group in groups:
        names = result["names"][group]
        scores = result["scores"][group]

        pvals_adj = result.get("pvals_adj")
        logfoldchanges = result.get("logfoldchanges")

        for i, gene in enumerate(names[:n_genes]):
            rows.append(
                {
                    "group": group,
                    "rank": i + 1,
                    "gene": gene,
                    "score": float(scores[i]) if scores is not None else None,
                    "logfoldchange": float(logfoldchanges[group][i]) if logfoldchanges is not None else None,
                    "pval_adj": float(pvals_adj[group][i]) if pvals_adj is not None else None,
                }
            )

    return pd.DataFrame(rows)
