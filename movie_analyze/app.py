# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from analyze_movies import genre_names_from_cell, load_movies

# =========================
# 設定
# =========================
CSV_PATH = Path("tmdb_5000_movies.csv")

st.set_page_config(page_title="映画分析（TMDB）", layout="wide")
st.title("TMDB 5000 映画データ分析")

sns.set_theme(style="whitegrid")

# =========================
# データ読み込み
# =========================
@st.cache_data(show_spinner=False)
def load_and_prepare() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not CSV_PATH.exists():
        st.error(f"CSV が見つかりません: {CSV_PATH}")
        st.stop()

    df = load_movies(CSV_PATH)
    df = df.dropna(subset=["year"]).copy()
    df["year"] = df["year"].astype(int)

    for col in ["budget", "revenue", "runtime", "vote_average", "vote_count", "popularity"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["genres_list"] = df["genres"].apply(genre_names_from_cell)
    df_long = df.explode("genres_list", ignore_index=True).rename(columns={"genres_list": "genre"})
    df_long = df_long.dropna(subset=["genre"]).copy()
    df_long["genre"] = df_long["genre"].astype(str)

    return df, df_long


movies_df, genres_long_df = load_and_prepare()

# =========================
# フィルター
# =========================
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
    base = movies_df[(movies_df["year"] >= year_start) & (movies_df["year"] <= year_end)].copy()

    if selected_genre == "全ジャンル":
        return base

    long_filtered = genres_long_df[
        (genres_long_df["genre"] == selected_genre)
        & (genres_long_df["year"] >= year_start)
        & (genres_long_df["year"] <= year_end)
    ]
    ids = long_filtered["id"].dropna().unique().tolist()
    return base[base["id"].isin(ids)].copy()


data = filter_data()

# =========================
# KPI
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("映画本数", f"{len(data):,}")

avg_vote = float(data["vote_average"].mean()) if data["vote_average"].notna().any() else float("nan")
col2.metric("平均評価", "-" if pd.isna(avg_vote) else f"{avg_vote:.2f}")

avg_runtime = float(data["runtime"].mean()) if data["runtime"].notna().any() else float("nan")
col3.metric("平均上映時間", "-" if pd.isna(avg_runtime) else f"{avg_runtime:.1f} 分")

st.subheader("グラフ")

# =========================
# グラフ関数（安定版）
# =========================
def plot_budget_vs_revenue(df: pd.DataFrame):
    d = df[(df["budget"] > 0) & (df["revenue"] > 0)].copy()
    if d.empty:
        st.info("予算・興行収入データがありません")
        return

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.scatter(d["budget"], d["revenue"], alpha=0.35)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title("予算 vs 興行収入")

    st.pyplot(fig)
    plt.close(fig)


def plot_movies_per_year(df: pd.DataFrame):
    yearly = df.groupby("year").size().sort_index()
    if yearly.empty:
        st.info("年別データなし")
        return

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(yearly.index, yearly.values)
    ax.set_title("年別映画本数")

    st.pyplot(fig)
    plt.close(fig)


def plot_vote_average_hist(df: pd.DataFrame):
    d = df[df["vote_count"].fillna(0) >= 50]
    if d.empty:
        st.info("評価データなし")
        return

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.hist(d["vote_average"], bins=40)
    ax.set_title("評価分布")

    st.pyplot(fig)
    plt.close(fig)


def plot_runtime_hist(df: pd.DataFrame):
    d = df.dropna(subset=["runtime"])
    d = d[(d["runtime"] > 0) & (d["runtime"] < 400)]
    if d.empty:
        st.info("上映時間データなし")
        return

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.hist(d["runtime"], bins=50)
    ax.set_title("上映時間分布")

    st.pyplot(fig)
    plt.close(fig)


# =========================
# 描画（containerで分離）
# =========================
if data.empty:
    st.warning("該当データなし")
else:
    with st.container():
        plot_budget_vs_revenue(data)

    with st.container():
        plot_movies_per_year(data)

    with st.container():
        plot_vote_average_hist(data)

    with st.container():
        plot_runtime_hist(data)
