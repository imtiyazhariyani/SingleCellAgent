from pathlib import Path
from typing import Optional

import pandas as pd


def write_markdown_report(
    output_path: str,
    question: str,
    validation_result,
    plan,
    qc_summary: Optional[pd.DataFrame] = None,
    marker_results: Optional[pd.DataFrame] = None,
):
    """
    Write a simple Markdown analysis report.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = []

    lines.append("# SingleCellAgent Report\n")
    lines.append("## User Question\n")
    lines.append(f"> {question}\n")

    lines.append("## Dataset Validation\n")
    lines.append(f"**Status:** {validation_result.status}\n")

    lines.append("### Messages\n")
    for msg in validation_result.messages:
        lines.append(f"- {msg}")

    if validation_result.warnings:
        lines.append("\n### Warnings\n")
        for warning in validation_result.warnings:
            lines.append(f"- {warning}")

    lines.append("\n## Inferred Metadata Columns\n")
    for role, column in validation_result.inferred_columns.items():
        lines.append(f"- **{role}:** `{column}`")

    lines.append("\n## Analysis Plan\n")
    for i, step in enumerate(plan.steps, start=1):
        lines.append(f"{i}. {step}")

    if plan.required_metadata:
        lines.append("\n### Required Metadata\n")
        for item in plan.required_metadata:
            lines.append(f"- `{item}`")

    if plan.caveats:
        lines.append("\n### Caveats\n")
        for caveat in plan.caveats:
            lines.append(f"- {caveat}")

    if qc_summary is not None:
        lines.append("\n## QC Summary\n")
        lines.append(qc_summary.to_markdown(index=False))

    if marker_results is not None:
        lines.append("\n## Marker Gene Results\n")
        lines.append(marker_results.head(50).to_markdown(index=False))

    output_path.write_text("\n".join(lines))
