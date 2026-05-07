"""Field service reporting copilot — Claude-powered Q&A with DataFrame tool use."""

import json
import os
import traceback
import anthropic
import pandas as pd
from dotenv import load_dotenv
from data_loader import load_jobs, summary_stats

load_dotenv()


def _get_api_key() -> str | None:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    try:
        import streamlit as st
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return None


CLIENT = anthropic.Anthropic(api_key=_get_api_key())
MODEL = "claude-opus-4-6"

# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "query_dataframe",
        "description": (
            "Run a pandas expression against the jobs DataFrame to answer questions. "
            "The variable `df` is pre-loaded with all 1,200 job records. "
            "Return any valid pandas expression: groupby, filter, value_counts, sort_values, etc. "
            "The result will be converted to a string and returned to you. "
            "Available columns: job_id, scheduled_date, trade, job_type, priority, status, "
            "technician_id, technician_name, technician_level, customer_type, city, state, "
            "equipment_involved, reported_issue, labor_hours, labor_rate_usd, labor_cost_usd, "
            "parts_cost_usd, total_cost_usd, payment_method, first_time_fix, csat_score, "
            "revisit_required, notes. "
            "Dtypes: scheduled_date is datetime64, csat_score is float (NaN when not completed), "
            "first_time_fix and revisit_required are bool."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": (
                        "A single pandas expression using `df`. "
                        "Examples: "
                        "\"df.groupby('technician_name')['first_time_fix'].mean().sort_values(ascending=False)\" "
                        "\"df[df['revisit_required']]['job_type'].value_counts().head(10)\" "
                        "\"df.groupby('trade')[['total_cost_usd','csat_score']].agg({'total_cost_usd':'sum','csat_score':'mean'})\""
                    ),
                }
            },
            "required": ["expression"],
        },
    }
]


# ---------------------------------------------------------------------------
# Tool execution
# ---------------------------------------------------------------------------

def run_query(expression: str, df: pd.DataFrame) -> str:
    try:
        result = eval(expression, {"df": df, "pd": pd})  # noqa: S307
        if isinstance(result, pd.DataFrame):
            return result.to_string()
        if isinstance(result, pd.Series):
            return result.to_string()
        return str(result)
    except Exception:
        return f"Error executing expression:\n{traceback.format_exc()}"


# ---------------------------------------------------------------------------
# Agentic loop
# ---------------------------------------------------------------------------

def build_system_prompt(df: pd.DataFrame) -> str:
    stats = summary_stats(df)
    return (
        "You are a field service operations analyst for Apex Home Services, "
        "a residential and commercial HVAC, plumbing, and electrical company.\n\n"
        f"The jobs dataset has {stats['total_jobs']} work orders spanning 2024–2025.\n"
        f"Overall metrics: completion rate {stats['completion_rate']:.1%}, "
        f"avg CSAT {stats['avg_csat']}/5, FTF rate {stats['ftf_rate']:.1%}, "
        f"avg job value ${stats['avg_job_value']}, total revenue ${stats['total_revenue']:,.2f}.\n\n"
        "Use the query_dataframe tool to look up exact numbers before answering. "
        "Be specific, cite numbers, flag performance concerns, and suggest actionable improvements."
    )


def ask(question: str, df: pd.DataFrame = None) -> str:
    if df is None:
        df = load_jobs()

    messages = [{"role": "user", "content": question}]

    while True:
        response = CLIENT.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=build_system_prompt(df),
            tools=TOOLS,
            messages=messages,
        )

        # Append assistant turn
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Return the final text block
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    output = run_query(block.input["expression"], df)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": output,
                    })
            messages.append({"role": "user", "content": tool_results})


# ---------------------------------------------------------------------------
# CLI demo
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# RAG-powered training assistant
# ---------------------------------------------------------------------------

def ask_training(question: str) -> tuple[str, list[dict]]:
    """Answer an HVAC technical question using retrieved knowledge base chunks.

    Returns (answer_text, source_chunks) so the UI can show citations.
    """
    from retriever import retrieve, format_context

    chunks  = retrieve(question, n_results=4)
    context = format_context(chunks)

    system = (
        "You are an expert HVAC training assistant for Apex Home Services. "
        "Answer the technician's question using ONLY the context provided below. "
        "Be precise and practical — technicians need clear, actionable answers in the field. "
        "If the context doesn't contain enough information to answer fully, say so clearly "
        "rather than guessing. Cite the source document name when referencing specific facts.\n\n"
        f"CONTEXT:\n{context}"
    )

    response = CLIENT.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text, chunks


if __name__ == "__main__":
    df = load_jobs()
    questions = [
        "Which technician has the highest first-time fix rate?",
        "What trade generates the most revenue?",
        "Which job types have the most revisits?",
    ]
    for q in questions:
        print(f"\nQ: {q}")
        print(f"A: {ask(q, df)}")
        print("-" * 60)
