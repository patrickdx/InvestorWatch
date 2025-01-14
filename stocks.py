
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

def update_stocklist():
    # Get list of stocks that meet market cap criteria. Since sp500 is self-cleansing, companies get aquired / delisted frequently.

    market_cap = {
            'Mega' : 'Mega ($200bln and more)',
            'Large' : '+Large (over $10bln)',
            'Mid' : '+Mid (over $2bln)',
    }

    foverview = Overview()
    filters_dict = {'Market Cap.': market_cap['Large'], 'Country': 'USA'}

    foverview.set_filter(filters_dict=filters_dict)
    df = foverview.screener_view() 
    df['Market Cap (billions)'] = df['Market Cap'] / 1e9
    df.drop(columns = ['P/E', 'Change', 'Market Cap', 'Volume'], inplace = True)

    df.to_csv('stocks/stocks.csv', index = False)                               # sink all marketcap+ stocks


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
        print(e)

update_stocklist()    
df.apply(get_news, axis = 1)            # apply get_news() on every row



