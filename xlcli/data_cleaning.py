"""Data-cleaning helpers for Excel workbooks."""

from __future__ import annotations

import os

import pandas as pd


def clean_dataframe(
    df: pd.DataFrame,
    *,
    trim_whitespace: bool = True,
    drop_duplicates: bool = False,
    drop_missing: bool = False,
    fill_missing: str | None = None,
) -> pd.DataFrame:
    """Return a cleaned copy of *df* using only the requested operations."""
    cleaned = df.copy()

    if trim_whitespace:
        cleaned.columns = [
            column.strip() if isinstance(column, str) else column
            for column in cleaned.columns
        ]
        for column in cleaned.select_dtypes(include=["object", "string"]).columns:
            cleaned[column] = cleaned[column].map(
                lambda value: value.strip() if isinstance(value, str) else value
            )

    if drop_duplicates:
        cleaned = cleaned.drop_duplicates()
    if drop_missing:
        cleaned = cleaned.dropna()
    if fill_missing is not None:
        cleaned = cleaned.fillna(fill_missing)

    return cleaned


def clean_workbook(
    excel_file: str,
    *,
    sheet: str | int = 0,
    output: str | None = None,
    trim_whitespace: bool = True,
    drop_duplicates: bool = False,
    drop_missing: bool = False,
    fill_missing: str | None = None,
) -> tuple[str, int, int]:
    """Clean one worksheet and save all workbook sheets to a new .xlsx file."""
    if not os.path.isfile(excel_file):
        raise FileNotFoundError(f"Excel file not found: {excel_file}")

    output_file = output or os.path.splitext(excel_file)[0] + "_cleaned.xlsx"
    if os.path.abspath(output_file) == os.path.abspath(excel_file):
        raise ValueError("Output must be a different file so the original stays unchanged.")
    if os.path.splitext(output_file)[1].lower() != ".xlsx":
        raise ValueError("Output must use the .xlsx extension.")

    with pd.ExcelFile(excel_file) as workbook:
        if isinstance(sheet, int):
            if sheet < 0 or sheet >= len(workbook.sheet_names):
                raise ValueError(
                    f"Sheet index {sheet} is out of range; workbook has "
                    f"{len(workbook.sheet_names)} sheet(s)."
                )
            selected_sheet = workbook.sheet_names[sheet]
        else:
            selected_sheet = sheet
            if selected_sheet not in workbook.sheet_names:
                raise ValueError(
                    f"Sheet '{selected_sheet}' not found. Available sheets: "
                    + ", ".join(workbook.sheet_names)
                )

        selected_before = 0
        selected_after = 0
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            for sheet_name in workbook.sheet_names:
                frame = pd.read_excel(workbook, sheet_name=sheet_name)
                if sheet_name == selected_sheet:
                    selected_before = len(frame)
                    frame = clean_dataframe(
                        frame,
                        trim_whitespace=trim_whitespace,
                        drop_duplicates=drop_duplicates,
                        drop_missing=drop_missing,
                        fill_missing=fill_missing,
                    )
                    selected_after = len(frame)
                frame.to_excel(writer, sheet_name=sheet_name, index=False)

    return output_file, selected_before, selected_after
