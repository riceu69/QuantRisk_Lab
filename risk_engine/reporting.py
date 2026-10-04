"""Report generation utilities."""

from pathlib import Path

import pandas as pd


def write_excel_report(path: str | Path, **tables: pd.DataFrame) -> None:
    """Write analysis tables to a single Excel workbook."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, table in tables.items():
            table.to_excel(writer, sheet_name=name[:31], index=False)


def write_csv_bundle(output_dir: str | Path, **tables: pd.DataFrame) -> None:
    """Write each analysis table to a separate CSV file."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, table in tables.items():
        table.to_csv(output_dir / f"{name}.csv", index=False)
