import os
import json
from typing import Dict, Any, List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def basic_stats(df: pd.DataFrame) -> Dict[str, Any]:
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

    stats = {
        "n_rows": int(df.shape[0]),
        "n_cols": int(df.shape[1]),
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "nulls_per_column": df.isna().sum().sort_values(ascending=False).to_dict(),
        "sample_head": df.head(5).to_dict(orient="list"),
        "describe_numeric": df[numeric_cols].describe().to_dict() if numeric_cols else {},
    }
    return stats


def save_json(obj: Dict[str, Any], filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def plot_missingness(df: pd.DataFrame, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    missing = df.isna().mean().sort_values(ascending=False)
    plt.figure(figsize=(10, max(3, len(missing) * 0.25)))
    missing.plot(kind="bar")
    plt.title("Udział braków danych w kolumnach")
    plt.ylabel("Proporcja braków")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def correlation_heatmap(df: pd.DataFrame, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    num = df.select_dtypes(include=[np.number])
    if num.shape[1] == 0:
        return
    corr = num.corr(numeric_only=True)
    plt.figure(figsize=(min(1.2 * corr.shape[1], 16), min(1.2 * corr.shape[0], 12)))
    sns.heatmap(corr, cmap="coolwarm", center=0, square=False)
    plt.title("Mapa korelacji (kolumny numeryczne)")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def numeric_distributions(df: pd.DataFrame, out_dir: str, max_cols: int = 30) -> List[str]:
    os.makedirs(out_dir, exist_ok=True)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()[:max_cols]
    paths = []
    for col in num_cols:
        plt.figure(figsize=(7, 4))
        sns.histplot(df[col].dropna(), kde=True)
        plt.title(f"Rozkład: {col}")
        plt.tight_layout()
        p = os.path.join(out_dir, f"{col}.png")
        plt.savefig(p)
        plt.close()
        paths.append(p)
    return paths


def categorical_counts(df: pd.DataFrame, out_dir: str, top_n: int = 20, max_cols: int = 30) -> List[str]:
    os.makedirs(out_dir, exist_ok=True)
    cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()[:max_cols]
    paths = []
    for col in cat_cols:
        vc = df[col].astype("string").fillna("<NA>").value_counts().head(top_n)
        plt.figure(figsize=(8, 5))
        sns.barplot(x=vc.values, y=vc.index)
        plt.title(f"Top {top_n} wartości: {col}")
        plt.xlabel("Liczność")
        plt.ylabel(col)
        plt.tight_layout()
        p = os.path.join(out_dir, f"{col}.png")
        plt.savefig(p)
        plt.close()
        paths.append(p)
    return paths


def make_eda_report(stats: Dict[str, Any],
                    paths: Dict[str, str],
                    outfile_md: str) -> None:

    os.makedirs(os.path.dirname(outfile_md), exist_ok=True)

    numeric_cols = stats.get("numeric_cols", [])
    categorical_cols = stats.get("categorical_cols", [])
    nulls = stats.get("nulls_per_column", {})

    lines = []
    lines.append("# Raport EDA\n")
    lines.append(f"- Wiersze: **{stats['n_rows']}**, Kolumny: **{stats['n_cols']}**\n")
    lines.append(f"- Kolumny numeryczne ({len(numeric_cols)}): {', '.join(numeric_cols) if numeric_cols else '-'}")
    lines.append(f"- Kolumny kategoryczne ({len(categorical_cols)}): {', '.join(categorical_cols) if categorical_cols else '-'}\n")

    lines.append("## Braki danych")
    if any(v > 0 for v in nulls.values()):
        lines.append(f"Zobacz wykres: `{paths.get('missing_png','')}`")
    else:
        lines.append("Brak braków danych w kolumnach.")
    lines.append("")

    if numeric_cols:
        lines.append("## Korelacje (numeryczne)")
        lines.append(f"Mapa korelacji: `{paths.get('corr_png','')}`\n")

        lines.append("## Rozkłady zmiennych numerycznych")
        lines.append(f"Folder: `{paths.get('num_dir','')}`\n")

    if categorical_cols:
        lines.append("## Rozkłady zmiennych kategorycznych")
        lines.append(f"Folder: `{paths.get('cat_dir','')}`\n")

    lines.append("## Wskazówki do dalszych kroków")
    lines.append("- Uzupełnienie/obsługa braków danych (medianą/modą lub imputacją wielowymiarową).")
    lines.append("- Standaryzacja/normalizacja kolumn numerycznych.")
    lines.append("- Enkodowanie zmiennych kategorycznych (One-Hot/Target Encoding).")
    lines.append("- Usunięcie lub transformacja outlierów (np. winsoryzacja).")
    lines.append("")

    with open(outfile_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
