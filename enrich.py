import yfinance as yf 
from bs4 import BeautifulSoup
import time
import os 
import numpy as np 
from finvizfinance.news import News
from finvizfinance.screener.overview import Overview
from finvizfinance.quote import finvizfinance
import pandas as pd 
import yfinance as yf
from datetime import timedelta, datetime
import time

INPUT_PATH = 'stocks/tickers'

class explore:
    '''A collection of data exploration ideas to be applied on the base news article df.'''
    
    def __init__(self, ticker):
        self.ticker = ticker 
        self.df = self._get_news()


    def _get_news(self):       # sinks new news sources to csv files
        ticker = self.ticker
        try:
            time.sleep(0.2)
            whitelist = ['Bloomberg', 'Reuters']
            news_df = finvizfinance(ticker).ticker_news()
            news_df = news_df[news_df['Source'].isin(whitelist)]              # whitelist

            file = f"{"./stocks/tickers"}/{ticker}.csv"
            last_modified = datetime.fromtimestamp(os.path.getmtime(file))
            news_df = news_df[(news_df['Date'] >= last_modified)].sort_values('Date')       # filter new news inbetween modified date and today

            print(f'Found {len(news_df)} new sources of ${ticker} ...')   
            return news_df

        except Exception as e:
            print(e)
    

    def _ex_price_changes(self): 
        pass

    def _ex_search_hits(self):
        pass

    def enrich(self):               
        
        self._ex_price_changes()
        self._ex_search_hits()
        return self.df 
        


print(explore('AAPL').df)
        


