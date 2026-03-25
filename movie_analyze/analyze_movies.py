# -*- coding: utf-8 -*-
"""
tmdb_5000_movies.csv の読み込み・集計・可視化

使い方:
  pip install -r requirements.txt
  python analyze_movies.py

出力: figures/ に PNG を保存
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# --- パス ---
BASE = Path(__file__).resolve().parent
CSV_PATH = BASE / "tmdb_5000_movies.csv"
FIG_DIR = BASE / "figures"

# --- 日本語表示（macOS 想定。表示が崩れる場合はフォントを環境に合わせて変更） ---
plt.rcParams["font.family"] = ["Hiragino Sans", "Hiragino Kaku Gothic ProN", "Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

sns.set_theme(style="whitegrid", font=plt.rcParams["font.family"][0])


def load_movies(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["year"] = df["release_date"].dt.year
    return df


def genre_names_from_cell(cell: str) -> list[str]:
    if pd.isna(cell) or str(cell).strip() == "":
        return []
    try:
        items = json.loads(cell)
    except (json.JSONDecodeError, TypeError):
        return []
    return [x.get("name", "") for x in items if isinstance(x, dict)]


def explode_genres(df: pd.DataFrame) -> pd.DataFrame:
    """1行1ジャンルに展開した DataFrame（title などを保持）"""
    rows = []
    for _, r in df.iterrows():
        for g in genre_names_from_cell(r["genres"]):
            if g:
                rows.append({"title": r["title"], "genre": g, "year": r["year"], "vote_average": r["vote_average"]})
    return pd.DataFrame(rows)


def print_summary(df: pd.DataFrame) -> None:
    print("=== 基本情報 ===")
    print(f"行数: {len(df):,}")
    print(f"列: {list(df.columns)}")
    print()
    print("=== 数値列の要約 ===")
    num_cols = ["budget", "revenue", "runtime", "vote_average", "vote_count", "popularity"]
    print(df[num_cols].describe().round(2).to_string())
    print()
    print(f"公開年の範囲（欠損除く）: {df['year'].min():.0f} ～ {df['year'].max():.0f}")


def plot_budget_vs_revenue(df: pd.DataFrame, out: Path) -> None:
    """予算と興行収入（0より大きいもののみ）"""
    d = df[(df["budget"] > 0) & (df["revenue"] > 0)].copy()
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.scatterplot(data=d, x="budget", y="revenue", alpha=0.35, ax=ax)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("予算（対数スケール）")
    ax.set_ylabel("興行収入（対数スケール）")
    ax.set_title("予算 vs 興行収入（budget>0, revenue>0）")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_genre_bar(genre_df: pd.DataFrame, out: Path, top_n: int = 15) -> None:
    counts = genre_df["genre"].value_counts().head(top_n)
    fig, ax = plt.subplots(figsize=(10, 6))
    counts.sort_values().plot(kind="barh", ax=ax, color="steelblue")
    ax.set_xlabel("本数")
    ax.set_ylabel("ジャンル")
    ax.set_title(f"ジャンル別映画本数（上位 {top_n}）")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_movies_per_year(df: pd.DataFrame, out: Path) -> None:
    y = df.dropna(subset=["year"])
    yearly = y.groupby("year").size()
    # 極端に古い／未来の年はノイズになりやすいので例として 1920–2020 に絞る
    yearly = yearly.loc[(yearly.index >= 1920) & (yearly.index <= 2020)]
    fig, ax = plt.subplots(figsize=(11, 5))
    yearly.plot(ax=ax, color="darkgreen", linewidth=1.2)
    ax.set_xlabel("公開年")
    ax.set_ylabel("本数")
    ax.set_title("年別の映画本数（1920–2020）")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_vote_average_hist(df: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    d = df[df["vote_count"] >= 50]  # 票数が少ない極端値を軽く除外
    sns.histplot(d["vote_average"], bins=40, kde=True, ax=ax, color="coral")
    ax.set_xlabel("平均評価（vote_average）")
    ax.set_ylabel("本数")
    ax.set_title("評価の分布（vote_count ≥ 50）")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_runtime_hist(df: pd.DataFrame, out: Path) -> None:
    d = df.dropna(subset=["runtime"])
    d = d[(d["runtime"] > 0) & (d["runtime"] < 400)]
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(d["runtime"], bins=50, kde=True, ax=ax, color="mediumpurple")
    ax.set_xlabel("上映時間（分）")
    ax.set_ylabel("本数")
    ax.set_title("上映時間の分布")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def main() -> None:
    if not CSV_PATH.exists():
        raise SystemExit(f"CSV が見つかりません: {CSV_PATH}")

    FIG_DIR.mkdir(exist_ok=True)

    df = load_movies(CSV_PATH)
    print_summary(df)

    genre_df = explode_genres(df)
    print()
    print("=== ジャンル出現回数（上位10） ===")
    top_genres = Counter(genre_df["genre"]).most_common(10)
    for name, c in top_genres:
        print(f"  {name}: {c}")

    plot_budget_vs_revenue(df, FIG_DIR / "budget_vs_revenue.png")
    plot_genre_bar(genre_df, FIG_DIR / "genres_top.png")
    plot_movies_per_year(df, FIG_DIR / "movies_per_year.png")
    plot_vote_average_hist(df, FIG_DIR / "vote_average_hist.png")
    plot_runtime_hist(df, FIG_DIR / "runtime_hist.png")

    print()
    print(f"図を保存しました: {FIG_DIR}")


if __name__ == "__main__":
    main()
