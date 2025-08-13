import time
import random 
from finvizfinance.screener.overview import Overview
from finvizfinance.quote import finvizfinance
import pandas as pd
from Driver import Driver 
from util import web_scrape_content, web_scrape_tags
from sentiment_analysis import SentimentAnalyzer

'''
    Script that ingests news data from Yahoo Finance and stores it in MongoDB.  
    TODO: EXPAND # OF STOCKS > 500
    TODO: take care of duplicates 
'''

def refresh_sp500_list():
    """
    Refreshes the SP500.csv file with the current S&P 500 companies using finvizfinance screener.
    This ensures we always have the most up-to-date list of companies.
    """
    print("Refreshing S&P 500 company list using finvizfinance...")
    
    try:
        
        fviz = Overview()
        filters_dict = {'Index': 'S&P 500'}
        fviz.set_filter(filters_dict=filters_dict)
        df = fviz.screener_view()
        
        if df.empty:
            print("S&P 500 refresh failed. Using existing SP500.csv")
            return
        
        # Rename columns to match your existing format
        df_formatted = pd.DataFrame({
            'Ticker': df['Ticker'],
            'Company': df['Company'],
            'Sector': df['Sector'],
            'Industry': df['Industry'],
            'Country': df['Country'],
            'Market Cap': df['Market Cap'],
            'Price': df['Price']
        })
        
        csv_path = 'SP500.csv'
        df_formatted.to_csv(csv_path, index=False)
        
        print(f"Successfully updated SP500.csv with {len(df_formatted)} companies")
        
    except Exception as e:
        print(f"Error refreshing S&P 500 list: {e}")
        print("Using existing SP500.csv file")



def gather_news(ticker) -> pd.DataFrame:       
    
    try:
        whitelist = ['Bloomberg', 'Reuters']
        news_df = finvizfinance(ticker).ticker_news()
        news_df = news_df[news_df['Source'].isin(whitelist)]
        news_df['Ticker'] = ticker

        # only download newly published articles according to last ingest date

        # get the latest date from the existing articles
        query = driver.collection.find({'ticker': ticker}).sort({'date': -1}) 
        latest_article_date = query.next()['date']

        # only query by dates bigger 
        if latest_article_date: 
            news_df = news_df[news_df['Date'] > latest_article_date]

        print(f'Found {len(news_df)} new sources of ${ticker} ...')
        return news_df

    except Exception as e:      # probably got removed from SP500 or a merger
        print("Error gathering news: ", ticker, e)
        return pd.DataFrame()  

def ingest_news(df, sentiment_analyzer):
    
    for _, row in df.iterrows():
   
        document = {
            'date': row['Date'], 
            'title': row['Title'], 
            'link': row['Link'], 
            'source': row['Source'], 
            'ticker': row['Ticker'], 
            # optional
            'tags': [],     # the other stocks the article is related to
            'content': '',  # article content
            'sentiment': '' # article sentiment based on title
        }   
        
        # try to add complementary article information
        content  = web_scrape_content(row['Link'])
        tags = web_scrape_tags(row['Link'])

        if content: document['content'] = content 
        if tags: document['tags'] = tags 
        
        # Add sentiment analysis for the title
        try:
            sentiment_result = sentiment_analyzer.analyze_sentiment(row['Title'])
            document['sentiment'] = sentiment_result['sentiment']
        except Exception as e:
            print(f"Error analyzing sentiment for title: {row['Title']}... Error: {e}")

        driver.collection.insert_one(document)      # insert into mongodb


if __name__ == '__main__':

    print("Gathering news...")
    driver = Driver()
    
    print("Loading sentiment analysis model...")
    sentiment_analyzer = SentimentAnalyzer()
    
    if random.randint(0,10) == 7: refresh_sp500_list()                  # 10% chance to refresh 
    stock_list = pd.read_csv('SP500.csv')
    start_time = time.time() 

    for ticker in stock_list['Ticker']:
        time.sleep(0.2)
        news_df = gather_news(ticker)
        time.sleep(0.2)
        ingest_news(news_df, sentiment_analyzer)

    print(f'that took {time.time() - start_time:.2f}')

