"""
query_engine.py
Executes SQL queries against a pandas DataFrame and formats the results.

Strategy:
  1. Try pandasql (sqldf) — most idiomatic for pandas.
  2. Fall back to sqlite3 in-memory DB — always available in stdlib.
"""

from __future__ import annotations

import sqlite3
import pandas as pd
from tabulate import tabulate


# ── SQL Execution ─────────────────────────────────────────────────────────────

def _run_via_pandasql(sql: str, df: pd.DataFrame) -> pd.DataFrame:
    """Execute SQL with pandasql if installed."""
    from pandasql import sqldf  # noqa: PLC0415

    env = {"df": df}
    result = sqldf(sql, env)
    return result


def _run_via_sqlite3(sql: str, df: pd.DataFrame) -> pd.DataFrame:
    """Execute SQL using an in-memory SQLite database."""
    con = sqlite3.connect(":memory:")
    try:
        df.to_sql("df", con, index=False, if_exists="replace")
        result = pd.read_sql_query(sql, con)
    finally:
        con.close()
    return result


def run_sql_on_dataframe(sql: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Execute a SQL SELECT statement against *df*.

    Tries pandasql first; if not installed, falls back to sqlite3.

    Args:
        sql:  A SQL SELECT query; the table name must be 'df'.
        df:   The source DataFrame.

    Returns:
        A new DataFrame with the query results.

    Raises:
        Exception: Propagates any SQL execution error after the fallback.
    """
    try:
        return _run_via_pandasql(sql, df)
    except ImportError:
        pass  # pandasql not installed → use sqlite3 fallback
    except Exception:
        raise  # pandasql is installed but the query itself failed

    return _run_via_sqlite3(sql, df)


# ── Result Formatting ─────────────────────────────────────────────────────────

def format_results(df: pd.DataFrame, tablefmt: str = "rounded_outline") -> str:
    """
    Format a DataFrame as a terminal-friendly table using tabulate.

    Args:
        df:        The DataFrame to format.
        tablefmt:  Any tabulate table format string (default: rounded_outline).

    Returns:
        A formatted string ready to print.
    """
    return tabulate(
        df,
        headers="keys",
        tablefmt=tablefmt,
        showindex=False,
        numalign="right",
        stralign="left",
    )
