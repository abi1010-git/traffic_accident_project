from pathlib import Path
import re

import matplotlib.pyplot as plt
import pandas as pd


DATA_EXTENSIONS = (".csv", ".xlsx", ".xls")


def find_first_dataset(data_dir):
    """Return the first CSV or Excel dataset found in the data folder."""
    data_dir = Path(data_dir)
    if not data_dir.exists():
        raise FileNotFoundError(f"Data folder does not exist: {data_dir}")

    files = sorted(
        path
        for path in data_dir.iterdir()
        if path.is_file()
        and path.suffix.lower() in DATA_EXTENSIONS
        and not path.name.startswith("~$")
    )

    if not files:
        raise FileNotFoundError(
            f"No CSV or Excel dataset found in {data_dir}. "
            "Add your traffic accident data file to the data folder, then rerun the notebook."
        )

    return files[0]


def load_dataset(path):
    """Load a CSV or Excel dataset into a pandas DataFrame."""
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)

    raise ValueError(f"Unsupported file type: {path.suffix}")


def _normalize_column_name(name):
    name = str(name).strip().lower()
    name = re.sub(r"[^0-9a-zA-Z]+", "_", name)
    return name.strip("_")


def _deduplicate_columns(columns):
    seen = {}
    clean_columns = []

    for column in columns:
        count = seen.get(column, 0)
        clean_columns.append(column if count == 0 else f"{column}_{count + 1}")
        seen[column] = count + 1

    return clean_columns


def clean_column_names(df):
    """Return a copy of df with analysis-friendly column names."""
    cleaned = df.copy()
    cleaned.columns = _deduplicate_columns(
        [_normalize_column_name(column) for column in cleaned.columns]
    )
    return cleaned


def summarize_dataframe(df):
    """Create a compact column summary for data cleaning decisions."""
    summary = pd.DataFrame(
        {
            "dtype": df.dtypes.astype(str),
            "non_null": df.notna().sum(),
            "missing": df.isna().sum(),
            "missing_pct": (df.isna().mean() * 100).round(2),
            "unique": df.nunique(dropna=True),
        }
    )
    return summary.sort_values(["missing_pct", "unique"], ascending=[False, False])


def find_column(df, candidates):
    """Find the first likely matching column from a list of candidate names."""
    columns = list(df.columns)
    normalized_to_original = {_normalize_column_name(column): column for column in columns}

    for candidate in candidates:
        normalized = _normalize_column_name(candidate)
        if normalized in normalized_to_original:
            return normalized_to_original[normalized]

    for candidate in candidates:
        normalized = _normalize_column_name(candidate)
        for column in columns:
            normalized_column = _normalize_column_name(column)
            if normalized in normalized_column or normalized_column in normalized:
                return column

    return None


def plot_top_categories(df, column, top_n=10, title=None):
    """Plot the most common values in a categorical column."""
    counts = (
        df[column]
        .astype("string")
        .fillna("Unknown")
        .value_counts()
        .head(top_n)
        .sort_values()
    )

    ax = counts.plot(kind="barh", figsize=(9, 5), color="#2f6f8f")
    ax.set_title(title or f"Top {top_n} values for {column}")
    ax.set_xlabel("Number of accidents")
    ax.set_ylabel("")
    plt.tight_layout()
    return ax

