# XLcli-ai — Natural Language Excel Query CLI

[![PyPI version](https://img.shields.io/pypi/v/xlcli-ai.svg)](https://pypi.org/project/xlcli-ai/)
[![Downloads](https://pypi.org/project/xlcli-ai/)
[![License](https://img.shields.io/github/license/ammarkaskar/xlcli-ai)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/ammarkaskar/xlcli-ai?style=social)](https://github.com/ammarkaskar/xlcli-ai)

Query Excel spreadsheets using **plain English directly from your terminal**.

XLcli converts natural language questions into SQL queries and runs them on your Excel file.

Powered by **Groq + Llama 3.3**.

---

# ✨ Features

• Query Excel files using natural language
• AI converts questions → SQL automatically
• Interactive chat mode for exploring data
• Dataset insights and statistics
• Clean terminal tables using `tabulate`
• Works locally with your Excel files

---

# 📦 Installation

Install from PyPI:

```
pip install xlcli-ai
```

---

# 🚀 Quick Start

Ask a question about your Excel file:

```
xlcli ask sales.xlsx "highest sales"
```

Start interactive chat mode:

```
xlcli chat sales.xlsx
```

View dataset insights:

```
xlcli insights sales.xlsx
```

View the spreadsheet:

```
xlcli view sales.xlsx
```

---

# 💻 Example

### Ask a question

```
xlcli ask sales.xlsx "highest sales"
```

Output:

```
Generated SQL:
SELECT Name, Sales FROM df ORDER BY Sales DESC LIMIT 1

Result:

┌────────┬───────┐
│ Name   │ Sales │
├────────┼───────┤
│ Ammar  │ 523   │
└────────┴───────┘
```

---

# 💬 Chat Mode

```
xlcli chat sales.xlsx
```

Example:

```
> name and department

Alice   Sales
Bob     Engineering
Carol   Sales
David   Marketing
...
```

Type `exit` to quit chat mode.

---

# 📊 Dataset Insights

```
xlcli insights sales.xlsx
```

Example output:

```
Sales:
Highest : 523 (Ammar)
Average : 315.73
Lowest  : 95 (Eve)
```

Includes:

• column statistics
• department distribution
• region distribution

---

# 🧠 How It Works

1. Load Excel file with **pandas**
2. Convert natural language → SQL via **Groq LLM**
3. Execute SQL query on the dataframe
4. Display results in terminal tables

---

# 🛠 Project Structure

```
xlcli-ai
│
├── xlcli
│   ├── __init__.py
│   ├── main.py
│   ├── cli.py
│   ├── ai_query.py
│   ├── query_engine.py
│   └── insights.py
│
├── pyproject.toml
├── README.md
├── requirements.txt
└── sales.xlsx
```

---

# 📈 Roadmap

* [ ] Data cleaning command
* [ ] Chart generation
* [ ] Multiple sheet support
* [ ] Streaming query results

---

# 🤝 Contributing

Pull requests are welcome.

Steps:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

# 📜 License

MIT License

---

# 👨‍💻 Author

**Ammar Kaskar**

GitHub:
https://github.com/ammarkaskar

---

⭐ If you like this project, consider giving it a star!
