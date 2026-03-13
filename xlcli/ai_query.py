"""
ai_query.py
Converts natural language questions into SQL queries using the Groq API.
"""

import os
from groq import Groq


def build_schema_description(df) -> str:
    """Build a compact schema description from a DataFrame for the prompt."""
    lines = ["Table name: df", "Columns:"]
    for col in df.columns:
        dtype = str(df[col].dtype)
        sample_values = df[col].dropna().head(3).tolist()
        sample_str = ", ".join(str(v) for v in sample_values)
        lines.append(f"  - {col} ({dtype}) — e.g. {sample_str}")
    return "\n".join(lines)


def natural_language_to_sql(question: str, df, api_key: str | None = None) -> str:
    """
    Send a natural language question + DataFrame schema to Groq
    and return a SQL SELECT query string.
    """
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError(
            "Groq API key not found. "
            "Set the GROQ_API_KEY environment variable or pass --api-key."
        )

    client = Groq(api_key=key)
    schema = build_schema_description(df)

    system_prompt = (
        "You are a SQL expert. The user will give you a question about a dataset. "
        "You must respond with ONLY a valid SQL SELECT statement — no explanation, "
        "no markdown code fences, no extra text. "
        "The table is always named 'df'. "
        "Use standard SQL syntax compatible with SQLite."
    )

    user_prompt = (
        f"Dataset schema:\n{schema}\n\n"
        f"Question: {question}\n\n"
        "Return only the SQL query."
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        max_tokens=512,
    )

    sql = response.choices[0].message.content.strip()

    # Strip accidental markdown fences the model might still include
    if sql.startswith("```"):
        lines = sql.splitlines()
        sql = "\n".join(
            line for line in lines if not line.startswith("```")
        ).strip()

    if not sql.lower().startswith("select"):
        raise ValueError(f"Model returned an unexpected response:\n{sql}")

    return sql