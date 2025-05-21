'''
    Streamlit dashboard for displaying results from the MongoDB database.
    - Displays a table of news articles for a selected week.
    - Allows filtering by ticker.
    - Displays a bar chart of articles per day.
    - Displays a bar chart of the top tickers mentioned in the articles.
'''


import streamlit as st; st.set_page_config(layout='wide')
from Driver import Driver
import pandas as pd
from datetime import datetime, timedelta, timezone
import plotly.express as px
from collections import Counter


# Streamlit Dashboard
# - Data flow: any time something must be updated on the screen, Streamlit reruns your entire Python script from top to bottom. (when user intracts / code changes)


st.title("📈 Weekly Stock News :blue[Dashboard]")
driver = Driver()


# Weekly date selector
today = datetime.now(timezone.utc)
last_sunday = today - timedelta(days=today.weekday() + 1)
weeks = [last_sunday - timedelta(weeks=i) for i in range(12)]
week_ranges = [f"{w.strftime('%Y-%m-%d')} to {(w + timedelta(days=6)).strftime('%Y-%m-%d')}" for w in weeks]
selected_week = st.selectbox("Select a week:", week_ranges)


# Date filtering
start_date = datetime.strptime(selected_week.split(" to ")[0], "%Y-%m-%d")
end_date = start_date + timedelta(days=6)
query = {"date": {"$gte": start_date, "$lte": end_date}}

# Fetch data
data = pd.DataFrame(driver.collection.find(query))
if data.empty:
    st.warning("No news articles found for this week.")
    st.stop()

# Ticker filtering 
selected_tickers = st.multiselect('Select a Ticker', data['ticker'].unique())
if selected_tickers: data = data[data['ticker'].isin(selected_tickers)]                     


# Preprocessing
data["date"] = pd.to_datetime(data["date"])
data["day"] = data["date"].dt.date
data = (data
        .drop(columns=['_id'])
        .drop_duplicates(subset=['title'])      # scuffed removal for duplicates for now
        .reset_index(drop = True)
       )

print(data) 


# -----------------------------------------------------------------------------------------------------------
 
# News table with expanders
st.subheader("📰 News Articles")
st.dataframe(data)

# Daily article count
st.subheader("🗓️ Articles Per Day")
daily_counts = data.groupby("day").size().reset_index(name="count")
fig = px.bar(daily_counts, x="day", y="count", title="Article Count by Day")
st.plotly_chart(fig)

# Ticker frequency (from 'ticker' and 'tags')
def extract_tickers(row):
    tickers = [row["ticker"]] if "ticker" in row and row["ticker"] else []
    tickers += row.get("tags", [])
    return tickers

all_tickers = data.apply(extract_tickers, axis=1).sum()
ticker_counts = pd.DataFrame(Counter(all_tickers).most_common(10), columns=["Ticker", "Mentions"])

st.subheader("🏷️ Top Tickers Mentioned")
fig2 = px.bar(ticker_counts, x="Mentions", y="Ticker", orientation="h")
st.plotly_chart(fig2)

