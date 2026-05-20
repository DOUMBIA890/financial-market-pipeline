# 📊 Financial Market Pipeline (Crypto Data Platform)

## 🚀 Overview

Ce projet est une **plateforme complète de data engineering** pour l’analyse des cryptomonnaies en temps réel.

Il couvre tout le pipeline de données :

- 🔄 Ingestion automatique des données crypto (API CoinGecko)
- 🗄️ Stockage dans PostgreSQL (Raw Layer)
- ⚙️ Transformation avec dbt (Staging + Marts)
- 📊 Analyse avancée (prix, volatilité, performance)
- 📈 Dashboard interactif avec Streamlit
- 🔁 Pipeline automatisé (ingestion → dbt run → dbt test)

---

## 🏗️ Architecture du projet


API CoinGecko
↓
Python Ingestion Script
↓
PostgreSQL (raw schema)
↓
dbt (staging layer)
↓
dbt marts (analytics layer)
↓
Streamlit Dashboard
↓
User insights


---

## 📦 Stack technique

- Python 🐍
- PostgreSQL 🐘
- dbt (data build tool)
- Streamlit 📊
- Plotly 📈
- SQLAlchemy
- CoinGecko API

---

## ⚙️ Pipeline automatisé

Le pipeline exécute automatiquement :

```bash
python pipeline/run_pipeline.py
Étapes :
📥 Ingestion des données crypto
⚙️ Transformation dbt (dbt run)
🧪 Tests qualité (dbt test)
📊 Modèles dbt
🔹 Staging
stg_crypto_prices
🔹 Marts
mart_crypto_daily_avg
mart_crypto_volatility
mart_crypto_performance
📈 Dashboard Streamlit