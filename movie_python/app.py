# -*- coding: utf-8 -*-
from __future__ import annotations

import io
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Streamlit サーバ側での描画バックエンド問題を回避
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from analyze_movies import genre_names_from_cell, load_movies


BASE = Path(__file__).resolve().parent
CSV_PATH = BASE / "tmdb_5000_movies.csv"

# macOS で日本語が崩れにくいフォント設定（環境で調整してください）
plt.rcParams["font.family"] = [
    "Hiragino Sans",
    "Hiragino Kaku Gothic ProN",
    "Yu Gothic",
    "Meiryo",
    "sans-serif",
]
plt.rcParams["axes.unicode_minus"] = False
sns.set_theme(style="whitegrid", font=plt.rcParams["font.family"][0])

st.set_page_config(page_title="映画分析（TMDB）", layout="wide")
st.title("TMDB 5000 映画データ分析")


def load_and_prepare(csv_bytes):
    """movies_df（映画単位）と genres_long_df（映画×ジャンル単位）を作る。"""
    if csv_bytes is None:
        if not CSV_PATH.exists():
            raise FileNotFoundError(f"CSV が見つかりません: {CSV_PATH}")
        df = load_movies(CSV_PATH)
    else:
        df = pd.read_csv(io.BytesIO(csv_bytes))
        df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
        df["year"] = df["release_date"].dt.year
    df = df.dropna(subset=["year"]).copy()
    df["year"] = df["year"].astype(int)

    # 必要カラムがないと KeyError で落ちるので先に検査する
    required_cols = {"id", "title", "release_date", "genres", "budget", "revenue", "runtime", "vote_average", "vote_count"}
    missing = sorted(required_cols - set(df.columns))
    if missing:
        raise ValueError(f"CSV に必要なカラムが不足しています: {missing}")

    # 数値列を型変換（可視化・集計用）
    for col in ["budget", "revenue", "runtime", "vote_average", "vote_count", "popularity"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # genres を展開して「1行1ジャンル」にする（ジャンル別の絞り込み用）
    df["genres_list"] = df["genres"].apply(genre_names_from_cell)
    df_long = df.explode("genres_list", ignore_index=True).rename(columns={"genres_list": "genre"})
    df_long = df_long.dropna(subset=["genre"]).copy()
    df_long["genre"] = df_long["genre"].astype(str)

    return df, df_long


uploaded = st.sidebar.file_uploader("tmdb_5000_movies.csv（任意）", type=["csv"])
try:
    movies_df, genres_long_df = load_and_prepare(uploaded.getvalue() if uploaded is not None else None)
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

year_min = int(movies_df["year"].min())
year_max = int(movies_df["year"].max())

sidebar = st.sidebar
sidebar.header("フィルター")
year_start, year_end = sidebar.slider(
    "公開年の範囲",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
    step=1,
)

genre_options = sorted(genres_long_df["genre"].unique().tolist())
selected_genre = sidebar.selectbox("ジャンル", ["全ジャンル"] + genre_options, index=0)


def filter_data() -> pd.DataFrame:
    # year 範囲で絞り込み
    base = movies_df[(movies_df["year"] >= year_start) & (movies_df["year"] <= year_end)].copy()

    if selected_genre == "全ジャンル":
        return base

    # ジャンルで絞り込み（同一映画が複数ジャンルを持っていても、指定ジャンルでは1回として扱う）
    long_filtered = genres_long_df[
        (genres_long_df["genre"] == selected_genre)
        & (genres_long_df["year"] >= year_start)
        & (genres_long_df["year"] <= year_end)
    ]
    ids = long_filtered["id"].dropna().unique().tolist()
    return base[base["id"].isin(ids)].copy()


data = filter_data()

col1, col2, col3 = st.columns(3)
col1.metric("映画本数", f"{len(data):,}")

avg_vote = float(data["vote_average"].mean()) if data["vote_average"].notna().any() else float("nan")
col2.metric("平均評価", "-" if pd.isna(avg_vote) else f"{avg_vote:.2f}")

avg_runtime = float(data["runtime"].mean()) if data["runtime"].notna().any() else float("nan")
col3.metric("平均上映時間", "-" if pd.isna(avg_runtime) else f"{avg_runtime:.1f} 分")

st.subheader("グラフ")


def plot_budget_vs_revenue(df: pd.DataFrame) -> None:
    d = df[(df["budget"] > 0) & (df["revenue"] > 0)].copy()
    if d.empty:
        st.info("予算・興行収入がともに 1 以上のデータがありません（選択範囲をご確認ください）。")
        return

    plt.close("all")
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.scatter(d["budget"], d["revenue"], alpha=0.35)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("予算（対数スケール）")
    ax.set_ylabel("興行収入（対数スケール）")
    ax.set_title("予算 vs 興行収入")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def plot_movies_per_year(df: pd.DataFrame) -> None:
    yearly = df.groupby("year").size().sort_index()
    if yearly.empty:
        st.info("年別集計に使えるデータがありません。")
        return

    plt.close("all")
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(yearly.index, yearly.values, color="darkgreen", linewidth=1.8)
    ax.set_xlabel("公開年")
    ax.set_ylabel("本数")
    ax.set_title("年別の映画本数")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def plot_vote_average_hist(df: pd.DataFrame) -> None:
    d = df[df["vote_count"].fillna(0) >= 50].copy()
    if d.empty:
        st.info("vote_count >= 50 のデータがありません。")
        return

    plt.close("all")
    fig, ax = plt.subplots(figsize=(9, 4.8))
    sns.histplot(d["vote_average"], bins=40, kde=True, ax=ax, color="coral")
    ax.set_xlabel("平均評価（vote_average）")
    ax.set_ylabel("本数")
    ax.set_title("評価の分布（vote_count >= 50）")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def plot_runtime_hist(df: pd.DataFrame) -> None:
    d = df.dropna(subset=["runtime"]).copy()
    d = d[(d["runtime"] > 0) & (d["runtime"] < 400)]
    if d.empty:
        st.info("上映時間の分布に使えるデータがありません。")
        return

    plt.close("all")
    fig, ax = plt.subplots(figsize=(9, 4.8))
    sns.histplot(d["runtime"], bins=50, kde=True, ax=ax, color="mediumpurple")
    ax.set_xlabel("上映時間（分）")
    ax.set_ylabel("本数")
    ax.set_title("上映時間の分布")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


if data.empty:
    st.warning("選択条件に一致する映画がありません。")
else:
    plot_budget_vs_revenue(data)
    plot_movies_per_year(data)
    plot_vote_average_hist(data)
    plot_runtime_hist(data)

