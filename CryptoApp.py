import streamlit as st
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

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

market_data = fetch_market_data()

if market_data:
    df = pd.DataFrame(market_data, columns=["name", "symbol", "current_price", "market_cap", 
                                            "total_volume", "price_change_percentage_24h"])

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

else:
    st.error("Failed to load data.")
    