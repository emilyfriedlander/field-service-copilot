"""Load and preprocess the jobs dataset."""

import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "jobs.csv"


def load_jobs(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["scheduled_date"])
    df["csat_score"] = pd.to_numeric(df["csat_score"], errors="coerce")
    df["first_time_fix"] = df["first_time_fix"].astype(bool)
    df["revisit_required"] = df["revisit_required"].astype(bool)
    return df


def summary_stats(df: pd.DataFrame) -> dict:
    completed = df[df["status"] == "Completed"]
    return {
        "total_jobs": len(df),
        "completed": len(completed),
        "completion_rate": round(len(completed) / len(df), 3),
        "avg_csat": round(completed["csat_score"].mean(), 2),
        "ftf_rate": round(df["first_time_fix"].mean(), 3),
        "avg_job_value": round(df["total_cost_usd"].mean(), 2),
        "total_revenue": round(df["total_cost_usd"].sum(), 2),
    }
