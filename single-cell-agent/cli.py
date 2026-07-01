import argparse
from pathlib import Path

from single_cell_agent.agent import run_single_cell_agent
from single_cell_agent.io import load_adata
from single_cell_agent.metadata import summarize_metadata
from single_cell_agent.planning import create_analysis_plan
from single_cell_agent.reporting import write_markdown_report
from single_cell_agent.tools.qc import summarize_qc
from single_cell_agent.tools.markers import run_marker_analysis
from single_cell_agent.validation.checks import validate_adata

def cmd_agent(args):
    final_answer = run_single_cell_agent(
        adata_path=args.adata,
        question=args.question,
        output_dir=args.out,
        model=args.model,
        max_turns=args.max_turns,
    )

    print("\nFinal agent response:\n")
    print(final_answer)

def cmd_validate(args):
    adata = load_adata(args.adata)
    result = validate_adata(adata)

    print(f"Validation status: {result.status}\n")

    print("Messages:")
    for msg in result.messages:
        print(f"- {msg}")

    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"- {warning}")


def cmd_metadata(args):
    adata = load_adata(args.adata)
    summary = summarize_metadata(adata)

    print(f"Cells: {summary['n_cells']:,}")
    print(f"Genes/features: {summary['n_genes']:,}")

    print("\nInferred columns:")
    for role, column in summary["inferred_columns"].items():
        print(f"- {role}: {column}")

    print("\nObservation columns:")
    for col in summary["obs_columns"]:
        print(f"- {col}")


def cmd_plan(args):
    adata = load_adata(args.adata)
    validation = validate_adata(adata)
    plan = create_analysis_plan(args.question, validation.inferred_columns)

    print("Analysis plan:\n")
    for i, step in enumerate(plan.steps, start=1):
        print(f"{i}. {step}")

    if plan.required_metadata:
        print("\nRequired metadata:")
        for item in plan.required_metadata:
            print(f"- {item}")

    if plan.caveats:
        print("\nCaveats:")
        for caveat in plan.caveats:
            print(f"- {caveat}")


def cmd_run(args):
    adata = load_adata(args.adata)
    validation = validate_adata(adata)
    plan = create_analysis_plan(args.question, validation.inferred_columns)
    qc_summary = summarize_qc(adata)

    marker_results = None

    cell_type_col = validation.inferred_columns.get("cell_type")

    if cell_type_col is not None and args.run_markers:
        marker_results = run_marker_analysis(
            adata,
            groupby=cell_type_col,
            n_genes=args.n_marker_genes,
        )

    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "single_cell_agent_report.md"

    write_markdown_report(
        output_path=report_path,
        question=args.question,
        validation_result=validation,
        plan=plan,
        qc_summary=qc_summary,
        marker_results=marker_results,
    )

    print(f"Report written to: {report_path}")


def main():
    parser = argparse.ArgumentParser(
        description="SingleCellAgent: AI-guided single-cell analysis agent"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate an AnnData object")
    validate_parser.add_argument("--adata", required=True, help="Path to .h5ad file")
    validate_parser.set_defaults(func=cmd_validate)

    metadata_parser = subparsers.add_parser("metadata", help="Summarize AnnData metadata")
    metadata_parser.add_argument("--adata", required=True, help="Path to .h5ad file")
    metadata_parser.set_defaults(func=cmd_metadata)

    plan_parser = subparsers.add_parser("plan", help="Create an analysis plan")
    plan_parser.add_argument("--adata", required=True, help="Path to .h5ad file")
    plan_parser.add_argument("--question", required=True, help="Biological question")
    plan_parser.set_defaults(func=cmd_plan)

    run_parser = subparsers.add_parser("run", help="Run a basic SingleCellAgent workflow")
    run_parser.add_argument("--adata", required=True, help="Path to .h5ad file")
    run_parser.add_argument("--question", required=True, help="Biological question")
    run_parser.add_argument("--out", default="results", help="Output directory")
    run_parser.add_argument("--run-markers", action="store_true", help="Run marker gene analysis")
    run_parser.add_argument("--n-marker-genes", type=int, default=20, help="Number of markers per group")
    run_parser.set_defaults(func=cmd_run)

    agent_parser = subparsers.add_parser("agent", help="Run the LLM-powered SingleCellAgent")
    agent_parser.add_argument("--adata", required=True, help="Path to .h5ad file")
    agent_parser.add_argument("--question", required=True, help="Biological question")
    agent_parser.add_argument("--out", default="results", help="Output directory")
    agent_parser.add_argument(
        "--model",
        default=None,
        help="Anthropic model name. Defaults to ANTHROPIC_MODEL env var or claude-sonnet-4-5.",
    )
    agent_parser.add_argument(
        "--max-turns",
        type=int,
        default=8,
        help="Maximum number of agent/tool-use turns.",
    )
    agent_parser.set_defaults(func=cmd_agent)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
