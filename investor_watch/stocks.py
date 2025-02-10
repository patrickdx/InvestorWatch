
import yfinance as yf
import os 
from finvizfinance.news import News
from finvizfinance.screener.overview import Overview
from finvizfinance.quote import finvizfinance
import pandas as pd 
from datetime import datetime, timedelta
import time
import requests 
from investor_watch.constants import TICKER_PATH





stock_list = pd.read_csv('stocks/stocks.csv')

def update_stocklist():   # Update the list of stocks that meet market cap criteria.
    global stock_list

    foverview = Overview()
    foverview.set_filter(filters_dict={'Market Cap.': '+Large (over $10bln)', 'Country': 'USA'})
    df = foverview.screener_view() 
    df['Market Cap (billions)'] = df['Market Cap'] / 1e9
    df.drop(columns = ['P/E', 'Change', 'Market Cap', 'Volume'], inplace = True)

    stock_list = pd.concat([df,stock_list]).drop_duplicates(subset=['Ticker'])        # dropped duplicates will be the older ones (in stock_list)
    stock_list.to_csv('../stocks/stocks.csv', index = False) 


def get_news(df : pd.Series):       # sinks new news sources to csv files
    try:
        time.sleep(0.2)
        whitelist = ['Bloomberg', 'Reuters']
        news_df = finvizfinance(df['Ticker']).ticker_news()
        news_df = news_df[news_df['Source'].isin(whitelist)]              # whitelist

        file = f"{TICKER_PATH}/{df['Ticker']}.csv"
        last_modified = datetime.fromtimestamp(os.path.getmtime(file))
        news_df = news_df[(news_df['Date'] >= last_modified)].sort_values('Date')       # filter new news inbetween modified date and today

        if not os.path.exists(file):
            news_df.to_csv(file, index = False)  
            print(f'created {file} ...')

        news_df.to_csv(file, mode='a', header=False, index=False)         # append to existing file
        print(f'Found {len(news_df)} new sources of ${df['Ticker']} ...')   

    except Exception as e:
        print(e)


stock_list.apply(get_news, axis = 1)            # apply get_news() on every row


