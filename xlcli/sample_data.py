"""
sample_data.py
Generates a sample sales.xlsx dataset for testing xlcli.

Run:
    python sample_data.py
"""

import pandas as pd

data = {
    "Name": [
        "Alice", "Bob", "Carol", "David", "Eve",
        "Frank", "Grace", "Hank", "Ivy", "Jack",
    ],
    "Department": [
        "Sales", "Engineering", "Sales", "Marketing", "Engineering",
        "Sales", "Marketing", "Engineering", "Sales", "Marketing",
    ],
    "Age": [28, 35, 42, 31, 26, 45, 38, 29, 33, 41],
    "Sales": [450, 120, 390, 210, 95, 520, 300, 180, 410, 275],
    "Region": [
        "North", "South", "East", "West", "North",
        "South", "East", "West", "North", "South",
    ],
    "Years_Experience": [3, 10, 15, 6, 2, 20, 12, 4, 8, 16],
    "Rating": [4.5, 3.8, 4.2, 3.5, 3.1, 4.8, 4.0, 3.6, 4.3, 3.9],
}

df = pd.DataFrame(data)
df.to_excel("sales.xlsx", index=False)
print("✅  sales.xlsx created successfully.")
print(df.to_string(index=False))
