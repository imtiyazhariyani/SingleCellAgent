from dataclasses import dataclass, field
from typing import Dict, List, Optional

from single_cell_agent.metadata import infer_metadata_columns


@dataclass
class ValidationResult:
    status: str
    messages: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    inferred_columns: Dict[str, Optional[str]] = field(default_factory=dict)


def validate_adata(adata) -> ValidationResult:
    """
    Validate whether an AnnData object looks suitable for downstream analysis.
    """
    messages = []
    warnings = []

    if adata.n_obs == 0:
        warnings.append("AnnData object contains 0 cells.")

    if adata.n_vars == 0:
        warnings.append("AnnData object contains 0 genes/features.")

    if not adata.obs_names.is_unique:
        warnings.append("Cell/barcode names are not unique.")

    if not adata.var_names.is_unique:
        warnings.append("Gene/feature names are not unique.")

    inferred = infer_metadata_columns(adata)

    messages.append(f"Detected {adata.n_obs:,} cells and {adata.n_vars:,} genes/features.")

    for role, column in inferred.items():
        if column is None:
            warnings.append(f"Could not infer a likely `{role}` column in adata.obs.")
        else:
            messages.append(f"Inferred `{role}` column: `{column}`.")

    sample_col = inferred.get("sample")
    condition_col = inferred.get("condition")

    if sample_col and condition_col:
        sample_condition = adata.obs[[sample_col, condition_col]].drop_duplicates()
        condition_counts = sample_condition[condition_col].value_counts()

        for condition, n_samples in condition_counts.items():
            if n_samples < 2:
                warnings.append(
                    f"Condition `{condition}` appears to have fewer than 2 biological samples. "
                    "Pseudobulk differential expression may be underpowered or invalid."
                )

    status = "pass" if len(warnings) == 0 else "warning"

    return ValidationResult(
        status=status,
        messages=messages,
        warnings=warnings,
        inferred_columns=inferred,
    )
