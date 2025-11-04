import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# ====== PAGE CONFIG ======
st.set_page_config(page_title="KOSPI 200 Stock Recommendation", page_icon="📈", layout="wide")

# ====== INTRODUCTION ======
st.title("📈 KOSPI 200 Stock Recommendation System - English Version")
st.markdown("""
Welcome to the **KOSPI 200 Stock Recommendation System**!  

This interactive app allows you to:  
- Browse top recommended KOSPI 200 stocks  
- Filter by price change (up/down)  
- View historical price trends  
- Search for specific stocks  

**How to use:**  
1. Choose a filter or enter a stock symbol.  
2. Click "Get Recommendations".  
3. Explore stock information and charts.  

*Note: This app uses a stock data API that requires an API Key.*
""")

# ====== USER INPUT ======
api_key = st.text_input("Enter your Stock API Key:", "")
stock_filter = st.selectbox("Filter by price movement:", ["All", "Gainers", "Losers"])
search_symbol = st.text_input("Search by stock symbol (optional):", "")

search_button = st.button("Get Recommendations")

# ====== FETCH STOCK DATA ======
if search_button and api_key:
    # Example using Finnhub API (replace with your API)
    base_url = "https://finnhub.io/api/v1/quote"  # For demonstration
    kospi_stocks = ["005930.KS", "000660.KS", "035420.KS", "051910.KS", "207940.KS"]  # Samsung, SK Hynix, Naver...
    
    stock_data = []
    for symbol in kospi_stocks:
        if search_symbol and search_symbol.upper() not in symbol:
            continue
        params = {"symbol": symbol, "token": api_key}
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            stock_data.append({
                "symbol": symbol,
                "current_price": data.get("c", 0),
                "open": data.get("o", 0),
                "high": data.get("h", 0),
                "low": data.get("l", 0),
                "previous_close": data.get("pc", 0),
                "change": data.get("c", 0) - data.get("pc", 0)
            })
        except:
            st.warning(f"Failed to fetch data for {symbol}")
    
    if stock_data:
        df = pd.DataFrame(stock_data)
        
        # Filter gainers or losers
        if stock_filter == "Gainers":
            df = df[df["change"] > 0]
        elif stock_filter == "Losers":
            df = df[df["change"] < 0]
        
        st.subheader("KOSPI 200 Stock Recommendations")
        st.dataframe(df)
        
        # ====== Interactive plot ======
        st.subheader("Stock Price Comparison")
        plt.figure(figsize=(8,4))
        for idx, row in df.iterrows():
            prices = [row["previous_close"], row["current_price"]]
            plt.plot(["Previous Close", "Current Price"], prices, marker='o', label=row["symbol"])
        plt.ylabel("Price (KRW)")
        plt.title("Stock Price Change")
        plt.legend()
        st.pyplot(plt)
    else:
        st.warning("No stocks matched your filters or API returned no data.")
else:
    if search_button:
        st.warning("Please enter a valid API Key.")
