import streamlit as st
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import time
from datetime import datetime

BASE_URL = "https://api.coingecko.com/api/v3"

st.title("Cryptocurrency Insights Dashboard")

st.sidebar.header("Settings")
currency = st.sidebar.selectbox("Select Currency", ["usd", "eur", "inr", "jpy"], index=0)
num_coins = st.sidebar.slider("Number of Coins to Analyze", min_value=5, max_value=50, value=10)

def fetch_market_data():
    url = f"{BASE_URL}/coins/markets"
    params = {
        "vs_currency": currency,
        "order": "market_cap_desc",
        "per_page": num_coins,
        "page": 1,
        "sparkline": False
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching data: {response.status_code}")
        return None

def fetch_ohlc_data(coin_id, vs_currency, from_timestamp, to_timestamp):
    url = f"{BASE_URL}/coins/{coin_id}/ohlc"
    params = {
        "vs_currency": vs_currency,
        "from": from_timestamp,
        "to": to_timestamp
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching OHLC data for {coin_id}: {response.status_code}")
        st.write(response.json())
        return None

market_data = fetch_market_data()

if market_data:
    df = pd.DataFrame(market_data, columns=["id", "name", "symbol", "current_price", "market_cap", "total_volume", "price_change_percentage_24h"])

    st.subheader("Market Data Overview")
    st.dataframe(df[["name", "symbol", "current_price", "market_cap", "total_volume", "price_change_percentage_24h"]])

    st.subheader("Top Gainers and Losers")
    gainers = df.nlargest(3, "price_change_percentage_24h")
    losers = df.nsmallest(3, "price_change_percentage_24h")

    col1, col2 = st.columns(2)
    with col1:
        st.write("*Top Gainers*")
        st.dataframe(gainers[["name", "symbol", "price_change_percentage_24h"]])
    with col2:
        st.write("*Top Losers*")
        st.dataframe(losers[["name", "symbol", "price_change_percentage_24h"]])

    st.subheader("Volatility Chart")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        data=df,
        x="total_volume",
        y="price_change_percentage_24h",
        size="market_cap",
        hue="name",
        sizes=(50, 500),
        alpha=0.7,
        ax=ax
    )
    ax.set_title("Volume vs Price Change")
    ax.set_xlabel("Trading Volume")
    ax.set_ylabel("Price Change (%)")
    ax.legend(title="Cryptocurrencies", bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig)

    st.subheader("OHLC Data")
    selected_coin = st.selectbox("Select a Coin", df["id"].tolist())
    start_date = st.date_input("Start Date", value=datetime(2023, 1, 1))
    end_date = st.date_input("End Date", value=datetime(2023, 12, 31))

    if st.button("Fetch OHLC Data"):
        from_timestamp = time.mktime(start_date.timetuple())
        to_timestamp = time.mktime(end_date.timetuple())

        st.write(f"Fetching OHLC data for {selected_coin} from {start_date} to {end_date}.")
        st.write(f"Start Timestamp: {from_timestamp}")
        st.write(f"End Timestamp: {to_timestamp}")

        ohlc_data = fetch_ohlc_data(selected_coin, currency, from_timestamp, to_timestamp)

        if ohlc_data:
            ohlc_df = pd.DataFrame(ohlc_data, columns=["timestamp", "open", "high", "low", "close"])
            ohlc_df["date"] = pd.to_datetime(ohlc_df["timestamp"], unit="ms")

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(ohlc_df["date"], ohlc_df["open"], label="Open", linestyle='-', color='green')
            ax.plot(ohlc_df["date"], ohlc_df["high"], label="High", linestyle='--', color='blue')
            ax.plot(ohlc_df["date"], ohlc_df["low"], label="Low", linestyle='--', color='red')
            ax.plot(ohlc_df["date"], ohlc_df["close"], label="Close", linestyle='-', color='black')
            
            ax.set_title(f"OHLC Data for {selected_coin.upper()}")
            ax.set_xlabel("Date")
            ax.set_ylabel(f"Price ({currency.upper()})")
            ax.legend()
            st.pyplot(fig)
else:
    st.error("Failed to load data.")
