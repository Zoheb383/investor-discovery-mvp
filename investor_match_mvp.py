# investor_match_mvp.py
# MVP for Investor Discovery & Deal Matching Platform (with backtesting support)

import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import streamlit as st
import pandas as pd

# -------------------- MODULE 1: MOCK ARTICLE INGESTION --------------------

def get_mock_articles():
    return [
        """
        Accel India has announced a new $650 million fund focused on early-stage consumer tech startups across India and Southeast Asia.
        This follows similar moves by Sequoia Capital and Lightspeed Ventures.
        """,
        """
        Matrix Partners and Peak XV Partners are increasing exposure to AI and healthtech sectors in India with $400M in new capital.
        Deals are expected across Singapore and Indonesia.
        """,
        """
        Elevation Capital joins forces with Falcon Edge to fund crypto and sustainability ventures in Asia.
        They are looking to deploy cheques between $5M to $20M.
        """
    ]

# -------------------- MODULE 2: NLP EXTRACTOR --------------------

def extract_data_from_text(text):
    fund_pattern = r"([A-Z][a-zA-Z]+\s(?:Capital|Ventures|Partners|Group|Investments|Fund|Advisors))"
    amount_pattern = r"\$[\d,]+(?:\s?(?:million|billion|M|B))"
    sector_keywords = ["consumer tech", "fintech", "edtech", "healthtech", "sustainability", "AI", "crypto"]
    geography_keywords = ["India", "Southeast Asia", "Singapore", "Indonesia", "Asia"]

    funds = re.findall(fund_pattern, text)
    amounts = re.findall(amount_pattern, text)
    sectors = [sector for sector in sector_keywords if sector.lower() in text.lower()]
    geographies = [geo for geo in geography_keywords if geo.lower() in text.lower()]

    return {
        "funds": list(set(funds)),
        "amounts": amounts,
        "sectors": sectors,
        "geographies": geographies
    }

# -------------------- MODULE 3: DATABASE --------------------

def init_db():
    conn = sqlite3.connect("investors.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS investors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fund TEXT,
            amount TEXT,
            sector TEXT,
            geography TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_data_to_db(data):
    conn = sqlite3.connect("investors.db")
    c = conn.cursor()
    for fund in data["funds"]:
        for sector in data["sectors"]:
            for geo in data["geographies"]:
                amount = data["amounts"][0] if data["amounts"] else None
                c.execute("INSERT INTO investors (fund, amount, sector, geography) VALUES (?, ?, ?, ?)",
                          (fund, amount, sector, geo))
    conn.commit()
    conn.close()

# -------------------- MODULE 4: STREAMLIT UI --------------------

def streamlit_ui():
    st.title("Investor Discovery Platform")
    conn = sqlite3.connect("investors.db")
    df = pd.read_sql_query("SELECT * FROM investors", conn)

    sector_filter = st.multiselect("Filter by Sector", df["sector"].unique())
    geo_filter = st.multiselect("Filter by Geography", df["geography"].unique())

    if sector_filter:
        df = df[df["sector"].isin(sector_filter)]
    if geo_filter:
        df = df[df["geography"].isin(geo_filter)]

    st.dataframe(df)
    conn.close()

# -------------------- MAIN EXECUTION --------------------

def run_backtest_pipeline():
    init_db()
    articles = get_mock_articles()
    for article in articles:
        extracted = extract_data_from_text(article)
        insert_data_to_db(extracted)

run_backtest_pipeline()

if __name__ == "__main__":
    streamlit_ui()
