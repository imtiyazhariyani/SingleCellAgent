import os
from typing import List, Dict, Any

import anthropic

from single_cell_agent.tool_registry import SingleCellToolRegistry, tool_result_to_json


SYSTEM_PROMPT = """
You are SingleCellAgent, an AI-guided single-cell genomics analysis assistant.

Your job is to help analyze AnnData single-cell datasets using deterministic tools.
You must not invent results. Biological claims must be grounded in tool outputs.

Important principles:
1. Validate the dataset before recommending analysis.
2. Inspect metadata before choosing comparisons.
3. Check sample, condition, cell-type, and batch structure.
4. Prefer sample-aware or pseudobulk reasoning for differential expression.
5. Flag insufficient replicates, missing metadata, and confounded designs.
6. Distinguish statistical results from biological interpretation.
7. Use cautious language when evidence is incomplete.
8. When appropriate, write a report using the write_report tool.

You have access to tools that inspect and analyze an AnnData object.
Use the tools to investigate before giving a final answer.
"""


def run_single_cell_agent(
    adata_path: str,
    question: str,
    output_dir: str = "results",
    model: str | None = None,
    max_turns: int = 8,
) -> str:
    """
    Run a Claude tool-use agent over a single-cell AnnData dataset.
    """
    model = model or os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")

    client = anthropic.Anthropic()
    registry = SingleCellToolRegistry(
        adata_path=adata_path,
        question=question,
        output_dir=output_dir,
    )

    messages: List[Dict[str, Any]] = [
        {
            "role": "user",
            "content": (
                f"Dataset path: {adata_path}\n\n"
                f"User biological question:\n{question}\n\n"
                "Analyze this dataset using available tools. "
                "Start by validating the dataset and inspecting metadata. "
                "Then decide which analysis steps are appropriate."
            ),
        }
    ]

    final_text = ""

    for turn in range(max_turns):
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=registry.tool_definitions(),
            messages=messages,
        )

        messages.append(
            {
                "role": "assistant",
                "content": response.content,
            }
        )

        tool_uses = [block for block in response.content if block.type == "tool_use"]

        # If Claude did not call a tool, this is the final answer.
        if not tool_uses:
            text_blocks = [block.text for block in response.content if block.type == "text"]
            final_text = "\n".join(text_blocks)
            break

        tool_results = []

        for tool_use in tool_uses:
            result = registry.run_tool(
                name=tool_use.name,
                tool_input=tool_use.input,
            )

            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": tool_result_to_json(result),
                }
            )

        messages.append(
            {
                "role": "user",
                "content": tool_results,
            }
        )

    if not final_text:
        final_text = (
            "Agent reached the maximum number of turns before producing a final response. "
            f"Check output directory: {output_dir}"
        )

    return final_text
