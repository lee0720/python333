# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

from analyze_movies import genre_names_from_cell, load_movies

# =========================
# 設定
# =========================
CSV_PATH = Path("tmdb_5000_movies.csv")

st.set_page_config(page_title="映画分析（TMDB）", layout="wide")
st.title("TMDB 5000 映画データ分析")

# =========================
# データ読み込み
# =========================
@st.cache_data(ttl=3600)
def load_and_prepare():
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

year_range = sidebar.slider(
    "公開年の範囲",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
)

year_start, year_end = year_range

genre_options = sorted(genres_long_df["genre"].unique().tolist())
selected_genre = sidebar.selectbox("ジャンル", ["全ジャンル"] + genre_options)


def filter_data():
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

avg_vote = data["vote_average"].mean()
col2.metric("平均評価", "-" if pd.isna(avg_vote) else f"{avg_vote:.2f}")

avg_runtime = data["runtime"].mean()
col3.metric("平均上映時間", "-" if pd.isna(avg_runtime) else f"{avg_runtime:.1f} 分")

st.subheader("グラフ")

# =========================
# Plotlyグラフ
# =========================
if data.empty:
    st.warning("該当データなし")
else:

    # ① 予算 vs 興行収入
    d1 = data[(data["budget"] > 0) & (data["revenue"] > 0)]
    if not d1.empty:
        fig1 = px.scatter(
            d1,
            x="budget",
            y="revenue",
            log_x=True,
            log_y=True,
            title="予算 vs 興行収入",
            opacity=0.5,
        )
        st.plotly_chart(fig1, use_container_width=True)

    # ② 年別映画本数
    yearly = data.groupby("year").size().reset_index(name="count")
    if not yearly.empty:
        fig2 = px.line(
            yearly,
            x="year",
            y="count",
            title="年別映画本数",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ③ 評価分布
    d2 = data[data["vote_count"].fillna(0) >= 50]
    if not d2.empty:
        fig3 = px.histogram(
            d2,
            x="vote_average",
            nbins=40,
            title="評価分布",
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ④ 上映時間分布
    d3 = data.dropna(subset=["runtime"])
    d3 = d3[(d3["runtime"] > 0) & (d3["runtime"] < 400)]
    if not d3.empty:
        fig4 = px.histogram(
            d3,
            x="runtime",
            nbins=50,
            title="上映時間分布",
        )
        st.plotly_chart(fig4, use_container_width=True)
