from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class AnalysisPlan:
    question: str
    steps: List[str] = field(default_factory=list)
    required_metadata: List[str] = field(default_factory=list)
    caveats: List[str] = field(default_factory=list)


def create_analysis_plan(question: str, inferred_columns: Dict[str, str]) -> AnalysisPlan:
    """
    Create a simple rule-based analysis plan from a biological question.

    This is the placeholder for the future LLM planner.
    """
    q = question.lower()

    steps = [
        "Load AnnData object.",
        "Validate dataset dimensions and metadata.",
        "Inspect inferred sample, condition, cell-type, and batch columns.",
    ]

    required_metadata = []
    caveats = []

    if any(term in q for term in ["differential", "de ", "disease", "condition", "treatment", "changed", "changes"]):
        steps.extend([
            "Check whether condition and biological sample columns are present.",
            "Assess whether each condition has sufficient biological replicates.",
            "Recommend pseudobulk differential expression for sample-aware inference.",
            "Summarize top differentially expressed genes by cell type.",
        ])
        required_metadata.extend(["condition", "sample", "cell_type"])
        caveats.append(
            "Cell-level differential expression can inflate significance if biological replicates are ignored."
        )

    if any(term in q for term in ["marker", "markers", "cell type", "cluster"]):
        steps.extend([
            "Run marker gene analysis across cell types or clusters.",
            "Check whether marker genes support existing annotations.",
        ])
        required_metadata.append("cell_type")

    if any(term in q for term in ["trajectory", "pseudotime", "development"]):
        steps.extend([
            "Inspect whether trajectory or pseudotime information is present.",
            "Evaluate gene expression trends along the trajectory.",
        ])
        caveats.append(
            "Trajectory interpretation depends strongly on preprocessing, cell-state coverage, and biological context."
        )

    if any(term in q for term in ["batch", "confound", "replicate"]):
        steps.extend([
            "Check whether batch, sample, and condition are confounded.",
            "Report potentially invalid comparisons."
        ])
        required_metadata.extend(["batch", "sample", "condition"])

    # Remove duplicates while preserving order
    required_metadata = list(dict.fromkeys(required_metadata))
    caveats = list(dict.fromkeys(caveats))

    if not required_metadata:
        caveats.append(
            "The question is broad. The agent should first clarify the biological comparison and relevant metadata."
        )

    return AnalysisPlan(
        question=question,
        steps=steps,
        required_metadata=required_metadata,
        caveats=caveats,
    )
