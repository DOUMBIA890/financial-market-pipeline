import os
import requests
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
import sys

# =========================
# UTF-8 FIX
# =========================
sys.stdout.reconfigure(encoding="utf-8")

# =========================
# ENV
# =========================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

print("DEBUG ENV:", DB_HOST, DB_USER, DB_PORT, DB_NAME)

# =========================
# ENGINE
# =========================
engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    pool_pre_ping=True
)

# =========================
# API
# =========================
url = "https://api.coingecko.com/api/v3/simple/price"

params = {
    "ids": "bitcoin,ethereum,solana",
    "vs_currencies": "usd"
}

response = requests.get(url, params=params, timeout=10)
response.raise_for_status()
data = response.json()

# =========================
# TRANSFORMATION RAW
# =========================
records = []

for crypto, values in data.items():
    records.append({
        "crypto": crypto,
        "price_usd": values["usd"],
        "timestamp": datetime.now(timezone.utc)
    })

df = pd.DataFrame(records)

print("📊 DATA INGESTED:")
print(df)

# =========================
# LOAD RAW TABLE (IMPORTANT FIX)
# =========================
df.to_sql(
    "crypto_prices",
    engine,
    schema="raw",
    if_exists="append",
    index=False
)

print("✅ Ingestion réussie (RAW uniquement)")