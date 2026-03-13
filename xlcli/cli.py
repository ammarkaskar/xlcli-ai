"""
cli.py
Defines the Click-based CLI interface for xlcli.
"""

import sys
import os
import click
import pandas as pd
import colorama
from colorama import Fore, Style

# Initialize colorama - required for Windows CMD color support
colorama.init(autoreset=True)

from .ai_query import natural_language_to_sql
from .query_engine import run_sql_on_dataframe, format_results

VERSION = "1.0.0"
COMMIT  = "a1b2c3d"

BANNER =  r"""
██╗  ██╗██╗      ██████╗██╗     ██╗
╚██╗██╔╝██║     ██╔════╝██║     ██║
 ╚███╔╝ ██║     ██║     ██║     ██║
 ██╔██╗ ██║     ██║     ██║     ██║
██╔╝ ██╗███████╗╚██████╗███████╗██║
╚═╝  ╚═╝╚══════╝ ╚═════╝╚══════╝╚═╝

XLcli — AI Excel CLI
"""


def print_banner():
    print(Fore.CYAN + Style.BRIGHT + BANNER)
    print(Fore.CYAN + Style.BRIGHT + f"  Version {VERSION}  " +
          Fore.WHITE + f"Commit {COMMIT}")
    print()
    print(Fore.WHITE + "  xlcli can query any Excel file using plain English.")
    print(Fore.WHITE + "  Describe what you want and AI generates the SQL for you.")
    print()
    print(Fore.GREEN + "  * Powered by Groq (llama-3.3-70b-versatile)")
    print(Fore.GREEN + "  * AI-generated SQL on your local Excel data")
    print(Fore.GREEN + "  * API Key : Connected")
    print()


def divider(color=Fore.WHITE):
    print(color + "  " + "-" * 58 + Style.RESET_ALL)


def pick_excel(provided_file=None):
    """
    If a file is provided and exists, return it directly.
    Otherwise scan the current directory for .xlsx files
    and show an interactive numbered picker.
    """
    if provided_file and os.path.exists(provided_file):
        return provided_file

    # Scan for Excel files in current directory
    files = sorted([f for f in os.listdir(".") if f.endswith(".xlsx") or f.endswith(".xls")])

    if not files:
        print(Fore.RED + Style.BRIGHT + "  [ERROR] No Excel files found in current directory.")
        print(Fore.YELLOW + "  Make sure your .xlsx file is in: " + os.getcwd())
        sys.exit(1)

    if len(files) == 1:
        print(Fore.GREEN + f"  [AUTO] Using: " + Fore.CYAN + Style.BRIGHT + files[0])
        print()
        return files[0]

    # Show picker
    print(Fore.CYAN + Style.BRIGHT + "  Available Excel files:")
    print()
    for i, f in enumerate(files, 1):
        size_kb = round(os.path.getsize(f) / 1024, 1)
        print(Fore.WHITE + f"    [{i}] " + Fore.CYAN + Style.BRIGHT + f"{f:<30}" +
              Fore.WHITE + f"  {size_kb} KB")
    print()

    while True:
        try:
            choice = input(Fore.CYAN + Style.BRIGHT + "  Select file (1-" +
                           str(len(files)) + "): " + Style.RESET_ALL).strip()
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                selected = files[idx]
                print(Fore.GREEN + Style.BRIGHT + f"  [OK] Selected: " +
                      Fore.CYAN + selected)
                print()
                return selected
            else:
                print(Fore.YELLOW + f"  Please enter a number between 1 and {len(files)}")
        except (ValueError, KeyboardInterrupt):
            print(Fore.RED + "\n  Cancelled.")
            sys.exit(0)


def load_df(excel_file, sheet):
    sheet_param = int(sheet) if str(sheet).isdigit() else sheet
    df = pd.read_excel(excel_file, sheet_name=sheet_param)
    df.columns = [str(c).strip().replace(" ", "_") for c in df.columns]
    return df


def save_df(df, excel_file):
    # Restore underscores back to spaces for saving
    df.columns = [c.replace("_", " ") for c in df.columns]
    df.to_excel(excel_file, index=False)
    df.columns = [c.replace(" ", "_") for c in df.columns]


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """xlcli - Query Excel files with natural language, powered by AI."""
    if ctx.invoked_subcommand is None:
        print_banner()
        print(Fore.CYAN + "  Available commands:")
        print(Fore.WHITE + "    xlcli ask  <file.xlsx> \"question\"  - Query with AI")
        print(Fore.WHITE + "    xlcli edit <file.xlsx>              - Edit the file")
        print(Fore.WHITE + "    xlcli view <file.xlsx>              - View all rows")
        print()


# ─────────────────────────────────────────────────────────────
# ASK command
# ─────────────────────────────────────────────────────────────
@cli.command("ask")
@click.argument("excel_file", required=False, default=None)
@click.argument("question", required=False, default=None)
@click.option("--api-key", envvar="GROQ_API_KEY", default=None)
@click.option("--sheet", default=0, show_default=True)
@click.option("--no-sql", is_flag=True, default=False)
def ask(excel_file, question, api_key, sheet, no_sql):
    """Ask a natural language QUESTION about an EXCEL_FILE."""
    print_banner()
    excel_file = pick_excel(excel_file)
    if not question:
        question = input(Fore.CYAN + Style.BRIGHT + "  Your question: " + Style.RESET_ALL).strip()
        print()

    print(Fore.WHITE + "  Loading " + Fore.CYAN + Style.BRIGHT + excel_file + Fore.WHITE + " ...")
    try:
        df = load_df(excel_file, sheet)
    except Exception as exc:
        print(Fore.RED + Style.BRIGHT + f"\n  [ERROR] Failed to load: {exc}")
        sys.exit(1)

    if df.empty:
        print(Fore.YELLOW + "  [WARN] The sheet is empty.")
        sys.exit(0)

    cols_preview = ", ".join(df.columns[:5]) + ("..." if len(df.columns) > 5 else "")
    print(Fore.GREEN + Style.BRIGHT + "  [OK] " +
          Fore.WHITE + f"{len(df):,} rows x {len(df.columns)} columns ({cols_preview})")
    print()

    print(Fore.WHITE + "  Generating SQL for: " + Fore.CYAN + Style.BRIGHT + f'"{question}"')
    try:
        sql = natural_language_to_sql(question, df, api_key=api_key)
    except Exception as exc:
        print(Fore.RED + Style.BRIGHT + f"\n  [ERROR] {exc}")
        sys.exit(1)

    if not no_sql:
        print()
        divider(Fore.WHITE)
        print(Fore.CYAN + Style.BRIGHT + "  Generated SQL:")
        print(Fore.YELLOW + f"  {sql}")
        divider(Fore.WHITE)

    try:
        result_df = run_sql_on_dataframe(sql, df)
    except Exception as exc:
        print(Fore.RED + Style.BRIGHT + f"\n  [ERROR] Query failed: {exc}")
        print(Fore.YELLOW + "  [TIP] Try rephrasing your question.")
        sys.exit(1)

    if result_df.empty:
        print(Fore.YELLOW + "\n  [WARN] No results returned.")
        sys.exit(0)

    print()
    divider(Fore.GREEN)
    print(Fore.GREEN + Style.BRIGHT + "  Result:")
    print()
    for line in format_results(result_df).splitlines():
        print(Fore.WHITE + f"  {line}")
    print()
    divider(Fore.GREEN)
    print(Fore.GREEN + Style.BRIGHT + f"  [OK] {len(result_df):,} row(s) returned.\n")


# ─────────────────────────────────────────────────────────────
# VIEW command
# ─────────────────────────────────────────────────────────────
@cli.command("view")
@click.argument("excel_file", required=False, default=None)
@click.option("--sheet", default=0, show_default=True)
def view(excel_file, sheet):
    """View all rows in an EXCEL_FILE."""
    print_banner()
    excel_file = pick_excel(excel_file)

    print(Fore.WHITE + "  Loading " + Fore.CYAN + Style.BRIGHT + excel_file + Fore.WHITE + " ...")
    try:
        df = load_df(excel_file, sheet)
    except Exception as exc:
        print(Fore.RED + Style.BRIGHT + f"\n  [ERROR] {exc}")
        sys.exit(1)

    print(Fore.GREEN + Style.BRIGHT + f"  [OK] {len(df):,} rows x {len(df.columns)} columns\n")
    divider(Fore.CYAN)
    print(Fore.CYAN + Style.BRIGHT + "  Data:")
    print()
    for line in format_results(df).splitlines():
        print(Fore.WHITE + f"  {line}")
    print()
    divider(Fore.CYAN)
    print()


# ─────────────────────────────────────────────────────────────
# EDIT command
# ─────────────────────────────────────────────────────────────
@cli.command("edit")
@click.argument("excel_file", required=False, default=None)
@click.option("--sheet", default=0, show_default=True)
def edit(excel_file, sheet):
    """Interactively edit rows in an EXCEL_FILE from the terminal.

    \b
    Operations:
      add    - Add a new row
      update - Update a value in an existing row
      delete - Delete a row by number
      view   - View current data
      done   - Save and exit
    """
    print_banner()
    excel_file = pick_excel(excel_file)

    print(Fore.WHITE + "  Loading " + Fore.CYAN + Style.BRIGHT + excel_file + Fore.WHITE + " ...")
    try:
        df = load_df(excel_file, sheet)
    except Exception as exc:
        print(Fore.RED + Style.BRIGHT + f"\n  [ERROR] {exc}")
        sys.exit(1)

    print(Fore.GREEN + Style.BRIGHT + f"  [OK] {len(df):,} rows x {len(df.columns)} columns")
    print()
    divider(Fore.CYAN)
    print(Fore.CYAN + Style.BRIGHT + "  Edit Mode  " +
          Fore.WHITE + "| Commands: add / update / delete / view / done")
    divider(Fore.CYAN)
    print()

    # Show current data
    for line in format_results(df).splitlines():
        print(Fore.WHITE + f"  {line}")
    print()

    while True:
        try:
            cmd = input(Fore.CYAN + Style.BRIGHT + "  edit> " + Style.RESET_ALL).strip().lower()
        except (KeyboardInterrupt, EOFError):
            print()
            cmd = "done"

        # ── VIEW ──────────────────────────────────────────────
        if cmd == "view":
            print()
            for line in format_results(df).splitlines():
                print(Fore.WHITE + f"  {line}")
            print()

        # ── ADD ───────────────────────────────────────────────
        elif cmd == "add":
            print(Fore.CYAN + "\n  Enter values for the new row:")
            new_row = {}
            for col in df.columns:
                val = input(Fore.WHITE + f"    {col}: " + Style.RESET_ALL).strip()
                # Try to convert to int or float if possible
                try:
                    val = int(val)
                except ValueError:
                    try:
                        val = float(val)
                    except ValueError:
                        pass
                new_row[col] = val

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            print(Fore.GREEN + Style.BRIGHT + "  [OK] Row added.\n")

        # ── UPDATE ────────────────────────────────────────────
        elif cmd == "update":
            print(Fore.CYAN + f"\n  Row numbers: 0 to {len(df) - 1}")
            try:
                row_num = int(input(Fore.WHITE + "    Row number : " + Style.RESET_ALL).strip())
                if row_num < 0 or row_num >= len(df):
                    print(Fore.RED + f"  [ERROR] Row {row_num} does not exist.\n")
                    continue

                print(Fore.CYAN + f"  Columns: {', '.join(df.columns)}")
                col_name = input(Fore.WHITE + "    Column name: " + Style.RESET_ALL).strip()

                # Match column ignoring case
                matched = next((c for c in df.columns if c.lower() == col_name.lower()), None)
                if not matched:
                    print(Fore.RED + f"  [ERROR] Column '{col_name}' not found.\n")
                    continue

                old_val = df.at[row_num, matched]
                new_val = input(Fore.WHITE + f"    New value (current: {old_val}): " + Style.RESET_ALL).strip()
                try:
                    new_val = int(new_val)
                except ValueError:
                    try:
                        new_val = float(new_val)
                    except ValueError:
                        pass

                df.at[row_num, matched] = new_val
                print(Fore.GREEN + Style.BRIGHT + f"  [OK] Row {row_num}, '{matched}' updated: {old_val} -> {new_val}\n")

            except ValueError:
                print(Fore.RED + "  [ERROR] Please enter a valid row number.\n")

        # ── DELETE ────────────────────────────────────────────
        elif cmd == "delete":
            print(Fore.CYAN + f"\n  Row numbers: 0 to {len(df) - 1}")
            try:
                row_num = int(input(Fore.WHITE + "    Row number to delete: " + Style.RESET_ALL).strip())
                if row_num < 0 or row_num >= len(df):
                    print(Fore.RED + f"  [ERROR] Row {row_num} does not exist.\n")
                    continue

                row_preview = df.iloc[row_num].to_dict()
                confirm = input(Fore.YELLOW + f"    Delete row {row_num} {row_preview}? (y/n): " + Style.RESET_ALL).strip().lower()
                if confirm == "y":
                    df = df.drop(index=row_num).reset_index(drop=True)
                    print(Fore.GREEN + Style.BRIGHT + f"  [OK] Row {row_num} deleted.\n")
                else:
                    print(Fore.WHITE + "  Cancelled.\n")

            except ValueError:
                print(Fore.RED + "  [ERROR] Please enter a valid row number.\n")

        # ── DONE ─────────────────────────────────────────────
        elif cmd == "done":
            try:
                save_df(df, excel_file)
                print(Fore.GREEN + Style.BRIGHT + f"\n  [OK] Saved to {excel_file}")
                print(Fore.WHITE + f"  {len(df):,} rows written.\n")
            except Exception as exc:
                print(Fore.RED + Style.BRIGHT + f"\n  [ERROR] Could not save: {exc}\n")
            break

        else:
            print(Fore.YELLOW + "  [?] Unknown command. Use: add / update / delete / view / done\n")


# ─────────────────────────────────────────────────────────────
# INSIGHTS command
# ─────────────────────────────────────────────────────────────
@cli.command("insights")
@click.argument("excel_file", required=False, default=None)
@click.option("--sheet", default=0, show_default=True)
def insights(excel_file, sheet):
    """Show smart data insights for an EXCEL_FILE.

    \b
    Example:
      python main.py insights sales.xlsx
    """
    print_banner()
    excel_file = pick_excel(excel_file)

    print(Fore.WHITE + "  Loading " + Fore.CYAN + Style.BRIGHT + excel_file + Fore.WHITE + " ...")
    try:
        df = load_df(excel_file, sheet)
    except Exception as exc:
        print(Fore.RED + Style.BRIGHT + f"\n  [ERROR] {exc}")
        sys.exit(1)

    if df.empty:
        print(Fore.YELLOW + "  [WARN] The sheet is empty.")
        sys.exit(0)

    print(Fore.GREEN + Style.BRIGHT + f"  [OK] {len(df):,} rows x {len(df.columns)} columns\n")
    divider(Fore.CYAN)
    print(Fore.CYAN + Style.BRIGHT + "  Dataset Insights")
    divider(Fore.CYAN)
    print()

    # Detect numeric and categorical columns automatically
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols     = df.select_dtypes(include="object").columns.tolist()

    # ── Numeric insights ──────────────────────────────────────
    if numeric_cols:
        # Try to find a "name" column for labelling top/bottom rows
        name_col = next(
            (c for c in df.columns if c.lower() in ("name", "employee", "person", "title", "product")),
            None
        )

        for col in numeric_cols:
            top_row    = df.loc[df[col].idxmax()]
            bottom_row = df.loc[df[col].idxmin()]
            avg_val    = df[col].mean()

            label_top    = f" ({top_row[name_col]})"    if name_col else ""
            label_bottom = f" ({bottom_row[name_col]})" if name_col else ""

            top_val    = top_row[col]
            bottom_val = bottom_row[col]

            # Format nicely
            fmt = lambda v: int(v) if float(v).is_integer() else round(float(v), 2)

            print(Fore.WHITE + f"  {col}:")
            print(Fore.GREEN  + f"    Highest : " + Fore.YELLOW + Style.BRIGHT +
                  f"{fmt(top_val)}{label_top}")
            print(Fore.WHITE  + f"    Average : " + Fore.YELLOW + f"{fmt(avg_val)}")
            print(Fore.RED    + f"    Lowest  : " + Fore.YELLOW +
                  f"{fmt(bottom_val)}{label_bottom}")
            print()

    # ── Categorical distribution ──────────────────────────────
    if cat_cols:
        # Skip name-like columns (too many unique values)
        dist_cols = [
            c for c in cat_cols
            if df[c].nunique() <= 10 and c.lower() not in ("name", "employee", "person")
        ]

        for col in dist_cols:
            divider(Fore.WHITE)
            print(Fore.CYAN + Style.BRIGHT + f"  {col} Distribution:")
            print()
            counts = df[col].value_counts()
            max_count = counts.max()
            for val, count in counts.items():
                bar   = "█" * int((count / max_count) * 20)
                pct   = round(count / len(df) * 100)
                print(Fore.WHITE  + f"    {str(val):<15} " +
                      Fore.CYAN   + f"{bar:<20} " +
                      Fore.YELLOW + f"{count}  " +
                      Fore.WHITE  + f"({pct}%)")
            print()

    divider(Fore.CYAN)
    print(Fore.GREEN + Style.BRIGHT + f"  [OK] Insights complete.\n")


# ─────────────────────────────────────────────────────────────
# CHAT command
# ─────────────────────────────────────────────────────────────
@cli.command("chat")
@click.argument("excel_file", required=False, default=None)
@click.option("--api-key", envvar="GROQ_API_KEY", default=None)
@click.option("--sheet", default=0, show_default=True)
def chat(excel_file, api_key, sheet):
    """Start a chat session to query an EXCEL_FILE conversationally.

    \b
    Example:
      python main.py chat sales.xlsx

    Then type questions naturally:
      > Who is the youngest employee?
      > Show employees with sales above 400
      > What is the average rating?
      > exit
    """
    print_banner()
    excel_file = pick_excel(excel_file)

    print(Fore.WHITE + "  Loading " + Fore.CYAN + Style.BRIGHT + excel_file + Fore.WHITE + " ...")
    try:
        df = load_df(excel_file, sheet)
    except Exception as exc:
        print(Fore.RED + Style.BRIGHT + f"\n  [ERROR] {exc}")
        sys.exit(1)

    if df.empty:
        print(Fore.YELLOW + "  [WARN] The sheet is empty.")
        sys.exit(0)

    cols_preview = ", ".join(df.columns[:5]) + ("..." if len(df.columns) > 5 else "")
    print(Fore.GREEN + Style.BRIGHT + "  [OK] " +
          Fore.WHITE + f"{len(df):,} rows x {len(df.columns)} columns ({cols_preview})")
    print()
    divider(Fore.CYAN)
    print(Fore.CYAN + Style.BRIGHT + "  Chat Mode  " +
          Fore.WHITE + "| Type your question. Type " +
          Fore.YELLOW + "exit" +
          Fore.WHITE + " to quit.")
    divider(Fore.CYAN)
    print()

    history = []   # keep track of Q&A for context display

    while True:
        try:
            question = input(Fore.CYAN + Style.BRIGHT + "  > " + Style.RESET_ALL).strip()
        except (KeyboardInterrupt, EOFError):
            print()
            question = "exit"

        if not question:
            continue

        if question.lower() in ("exit", "quit", "q", "bye"):
            print(Fore.CYAN + Style.BRIGHT + "\n  Goodbye! 👋\n")
            break

        if question.lower() in ("history", "h"):
            if not history:
                print(Fore.YELLOW + "  No history yet.\n")
            else:
                print()
                for i, (q, a) in enumerate(history, 1):
                    print(Fore.CYAN + f"  [{i}] " + Fore.WHITE + q)
                    print(Fore.WHITE + f"      {a}")
                print()
            continue

        if question.lower() in ("clear", "cls"):
            os.system("cls" if os.name == "nt" else "clear")
            print_banner()
            continue

        if question.lower() in ("help", "?"):
            print()
            print(Fore.CYAN + "  Commands:")
            print(Fore.WHITE + "    history  - Show past questions")
            print(Fore.WHITE + "    clear    - Clear the screen")
            print(Fore.WHITE + "    exit     - Quit chat mode")
            print(Fore.WHITE + "    Or just type any question about your data!")
            print()
            continue

        # ── Detect non-data questions locally ────────────────
        non_data_keywords = [
            "how to", "how do", "can i", "edit", "save", "open",
            "install", "run", "command", "use", "what is xlcli",
            "help me", "guide", "tutorial", "explain"
        ]
        if any(kw in question.lower() for kw in non_data_keywords):
            print(Fore.YELLOW + "  [TIP] That looks like a general question, not a data query.")
            print(Fore.WHITE  + "  To edit the file, run:")
            print(Fore.CYAN   + f"    python main.py edit {excel_file}")
            print(Fore.WHITE  + "  To view all data:")
            print(Fore.CYAN   + f"    python main.py view {excel_file}")
            print(Fore.WHITE  + "  Ask me things like: \"Who has the highest sales?\"")
            print()
            continue

        # ── Generate SQL and run ──────────────────────────────
        try:
            sql = natural_language_to_sql(question, df, api_key=api_key)
        except Exception as exc:
            print(Fore.RED + Style.BRIGHT + f"  [ERROR] {exc}\n")
            continue

        try:
            result_df = run_sql_on_dataframe(sql, df)
        except Exception as exc:
            print(Fore.RED + Style.BRIGHT + f"  [ERROR] Query failed: {exc}")
            print(Fore.YELLOW + "  [TIP] Try rephrasing your question.\n")
            continue

        # ── Display result ────────────────────────────────────
        if result_df.empty:
            answer = "No results found."
            print(Fore.YELLOW + f"  {answer}\n")
        elif result_df.shape == (1, 1):
            # Single value — print inline like ChatGPT
            answer = str(result_df.iloc[0, 0])
            print(Fore.GREEN + Style.BRIGHT + f"  {answer}\n")
        elif result_df.shape[1] == 1:
            # Single column — print as a clean list
            items = result_df.iloc[:, 0].tolist()
            answer = ", ".join(str(i) for i in items)
            for item in items:
                print(Fore.GREEN + Style.BRIGHT + f"  {item}")
            print()
        else:
            # Multi-column — print as table
            answer = format_results(result_df)
            print()
            for line in answer.splitlines():
                print(Fore.WHITE + f"  {line}")
            print()

        # Save to history
        history.append((question, answer if len(answer) < 80 else answer[:77] + "..."))