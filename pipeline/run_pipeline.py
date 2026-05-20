import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import subprocess
from pathlib import Path
import time

# ======================
# CONFIG PAGE
# ======================
st.set_page_config(
    page_title="Crypto Intelligence PRO",
    page_icon="📊",
    layout="wide"
)

# ======================
# STYLE DARK PRO
# ======================
st.markdown("""
<style>
    .main {
        background: radial-gradient(circle at top, #0b0f19, #05070d);
        color: white;
    }

    h1 {
        color: #00ffcc;
        font-size: 34px;
    }

    .stMetric {
        background: rgba(20, 25, 40, 0.85);
        border: 1px solid #2a3550;
        border-radius: 14px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Crypto Intelligence PRO Dashboard")
st.caption("Full pipeline: ingestion → dbt → analytics → monitoring → dashboard")

# ======================
# LOG FILE
# ======================
LOG_FILE = Path("pipeline/logs.txt")

# ======================
# DB CONNECTION
# ======================
load_dotenv()

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# ======================
# PIPELINE RUNNER
# ======================
def run_pipeline():

    st.info("🚀 Pipeline execution started...")

    process = subprocess.run(
        "python pipeline/run_pipeline.py",
        shell=True,
        capture_output=True,
        text=True
    )

    return process.returncode, process.stdout, process.stderr

# ======================
# LOAD DATA
# ======================
@st.cache_data(ttl=30)
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
# PIPELINE CONTROL CENTER
# ======================
st.subheader("⚙️ Pipeline Control Center")

col1, col2, col3 = st.columns(3)

with col1:
    run_btn = st.button("🚀 Run Full Pipeline")

with col2:
    refresh_btn = st.button("🔄 Refresh Data")

with col3:
    st.metric("Status", "READY")

# ======================
# RUN PIPELINE
# ======================
if run_btn:

    code, out, err = run_pipeline()

    st.subheader("📜 Pipeline Logs")

    st.text_area("STDOUT", out, height=250)

    if err:
        st.text_area("STDERR", err, height=200)

    if code == 0:
        st.success("✅ Pipeline executed successfully")
    else:
        st.error("❌ Pipeline failed")

    st.rerun()

# ======================
# REFRESH DATA
# ======================
if refresh_btn:
    st.cache_data.clear()
    st.rerun()

# ======================
# SIDEBAR FILTERS
# ======================
st.sidebar.header("🎛️ Filters")

cryptos = sorted(df_avg["crypto"].unique())

selected = st.sidebar.multiselect(
    "Cryptos",
    cryptos,
    default=cryptos
)

df_avg = df_avg[df_avg["crypto"].isin(selected)]
df_vol = df_vol[df_vol["crypto"].isin(selected)]
df_perf = df_perf[df_perf["crypto"].isin(selected)]

# ======================
# GLOBAL KPIs
# ======================
st.subheader("📌 Market Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Cryptos", len(selected))
c2.metric("Observations", len(df_avg))

last_date = df_avg["date_only"].max()
c3.metric("Last Update", str(last_date.date()) if pd.notnull(last_date) else "N/A")

c4.metric("Avg Price", f"{df_avg['avg_price_usd'].mean():,.2f} $")

# ======================
# PRICE KPI PER CRYPTO
# ======================
st.subheader("💰 Crypto KPIs")

cols = st.columns(len(selected))

for i, crypto in enumerate(selected):

    df_c = df_avg[df_avg["crypto"] == crypto].sort_values("date_only")

    if len(df_c) > 1:

        latest = df_c["avg_price_usd"].iloc[-1]
        prev = df_c["avg_price_usd"].iloc[-2]

        change = ((latest - prev) / prev) * 100

        cols[i].metric(
            crypto.upper(),
            f"{latest:,.2f} $",
            f"{change:.2f}%"
        )

# ======================
# PRICE EVOLUTION
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
    font=dict(color="white"),
    height=450
)

st.plotly_chart(fig_price, use_container_width=True)

# ======================
# VOLATILITY
# ======================
st.subheader("⚡ Volatility")

fig_vol = px.bar(
    df_vol,
    x="date_only",
    y="volatility",
    color="crypto",
    barmode="group"
)

fig_vol.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0b0f19",
    plot_bgcolor="#0b0f19",
    font=dict(color="white"),
    height=400
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
    font=dict(color="white"),
    height=400
)

st.plotly_chart(fig_perf, use_container_width=True)

# ======================
# CORRELATION MATRIX
# ======================
st.subheader("🔗 Correlation Matrix")

corr = df_avg.pivot_table(
    index="date_only",
    columns="crypto",
    values="avg_price_usd"
).corr()

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
    font=dict(color="white"),
    height=450
)

st.plotly_chart(fig_corr, use_container_width=True)

# ======================
# DATA TABLE
# ======================
st.subheader("📋 Data Table")

st.dataframe(df_avg, use_container_width=True)

# ======================
# LOG VIEWER
# ======================
st.subheader("📜 Pipeline Logs")

if LOG_FILE.exists():
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        logs = f.read()

    st.text_area("Logs", logs, height=250)
else:
    st.warning("No logs found")