# xlcli-ai  — Natural Language Excel Querying CLI

Query any Excel spreadsheet using plain English, powered by Groq.

---

## Features

- Load `.xlsx` files with pandas
- Convert natural language questions to SQL via Groq (`groq2o`)
- Execute SQL using pandasql (or falls back to stdlib `sqlite3` automatically)
- Display results in a clean terminal table via tabulate
- Graceful error handling and helpful hints

---

## Project Structure

```
xlcli/
├── main.py          # Entry point
├── cli.py           # Click CLI commands & options
├── ai_query.py      # Natural language → SQL via OpenAI API
├── query_engine.py  # SQL execution on DataFrames + result formatting
├── sample_data.py   # Script to generate sample sales.xlsx
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Clone / copy the project

```bash
cd xlcli-ai
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate.bat     # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> `pandasql` is optional. If it's not installed, xlcli automatically falls back  
> to Python's built-in `sqlite3` — no action needed.

### 4. Set your Groq API key

```bash
export GROQ_API_KEY="your_groq_api_key"          # macOS / Linux
set GROQ_API_KEY=your_groq_api_key               # Windows CMD
$env:GROQ_API_KEY="your_groq_api_key"            # Windows PowerShell
```

Or pass it inline with `--api-key`.

---

## Generate the Sample Dataset

```bash
python sample_data.py
```

This creates `sales.xlsx` with 10 rows covering Name, Department, Age, Sales,
Region, Years\_Experience, and Rating columns.

---

## Usage

```
python main.py ask <EXCEL_FILE> "<QUESTION>" [OPTIONS]
```

### Options

| Flag | Description |
|------|-------------|
| `--api-key TEXT` | OpenAI API key (overrides env var) |
| `--sheet TEXT/INT` | Sheet name or 0-based index (default: 0) |
| `--no-sql` | Suppress the generated SQL output |
| `--help` | Show help message |

---

## Examples

```bash
# Who has the highest sales?
python main.py ask sales.xlsx "Who has the highest sales?"

# Employees older than 25
python main.py ask sales.xlsx "Show employees older than 25"

# Average sales
python main.py ask sales.xlsx "What is the average sales?"

# Top 3 salespeople by region
python main.py ask sales.xlsx "Show the top 3 salespeople in the North region"

# Department summary
python main.py ask sales.xlsx "What is the total sales per department?"

# Use a specific sheet
python main.py ask report.xlsx "Summarise revenue by quarter" --sheet "Q1"

# Hide the SQL output
python main.py ask sales.xlsx "Who has the lowest rating?" --no-sql
```

---

## Example Output

```
📂  Loading sales.xlsx …
✅  Loaded 10 rows × 7 columns (Name, Department, Age, Sales, Region…)

🤖  Asking AI to generate SQL …

────────────────────────────────────────────────────────────
Generated SQL:
SELECT Name, Sales FROM df ORDER BY Sales DESC LIMIT 1
────────────────────────────────────────────────────────────

────────────────────────────────────────────────────────────
Result:
╭───────┬───────╮
│ Name  │ Sales │
├───────┼───────┤
│ Frank │   520 │
╰───────┴───────╯
────────────────────────────────────────────────────────────

1 row(s) returned.
```

---

## Error Handling

| Situation | Behaviour |
|-----------|-----------|
| Missing API key | Clear error message with instructions |
| Corrupt / missing Excel file | Descriptive error, non-zero exit |
| AI returns invalid SQL | Error shown; user prompted to rephrase |
| Query returns no rows | Friendly "no results" message |
| `pandasql` not installed | Silent fallback to `sqlite3` |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `pandas` | Load and manipulate Excel data |
| `openpyxl` | Excel file backend for pandas |
| `openai` | Call GPT to generate SQL |
| `tabulate` | Pretty-print results in the terminal |
| `click` | Build the CLI interface |
| `pandasql` *(optional)* | Run SQL on DataFrames (falls back to sqlite3) |

---

## Tips

- Column names with spaces are automatically converted to underscores  
  (`Sales Amount` → `Sales_Amount`) so SQL works cleanly.
- The AI always uses `gpt-4o-mini` (fast + cheap). Change `model=` in  
  `ai_query.py` if you prefer `gpt-4o` for more complex queries.
- Keep questions specific for best SQL generation accuracy.
