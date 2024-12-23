
import sys
import os 
from finvizfinance.news import News
from finvizfinance.screener.overview import Overview
from finvizfinance.quote import finvizfinance
import pandas as pd 
from datetime import datetime
import time

PATH = 'stocks/tickers'

if not os.path.exists(PATH): os.makedirs(PATH)


df = pd.read_csv('stocks/stocks.csv')

def get_news(df : pd.Series):       # sinks new news sources to csv files
    try:
            
        time.sleep(0.3)
        file = f"{PATH}/{df['Ticker']}.csv"
        whitelist = ['Bloomberg', 'Reuters']
        news_df = finvizfinance(df['Ticker']).ticker_news()
        news_df = news_df[news_df['Source'].isin(whitelist)]              # whitelist

        today = datetime.today()                                           
        last_modified = datetime.fromtimestamp(os.path.getmtime(file))
        news_df = news_df[(news_df['Date'] >= last_modified) & (news_df['Date'] <= today)].sort_values('Date')      # look for news dates inbetween last modified date and today

        if not os.path.exists(file):
            news_df.to_csv(file, index = False)  
            print(f'created {file} ...')

        news_df.to_csv(file, mode='a', header=False, index=False)         # append/remove header
        print(f'found {len(news_df)} new sources to {file} ...')   

    except Exception as e:
        print("Could not find news!", e)

    

df.apply(get_news, axis = 1)            # apply get_news() on every row


# get_news(df.iloc[465])

