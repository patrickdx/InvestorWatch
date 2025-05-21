import time
from finvizfinance.screener.overview import Overview
from finvizfinance.quote import finvizfinance
import pandas as pd
from datetime import datetime
from Driver import Driver 
from util import web_scrape_content, web_scrape_tags, ROOT_DIR

'''
    Ingests news data from Yahoo Finance and stores it in the NoSQL db.     
    Can schedule this to run daily or at your own discretion.
    TODO: EXPAND # OF STOCKS > 500
    TODO: take care of duplicates 
'''


driver = Driver()
stock_list = pd.read_csv(ROOT_DIR / 'SP500.csv')          # the stock list to query news from 

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

def ingest_news(df):
    
    for _, row in df.iterrows():
   
        document = {
            'date': row['Date'], 
            'title': row['Title'], 
            'link': row['Link'], 
            'source': row['Source'], 
            'ticker': row['Ticker'], 
            'tags': [],     # the other stocks the article is related to
            'content': ''   # optional
        }   
        
        # try to add complementary article information
        content  = web_scrape_content(row['Link'])
        tags = web_scrape_tags(row['Link'])

        if content: document['content'] = content 
        if tags: document['tags'] = tags 


        driver.collection.insert_one(document)      # insert into mongodb

        


def main():
    print("Gathering news...")
    start_time = time.time() 

    for ticker in stock_list['Ticker']:
        time.sleep(0.2)
        news_df = gather_news(ticker)
        time.sleep(0.2)
        ingest_news(news_df)

    print(f'that took {time.time() - start_time:.2f}')

if __name__ == '__main__':
    main()
