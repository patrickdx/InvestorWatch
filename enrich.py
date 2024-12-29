import logging
import requests 
from datetime import timedelta, datetime
import time
import pandas as pd
import yfinance as yf 
from bs4 import BeautifulSoup
import requests
import re 
import constants
import sys
import os 
import numpy as np 


INPUT_PATH = 'stocks/tickers'
OUTPUT_PATH = 'stocks/tickers_e'

class explore:

    def __init__(self, stock):
        self.stock = stock 
        PATH = OUTPUT_PATH if os.path.exists(f'{OUTPUT_PATH}/{stock}.csv') else INPUT_PATH      # why mine a second time?
        self.news = pd.read_csv(f'{PATH}/{stock}.csv', parse_dates=['Date'])

    def mine_price_changes(self):
        '''
        Adds intraday price movement to the news dataframe
        '''
        def get_intraday_return(): 
            oldest_date = self.news['Date'].min()
            data = yf.download(self.stock, period = 'max', start = oldest_date - timedelta(weeks = 1))       # news from [oldest_date, today]
            data.columns = data.columns.droplevel(1)                             # drop the multi-level column index
            data.columns.name = None 

            data['Prev Close'] = data['Close'].shift(1)     # get previous close by shifting it down by 1
            data['% Change'] = ((data['Close'] - data['Prev Close']) / data['Prev Close'])  * 100
            data['% Change'] = data['% Change'].round(2)
            data.sort_values('% Change', ascending = False, inplace = True)
            return data

        def lookup_date(timestamp, df):     # Looks up the price movement on a given date and populates news df
            try:
                return df.loc[str(timestamp.date()), '% Change']
            except KeyError:
                return None     # print(f'No price movement data for {timestamp.date()}')

        price_changes = get_intraday_return() 
        self.news['% Change'] = self.news['Date'].apply(lambda x: lookup_date(x, price_changes) )   
      

    def mine_google_results(self, topn = 1): 
        '''
        Mines potential news catalysts for the top N days with the highest price change (only necessary b/c of the free google api limit)
        '''
        news = self.news
        
        def get_search_results(row):                 
            if 'hits' in row and not np.isnan(row['hits']): print("already mined!"); return row['hits']           
            
            query = row['Title']
        
            params = {
                'q': f'"{query}"',
                'key': constants.GOOGLE_API_KEY, 
                'cx': constants.SEARCH_ENGINE_ID, 
            }

            try: 
                response = requests.get('https://www.googleapis.com/customsearch/v1', params = params).json() 
                if 'totalResults' not in response['queries']['request'][0]: return 0 
                num_results = int(response['queries']['request'][0]['totalResults'])
                print(query, num_results)
                return num_results
            
            except Exception as e:
                print(response)
                raise e

        volatility = news['% Change'].drop_duplicates().dropna().sort_values(key=abs, ascending=False).head(topn)
        news.loc[news['% Change'].isin(volatility), 'hits'] = news.loc[news['% Change'].isin(volatility)].apply(get_search_results, axis = 1)

    
    
    def enrich(self, topn = 1):
        '''
        Enriches the news dataframe with intraday price changes and google search results
        '''
        self.mine_price_changes() 
        self.mine_google_results(topn)
        # print(self.news)
        self.news.to_csv(f'{OUTPUT_PATH}/{self.stock}.csv', index = False)


if __name__ == '__main__':
    args = sys.argv[1:]
    for stock in args: explore(stock.upper()).enrich()


