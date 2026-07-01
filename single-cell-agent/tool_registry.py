import json
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from single_cell_agent.io import load_adata
from single_cell_agent.metadata import summarize_metadata
from single_cell_agent.planning import create_analysis_plan
from single_cell_agent.reporting import write_markdown_report
from single_cell_agent.tools.qc import summarize_qc
from single_cell_agent.tools.markers import run_marker_analysis
from single_cell_agent.validation.checks import validate_adata


def _json_safe(obj: Any) -> Any:
    """
    Convert common Python/pandas/numpy objects into JSON-safe objects.
    """
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")

    if isinstance(obj, pd.Series):
        return obj.to_dict()

    if isinstance(obj, Path):
        return str(obj)

    if hasattr(obj, "item"):
        try:
            return obj.item()
        except Exception:
            pass

    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]

    if isinstance(obj, tuple):
        return [_json_safe(v) for v in obj]

    return obj


class SingleCellToolRegistry:
    """
    Holds dataset state and exposes deterministic analysis tools to the agent.
    """

    def __init__(self, adata_path: str, question: str, output_dir: str = "results"):
        self.adata_path = adata_path
        self.question = question
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.adata = load_adata(adata_path)

        self.validation_result = None
        self.metadata_summary = None
        self.plan = None
        self.qc_summary = None
        self.marker_results = None

    def tool_definitions(self):
        """
        Tool schemas exposed to Claude.
        """
        return [
            {
                "name": "validate_dataset",
                "description": (
                    "Validate the AnnData object. Checks dimensions, unique cell/gene names, "
                    "inferred metadata columns, and whether conditions have sufficient sample structure."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            },
            {
                "name": "summarize_metadata",
                "description": (
                    "Summarize AnnData metadata, including observation columns, likely sample/condition/"
                    "cell-type/batch columns, and top values in inferred metadata columns."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            },
            {
                "name": "create_analysis_plan",
                "description": (
                    "Create a structured analysis plan for the user's biological question using inferred metadata."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "The biological question to plan an analysis for.",
                        }
                    },
                    "required": ["question"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "summarize_qc",
                "description": (
                    "Generate a lightweight QC summary of the AnnData object, including cells, genes, "
                    "metadata columns, and common QC metrics if present."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            },
            {
                "name": "run_marker_analysis",
                "description": (
                    "Run Scanpy marker gene analysis using rank_genes_groups. Use this when the user asks "
                    "about marker genes, cell type annotations, or cluster-defining genes."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "groupby": {
                            "type": "string",
                            "description": (
                                "Column in adata.obs to group cells by. If unsure, use the inferred cell-type column."
                            ),
                        },
                        "n_genes": {
                            "type": "integer",
                            "description": "Number of marker genes to return per group.",
                            "default": 20,
                        },
                    },
                    "required": ["groupby"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "write_report",
                "description": (
                    "Write a Markdown report using the validation result, analysis plan, QC summary, "
                    "marker results, and final interpretation."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "final_summary": {
                            "type": "string",
                            "description": "Final evidence-grounded interpretation to include in the report.",
                        },
                        "filename": {
                            "type": "string",
                            "description": "Markdown filename for the report.",
                            "default": "single_cell_agent_report.md",
                        },
                    },
                    "required": ["final_summary"],
                    "additionalProperties": False,
                },
            },
        ]

    def run_tool(self, name: str, tool_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a tool by name.
        """
        tool_input = tool_input or {}

        try:
            if name == "validate_dataset":
                return self._validate_dataset()

            if name == "summarize_metadata":
                return self._summarize_metadata()

            if name == "create_analysis_plan":
                question = tool_input.get("question", self.question)
                return self._create_analysis_plan(question)

            if name == "summarize_qc":
                return self._summarize_qc()

            if name == "run_marker_analysis":
                groupby = tool_input["groupby"]
                n_genes = int(tool_input.get("n_genes", 20))
                return self._run_marker_analysis(groupby=groupby, n_genes=n_genes)

            if name == "write_report":
                final_summary = tool_input["final_summary"]
                filename = tool_input.get("filename", "single_cell_agent_report.md")
                return self._write_report(final_summary=final_summary, filename=filename)

            return {
                "status": "error",
                "error": f"Unknown tool: {name}",
            }

        except Exception as exc:
            return {
                "status": "error",
                "tool": name,
                "error": str(exc),
            }

    def _validate_dataset(self) -> Dict[str, Any]:
        self.validation_result = validate_adata(self.adata)

        return {
            "status": "success",
            "validation_status": self.validation_result.status,
            "messages": self.validation_result.messages,
            "warnings": self.validation_result.warnings,
            "inferred_columns": self.validation_result.inferred_columns,
        }

    def _summarize_metadata(self) -> Dict[str, Any]:
        self.metadata_summary = summarize_metadata(self.adata)

        compact_summary = {
            "n_cells": self.metadata_summary["n_cells"],
            "n_genes": self.metadata_summary["n_genes"],
            "obs_columns": self.metadata_summary["obs_columns"],
            "inferred_columns": self.metadata_summary["inferred_columns"],
        }

        for key, value in self.metadata_summary.items():
            if key.endswith("_values"):
                compact_summary[key] = value

        return {
            "status": "success",
            "metadata_summary": _json_safe(compact_summary),
        }

    def _create_analysis_plan(self, question: str) -> Dict[str, Any]:
        if self.validation_result is None:
            self._validate_dataset()

        self.plan = create_analysis_plan(
            question=question,
            inferred_columns=self.validation_result.inferred_columns,
        )

        return {
            "status": "success",
            "question": self.plan.question,
            "steps": self.plan.steps,
            "required_metadata": self.plan.required_metadata,
            "caveats": self.plan.caveats,
        }

    def _summarize_qc(self) -> Dict[str, Any]:
        self.qc_summary = summarize_qc(self.adata)

        output_path = self.output_dir / "qc_summary.csv"
        self.qc_summary.to_csv(output_path, index=False)

        return {
            "status": "success",
            "qc_summary": _json_safe(self.qc_summary),
            "output_path": str(output_path),
        }

    def _run_marker_analysis(self, groupby: str, n_genes: int = 20) -> Dict[str, Any]:
        self.marker_results = run_marker_analysis(
            self.adata,
            groupby=groupby,
            n_genes=n_genes,
        )

        output_path = self.output_dir / "marker_results.csv"
        self.marker_results.to_csv(output_path, index=False)

        return {
            "status": "success",
            "groupby": groupby,
            "n_genes": n_genes,
            "n_rows": len(self.marker_results),
            "top_results": _json_safe(self.marker_results.head(30)),
            "output_path": str(output_path),
        }

    def _write_report(self, final_summary: str, filename: str) -> Dict[str, Any]:
        if self.validation_result is None:
            self._validate_dataset()

        if self.plan is None:
            self._create_analysis_plan(self.question)

        report_path = self.output_dir / filename

        write_markdown_report(
            output_path=report_path,
            question=self.question,
            validation_result=self.validation_result,
            plan=self.plan,
            qc_summary=self.qc_summary,
            marker_results=self.marker_results,
        )

        with open(report_path, "a") as handle:
            handle.write("\n\n## Agent Interpretation\n\n")
            handle.write(final_summary.strip())
            handle.write("\n")

        return {
            "status": "success",
            "report_path": str(report_path),
        }


def tool_result_to_json(result: Dict[str, Any]) -> str:
    return json.dumps(_json_safe(result), indent=2)
