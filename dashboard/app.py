import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# ======================
# CONFIG
# ======================
st.set_page_config(
    page_title="Crypto Trading Dashboard",
    page_icon="📊",
    layout="wide"
)

# ======================
# DARK TRADING THEME
# ======================
st.markdown("""
<style>
    .main {
        background-color: #0b0f19;
        color: #ffffff;
    }

    h1, h2, h3 {
        color: #ffffff;
    }

    .block-container {
        padding-top: 2rem;
    }

    div[data-testid="metric-container"] {
        background-color: #121a2a;
        border: 1px solid #26324a;
        padding: 14px;
        border-radius: 12px;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.3);
    }

    .stDataFrame {
        background-color: #0b0f19;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Crypto Trading Intelligence Dashboard")
st.caption("DBT • PostgreSQL • Streamlit • Analytics Engine")

# ======================
# DB CONNECTION
# ======================
load_dotenv()

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# ======================
# LOAD DATA
# ======================
@st.cache_data
def load_data():
    df_avg = pd.read_sql("SELECT * FROM analytics.mart_crypto_daily_avg", engine)
    df_vol = pd.read_sql("SELECT * FROM analytics.mart_crypto_volatility", engine)
    df_perf = pd.read_sql("SELECT * FROM analytics.mart_crypto_performance", engine)

    df_avg["date_only"] = pd.to_datetime(df_avg["date_only"])
    df_vol["date_only"] = pd.to_datetime(df_vol["date_only"])
    df_perf["date_only"] = pd.to_datetime(df_perf["date_only"])

    return df_avg, df_vol, df_perf


df_avg, df_vol, df_perf = load_data()

# ======================
# SIDEBAR FILTERS
# ======================
st.sidebar.header("🎛️ Trading Filters")

cryptos = sorted(df_avg["crypto"].unique())

selected_cryptos = st.sidebar.multiselect(
    "Assets",
    cryptos,
    default=cryptos
)

df_avg = df_avg[df_avg["crypto"].isin(selected_cryptos)]
df_vol = df_vol[df_vol["crypto"].isin(selected_cryptos)]
df_perf = df_perf[df_perf["crypto"].isin(selected_cryptos)]

# ======================
# KPI SECTION (TRADING STYLE)
# ======================
st.subheader("📊 Market Overview")

latest_prices = df_avg.groupby("crypto").tail(1)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Assets", len(selected_cryptos))
col2.metric("Observations", len(df_avg))
col3.metric("Last Update", str(df_avg["date_only"].max().date()))
col4.metric("Avg BTC Price", f"{df_avg[df_avg['crypto']=='bitcoin']['avg_price_usd'].mean():.2f}")

# ======================
# PRICE CHART
# ======================
st.subheader("📈 Price Evolution")

fig_price = px.line(
    df_avg,
    x="date_only",
    y="avg_price_usd",
    color="crypto",
    markers=True
)

fig_price.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0b0f19",
    plot_bgcolor="#0b0f19",
    font=dict(color="white")
)

st.plotly_chart(fig_price, use_container_width=True)

# ======================
# VOLATILITY
# ======================
st.subheader("⚡ Volatility Heat")

fig_vol = px.bar(
    df_vol,
    x="date_only",
    y="volatility",
    color="crypto"
)

fig_vol.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0b0f19",
    plot_bgcolor="#0b0f19",
    font=dict(color="white")
)

st.plotly_chart(fig_vol, use_container_width=True)

# ======================
# PERFORMANCE
# ======================
st.subheader("📊 Performance (%)")

fig_perf = px.line(
    df_perf,
    x="date_only",
    y="pct_change",
    color="crypto",
    markers=True
)

fig_perf.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0b0f19",
    plot_bgcolor="#0b0f19",
    font=dict(color="white")
)

st.plotly_chart(fig_perf, use_container_width=True)

# ======================
# TOP MOVERS
# ======================
st.subheader("🔥 Top Movers")

latest_perf = df_perf.sort_values("date_only").groupby("crypto").tail(1)

top = latest_perf.sort_values("pct_change", ascending=False)

st.dataframe(top[["crypto", "pct_change"]], use_container_width=True)

# ======================
# CORRELATION MATRIX
# ======================
st.subheader("🔗 Correlation Matrix")

corr_df = df_avg.pivot_table(
    index="date_only",
    columns="crypto",
    values="avg_price_usd"
)

corr = corr_df.corr()

fig_corr = go.Figure(
    data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale="RdBu",
        zmid=0
    )
)

fig_corr.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0b0f19",
    font=dict(color="white")
)

st.plotly_chart(fig_corr, use_container_width=True)

# ======================
# DATA TABLE
# ======================
st.subheader("📋 Raw Data (DBT Layer)")

st.dataframe(df_avg, use_container_width=True)