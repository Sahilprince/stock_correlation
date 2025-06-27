import pandas as pd
import streamlit as st
import yfinance as yf
from datetime import date
from niftystocks import ns

st.set_page_config(page_title="NSE Stock Correlation", layout="centered")

# 🎯 Get all NSE tickers (Nifty 500)
all_symbols = ns.get_nifty500_with_ns()

# @st.cache_data is used to cache the yfinance data downloads.
# This prevents re-downloading data if the same stock and date range are selected again.
@st.cache_data
def get_stock_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end, auto_adjust=True)
    print(df.columns)  # Debugging: print the first few rows of the DataFrame
    if df.empty or 'Close' not in df.columns:
        raise ValueError(f"No valid data found for {ticker}")
    df = df[['Close']]  # keep as DataFrame
    df.columns = [ticker]  # rename 'Close' to ticker name
    return df

# 🧠 App title
st.title("📈 NSE Stock Correlation Tool")

# 🎛️ User inputs
stock1 = st.selectbox("Select First Stock", all_symbols)
stock2 = st.selectbox("Select Second Stock", all_symbols)

start_date = st.date_input("Start Date", value=date(2024, 1, 1))
end_date = st.date_input("End Date", value=date.today())

# 🚀 Action button
if st.button("Calculate Correlation"):
    if stock1 == stock2:
        st.warning("Please select two different stocks.")
    else:
        try:
            # Download Adjusted Close price using the cached function
            s1 = get_stock_data(stock1, start_date, end_date)
            s2 = get_stock_data(stock2, start_date, end_date)
            print("Stock 1 Data Head:\n", s1.head())
            print("Stock 2 Data Head:\n", s2.head())

            # Join both DataFrames on date
            combined_df = s1.join(s2, how='inner')

            print("Combined Data Head:\n", combined_df.head())

            # Calculate daily returns for both stocks
            returns = combined_df.pct_change().dropna()
            print("Returns Data Head:\n", returns.head())

            # Check for enough data
            if returns.shape[0] < 2:
                st.warning(f"Not enough common data points for correlation between {stock1} and {stock2} in the selected date range.")
            else:
                # Calculate Pearson correlation
                corr = returns.corr().iloc[0, 1]

                st.success(f"Correlation between {stock1} and {stock2}: **{corr:.4f}**")
                print(f"Correlation between {stock1} and {stock2}: {corr:.4f}")

                # Optional: plot closing prices
                st.line_chart(combined_df)

        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")

