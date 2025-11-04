import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

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
1. Enter your Finnhub API Key (optional).  
2. Choose a stock from the dropdown or enter a stock symbol.  
3. Click "Get Recommendations".  
4. Explore stock information and charts.  

*Note: If you do not provide an API Key, the app will use simulated stock data.*
""")

# ====== USER INPUT ======
api_key = st.text_input("Enter your Finnhub API Key (optional):", "")

kospi_stocks_dict = {
    "Samsung Electronics": "005930.KS",
    "SK Hynix": "000660.KS",
    "Naver": "035420.KS",
    "LG Chem": "051910.KS",
    "Samsung Biologics": "207940.KS"
}

selected_stock_name = st.selectbox("Select a stock (dropdown):", ["All"] + list(kospi_stocks_dict.keys()))
search_symbol_input = st.text_input("Or enter stock symbol (optional):", "")
stock_filter = st.selectbox("Filter by price movement:", ["All", "Gainers", "Losers"])
search_button = st.button("Get Recommendations")

# ====== DETERMINE SEARCH SYMBOL ======
if selected_stock_name != "All":
    search_symbol = kospi_stocks_dict[selected_stock_name]
elif search_symbol_input:
    search_symbol = search_symbol_input.upper()
else:
    search_symbol = ""

# ====== FETCH STOCK DATA ======
kospi_stocks = list(kospi_stocks_dict.values())  # All stock codes

if search_button:
    stock_data = []

    if api_key:  # Use Finnhub API
        st.info("Fetching real-time data from Finnhub...")
        base_url = "https://finnhub.io/api/v1/quote"
        for symbol in kospi_stocks:
            if search_symbol and search_symbol not in symbol:
                continue
            params = {"symbol": symbol, "token": api_key}
            try:
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()
                if data.get("c") is None:
                    st.warning(f"No data returned for {symbol}")
                    continue
                stock_data.append({
                    "symbol": symbol,
                    "current_price": data.get("c", 0),
                    "previous_close": data.get("pc", 0),
                    "change": data.get("c", 0) - data.get("pc", 0)
                })
            except Exception as e:
                st.warning(f"Failed to fetch data for {symbol}: {e}")
    else:  # Use simulated data
        st.info("Using simulated stock data (no API Key provided).")
        stock_data = [
            {"symbol":"005930.KS","current_price":61000,"previous_close":60500,"change":500},
            {"symbol":"000660.KS","current_price":100000,"previous_close":99500,"change":500},
            {"symbol":"035420.KS","current_price":350000,"previous_close":345000,"change":500},
            {"symbol":"051910.KS","current_price":750000,"previous_close":740000,"change":10000},
            {"symbol":"207940.KS","current_price":950000,"previous_close":940000,"change":10000},
        ]
        if search_symbol:
            stock_data = [s for s in stock_data if search_symbol in s["symbol"]]

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

        # ====== Historical 7-day chart using yfinance ======
        st.subheader("Historical 7-Day Price Trend")
        for row in df.itertuples():
            symbol = row.symbol
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period="7d")
                if hist.empty:
                    continue
                plt.figure(figsize=(8,3))
                plt.plot(hist.index, hist['Close'], marker='o')
                plt.title(f"{symbol} - Last 7 Days Close Price")
                plt.ylabel("Price (KRW)")
                plt.xticks(rotation=45)
                plt.grid(True)
                st.pyplot(plt)
            except:
                st.warning(f"Cannot fetch historical data for {symbol}")
    else:
        st.warning("No stocks matched your filters or API returned no data.")

