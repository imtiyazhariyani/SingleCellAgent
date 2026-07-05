# SingleCellAgent
**Prototype AI-guided single-cell analysis agent that translates natural-language biological questions into reproducible Scanpy workflows, executes deterministic analysis modules, and validates outputs with automated checks**

SingleCellAgent is a prototype agentic system for single-cell genomics workflows. The goal is to help researchers translate biological questions into reproducible computational analyses, execute deterministic Scanpy-based workflows, validate outputs with automated checks, and generate evidence-grounded biological summaries.

This project is motivated by a common challenge in single-cell analysis: the hardest parts are often not running a function, but deciding whether the comparison is valid, whether the metadata supports the question, whether the statistical test is appropriate, and whether the biological interpretation is justified.

SingleCellAgent is designed as an AI-assisted analysis layer around real bioinformatics tools, with an emphasis on reliability, reproducibility, and transparent reasoning.

## Example Agent Run

SingleCellAgent was tested on the `10x_pbmc68k_reduced.h5ad` demo dataset with the question:

> Which marker genes distinguish the annotated PBMC cell types in this dataset, and do the marker patterns support the existing cell-type labels?

The agent validated the AnnData object, inspected metadata, ran deterministic Scanpy marker analysis, and generated an evidence-grounded report.

[View example PBMC marker analysis report](examples/reports/pbmc_marker_analysis_report.md)

## Setup

Clone the repository and install the package locally:

```bash
git clone https://github.com/imtiyazhariyani/SingleCellAgent.git
cd SingleCellAgent
pip install -e .
```

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="your_api_key_here"
```

Download or provide an `.h5ad` file, then run the agent:

```bash
single-cell-agent agent \
  --adata data/10x_pbmc68k_reduced.h5ad \
  --question "Which marker genes distinguish the annotated PBMC cell types in this dataset, and do the marker patterns support the existing cell-type labels?" \
  --out results/
```

The agent will validate the `AnnData` object, inspect metadata, run deterministic Scanpy-based analysis tools, and write outputs to the `results/` directory.

For non-LLM testing, you can also run:

```bash
single-cell-agent validate --adata data/10x_pbmc68k_reduced.h5ad
```

```bash
single-cell-agent metadata --adata data/10x_pbmc68k_reduced.h5ad
```

```bash
single-cell-agent plan \
  --adata data/10x_pbmc68k_reduced.h5ad \
  --question "Which marker genes distinguish the annotated PBMC cell types?"
```

## Project Goals

SingleCellAgent aims to:

* Convert natural-language biological questions into structured single-cell analysis plans
* Run reproducible Scanpy workflows on `AnnData` objects
* Validate metadata, sample structure, and comparison design before analysis
* Support common single-cell tasks including quality control review, differential expression, marker analysis, trajectory-aware exploration, and gene set/module interpretation
* Detect common analysis failure modes such as pseudoreplication, missing biological replicates, confounded metadata, invalid group comparisons, and overinterpretation of UMAPs
* Generate auditable summaries that link biological claims to specific outputs, figures, and statistics
* Provide benchmark tasks for evaluating how well AI systems reason about single-cell datasets

## Why This Matters

Single-cell RNA-seq analysis often requires domain expertise, statistical judgment, and careful interpretation. AI assistants can help accelerate this process, but only if they are connected to deterministic tools, constrained by metadata, and evaluated against realistic biological tasks.

SingleCellAgent explores how agentic AI systems can support real computational biology workflows while reducing hallucinated or unsupported conclusions.

## Planned Features

### Analysis Workflows

* `AnnData` loading and validation
* Metadata inspection and schema checks
* Cell-type composition analysis
* Marker gene discovery
* Pseudobulk differential expression
* Cell-type-specific differential expression
* Gene set and module scoring
* Trajectory-aware exploratory analysis
* Automated report generation

### Agentic Capabilities

* Natural-language question parsing
* Analysis plan generation
* Tool selection and execution
* Intermediate result inspection
* Error detection and recovery
* Evidence-grounded biological summarization
* Caveat and limitation reporting

### Evaluation Tasks

SingleCellAgent will include benchmark tasks for evaluating whether an AI agent can:

* Identify valid and invalid biological comparisons
* Detect missing or insufficient replicate structure
* Choose pseudobulk analysis when appropriate
* Avoid cell-level pseudoreplication
* Interpret UMAPs, marker plots, and differential expression outputs cautiously
* Detect metadata confounding
* Generate biologically plausible hypotheses grounded in the data
* Separate statistical results from speculative interpretation

## Example Use Case

A researcher asks:

> Which immune cell populations show disease-associated transcriptional changes, and are those changes robust across samples?

SingleCellAgent should be able to:

1. Inspect the dataset metadata
2. Identify relevant condition, sample, and cell-type columns
3. Check whether the comparison has biological replicates
4. Recommend an appropriate differential expression strategy
5. Run the analysis using deterministic tools
6. Summarize cell-type-specific results
7. Flag limitations or confounders
8. Generate a reproducible report with code, figures, and evidence-backed interpretations

## Intended Users

SingleCellAgent is intended for:

* Computational biologists
* Single-cell genomics researchers
* Bioinformatics teams
* Biology-focused AI researchers
* Scientists interested in reliable AI-assisted data analysis

## Current Status

This repository is an early-stage prototype. The initial focus is on defining the system architecture, core Scanpy tools, structured task outputs, and evaluation framework.

## Proposed Architecture

```text
User Question
     |
     v
Question Parser
     |
     v
Dataset + Metadata Validator
     |
     v
Analysis Planner
     |
     v
Deterministic Tool Execution
     |
     v
Automated Output Checks
     |
     v
Evidence-Grounded Biological Summary
     |
     v
Reproducible Report
```

## Repository Structure

```text
singlecellagent/
├── README.md
├── requirements.txt
├── pyproject.toml
├── data/
│   └── example/
├── notebooks/
│   └── prototype_demo.ipynb
├── singlecellagent/
│   ├── __init__.py
│   ├── io.py
│   ├── metadata.py
│   ├── planning.py
│   ├── tools/
│   │   ├── qc.py
│   │   ├── markers.py
│   │   ├── differential_expression.py
│   │   └── plotting.py
│   ├── validation/
│   │   ├── checks.py
│   │   └── schemas.py
│   ├── evaluation/
│   │   ├── tasks.py
│   │   └── graders.py
│   └── reporting.py
└── tests/
```

## Example Commands

Planned command-line interface:

```bash
single-cell-agent validate --adata data/example/pbmc.h5ad
```

```bash
single-cell-agent plan \
  --adata data/example/pbmc.h5ad \
  --question "Which cell types differ between control and disease samples?"
```

```bash
single-cell-agent run \
  --adata data/example/pbmc.h5ad \
  --question "Find disease-associated transcriptional changes by cell type" \
  --out results/
```

## Technologies

Planned core stack:

* Python
* Scanpy
* AnnData
* pandas
* NumPy
* SciPy
* statsmodels
* scikit-learn
* matplotlib
* PyTorch
* LLM/tool-use interfaces
* Reproducible workflow utilities

## Design Principles

1. **Deterministic tools over free-form answers**
   Biological claims should come from executable analysis modules, not unsupported text generation.

2. **Metadata-first reasoning**
   The agent should inspect sample, condition, batch, replicate, and cell-type structure before recommending analyses.

3. **Reproducibility by default**
   Outputs should include code, parameters, figures, tables, and provenance.

4. **Cautious biological interpretation**
   The system should distinguish between statistical results, biological interpretation, and speculation.

5. **Evaluation-driven development**
   The agent should be tested on realistic single-cell reasoning tasks, not only toy examples.

## Roadmap

* [ ] Define core `AnnData` validation utilities
* [ ] Implement metadata schema inspection
* [ ] Build deterministic Scanpy tool wrappers
* [ ] Add pseudobulk differential expression workflow
* [ ] Add marker gene and module scoring workflows
* [ ] Build natural-language-to-analysis-plan prototype
* [ ] Generate reproducible HTML/Markdown reports
* [ ] Create benchmark tasks for single-cell reasoning
* [ ] Add automated graders for common workflow errors
* [ ] Release example notebooks and demo dataset

## About

SingleCellAgent is being developed as an independent project by Imtiyaz Hariyani, a PhD candidate in computational biology and genomics. The project reflects an interest in building reliable AI systems for biological data analysis, with a focus on single-cell genomics, reproducible workflows, and evaluation-driven AI development.

## License

MIT License. See `LICENSE` for details.
