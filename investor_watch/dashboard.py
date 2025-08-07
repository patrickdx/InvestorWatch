'''
    Streamlit dashboard for displaying results from the MongoDB database.
    - Displays a table of news articles for a selected week.
    - Allows filtering by ticker.
    - Displays a bar chart of articles per day.
    - Displays a bar chart of the top tickers mentioned in the articles.
    - Data flow: any time something must be updated on the screen, Streamlit reruns your entire Python script from top to bottom. (when user intracts / code changes)
'''


import streamlit as st; st.set_page_config(layout='wide')
from Driver import Driver
import pandas as pd
from datetime import datetime, timedelta, timezone
import plotly.express as px
from collections import Counter



st.title("📈 Weekly Stock News :blue[Dashboard]")

# Weekly date selector
today = datetime.now(timezone.utc)
last_sunday = today - timedelta(days=today.weekday() + 1)
weeks = [last_sunday - timedelta(weeks=i) for i in range(12)]     # last 12 weeks
week_ranges = [f"{w.strftime('%Y-%m-%d')} to {(w + timedelta(days=6)).strftime('%Y-%m-%d')}" for w in weeks]
selected_week = st.selectbox("Select a week:", week_ranges)


# Get the start and end dates for the selected week
start_date = datetime.strptime(selected_week.split(" to ")[0], "%Y-%m-%d")
end_date = start_date + timedelta(days=6)
query = {"date": {"$gte": start_date, "$lte": end_date}}

# Load data from MongoDB
if query == st.session_state.get('query'):      # if the query is the same, use the persisted dataframe
    data = st.session_state['data']
else: 
    with st.spinner("Wait for it...", show_time=True):
        driver = Driver()
        data = pd.DataFrame(driver.collection.find(query))              # fetch from MongoDB the data for the selected week
        st.session_state['query'] = query 
        st.session_state['data'] = data

        if data.empty:
            st.warning("No news articles found for this week.")
            st.stop()



# Ticker filtering 
selected_tickers = st.multiselect('Select a Ticker', data['ticker'].unique())
if selected_tickers: data = data[data['ticker'].isin(selected_tickers)]                     


# Preprocessing
data["date"] = pd.to_datetime(data["date"])
data = (data
        .drop(columns=['_id', 'content'])
        .drop_duplicates(subset=['title'])      # scuffed removal for duplicates for now
        .reset_index(drop = True)
       )

print(data) 


# ---------------------------------------------GRAPHS--------------------------------------------------------------
 
# News table with expanders
st.subheader("📰 News Articles")
st.dataframe(data)

data["day"] = data["date"].dt.date

# Ticker frequency (from 'ticker' and 'tags')
def extract_tickers(row):
    tickers = [row["ticker"]] if "ticker" in row and row["ticker"] else []
    tickers += row.get("tags", [])
    return tickers

all_tickers = data.apply(extract_tickers, axis=1).sum()
ticker_counts = pd.DataFrame(Counter(all_tickers).most_common(10), columns=["Ticker", "Mentions"])


# ---------------------------------------------SENTIMENT ANALYSIS--------------------------------------------------------------

# Check if sentiment data exists
if 'sentiment' in data.columns and not data['sentiment'].isna().all():
    st.header("🎭 Sentiment Analysis")
    
    # Overall sentiment distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Overall Sentiment Distribution")
        sentiment_counts = data['sentiment'].value_counts()
        
        # Create a pie chart for sentiment distribution
        colors = {'positive': '#089981', 'neutral': '#d1c958', 'negative': '#F23645'}
        fig_pie = px.pie(values=sentiment_counts.values, names=sentiment_counts.index,
                        title="Sentiment Distribution",
                        color=sentiment_counts.index,
                        color_discrete_map=colors)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Display sentiment metrics
        total_articles = len(data)
        positive_pct = (sentiment_counts.get('positive', 0) / total_articles * 100)
        negative_pct = (sentiment_counts.get('negative', 0) / total_articles * 100)
        neutral_pct = (sentiment_counts.get('neutral', 0) / total_articles * 100)
        
        
    with col2:
        st.subheader("📈 Daily Sentiment Trends")
        # Daily sentiment trends
        daily_sentiment = data.groupby(['day', 'sentiment']).size().unstack(fill_value=0)
        
        # Ensure all sentiment columns exist
        for sentiment in ['positive', 'neutral', 'negative']:
            if sentiment not in daily_sentiment.columns:
                daily_sentiment[sentiment] = 0
        
        # Reorder columns to ensure consistent order
        daily_sentiment = daily_sentiment[['positive', 'neutral', 'negative']]
        
        # Create stacked bar chart for daily sentiment
        fig_daily = px.bar(daily_sentiment.reset_index(), x='day', 
                          y=['positive', 'neutral', 'negative'],
                          title="Daily Sentiment Breakdown",
                          color_discrete_map=colors)
        fig_daily.update_layout(barmode='stack')
        st.plotly_chart(fig_daily, use_container_width=True)
    
    # Sentiment by ticker analysis
    st.subheader("🏢 Sentiment by Top Tickers")
    
    # Get top 10 tickers and their sentiment breakdown
    top_tickers = ticker_counts.head(10)['Ticker'].tolist()
    ticker_sentiment_data = []
    
    for ticker in top_tickers:
        ticker_articles = data[data['ticker'] == ticker]
        if not ticker_articles.empty:
            sentiment_dist = ticker_articles['sentiment'].value_counts()
            for sentiment, count in sentiment_dist.items():
                ticker_sentiment_data.append({
                    'Ticker': ticker,
                    'Sentiment': sentiment,
                    'Count': count
                })
    
    if ticker_sentiment_data:
        ticker_sentiment_df = pd.DataFrame(ticker_sentiment_data)
        
        # Create grouped bar chart
        fig_ticker_sentiment = px.bar(ticker_sentiment_df, x='Ticker', y='Count', 
                                    color='Sentiment',
                                    title="Sentiment Distribution by Top Tickers",
                                    color_discrete_map=colors,
                                    barmode='group')
        fig_ticker_sentiment.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_ticker_sentiment, use_container_width=True)
    
    # Recent sentiment changes
    st.subheader("📊 Recent Sentiment Patterns")
    
    # Show most recent articles by sentiment
    recent_positive = data[data['sentiment'] == 'positive'].nlargest(3, 'date')[['ticker', 'title', 'date']]
    recent_negative = data[data['sentiment'] == 'negative'].nlargest(3, 'date')[['ticker', 'title', 'date']]
    
    col6, col7 = st.columns(2)
    
    with col6:
        st.success("🟢 Recent Positive News")
        if not recent_positive.empty:
            for _, article in recent_positive.iterrows():
                st.write(f"**{article['ticker']}**: {article['title'][:80]}...")
        else:
            st.write("No recent positive articles")
    
    with col7:
        st.error("🔴 Recent Negative News")
        if not recent_negative.empty:
            for _, article in recent_negative.iterrows():
                st.write(f"**{article['ticker']}**: {article['title'][:80]}...")
        else:
            st.write("No recent negative articles")

else:
    st.info("Could not find sentiment data. Run sentiment_analysis.py to add sentiment analysis to articles.")


st.subheader("🏷️ Top Tickers Mentioned")
fig2 = px.bar(ticker_counts, x="Mentions", y="Ticker", orientation="h")
st.plotly_chart(fig2)

