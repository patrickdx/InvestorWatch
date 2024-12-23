
import sys
import os 

sys.path.append(os.path.join(os.path.dirname(__file__), 'finvizfinance'))   # modify sys path to include finviz dir (temp)

from finvizfinance.news import News
from finvizfinance.screener.overview import Overview
from finvizfinance.quote import finvizfinance
import pandas as pd 
import datetime
import time
from util import logger


# stocks = pd.read_csv('+Large (over $10bln).csv')
# news_df = None
# counts = {}

# def truncate_corporate_suffix(name) -> pd.Series: 
#         suffix = [', Inc.', 'Inc.', 'Inc', 
#                   'Corp.', 'Corp', 'Corporation', 
#                   'Co.,', 'Co.', 'Co', 
#                   'Ltd.', 'Ltd'
#                 ]
#         for s in suffix: 
#             if name.endswith(s): name = name[: -len(s)].strip()
#         return name 


def get_stock_list():
    
    
    market_cap = {
         'Mega' : 'Mega ($200bln and more)',
         'Large' : '+Large (over $10bln)',
         'Mid' : '+Mid (over $2bln)',
    }

    foverview = Overview()
    filters_dict = {'Market Cap.': market_cap['Large'], 'Country': 'USA'}
    foverview.set_filter(filters_dict=filters_dict)
    df = foverview.screener_view() 
    df['Alias']= df['Company'].apply(truncate_corporate_suffix)
    df.drop(columns = ['P/E', 'Change'], inplace = True)
    df.rename(columns = {'Market Cap': 'market_cap'}, inplace = True)
    df.to_csv(market_cap[size] + '.csv', index = False)
    return df


# TODO: make this save to a csv file so dont have to do it every time like the get_stock_list one. plan is to have this re-query every day
def news(df : pd.Series) -> pd.DataFrame:  # to be used for .apply()
    time.sleep(0.1)
    global news_df
    ignore = ['Insider Monkey', 'Motley Fool', "Investor's Business Daily"]

    finviz = finvizfinance(df['Ticker'])
    df1 = finviz.ticker_news()
    df1 = df1[df1['Date'] >= str(datetime.date.today())]    # get todays news
    df1 = df1[~df1['Source'].isin(ignore)]
    df1['Ticker'] = df['Ticker']
    df1.insert(0, 'Ticker', df1.pop('Ticker'))
    return df1




#get_stock_list()

# pro tip: always think about accomplish something via vectorized operations instead of iteration.

def get_news(DEBUG = True):
    logger.info('indexing news into database...')
    news_series = stocks.apply(news, axis=1)
    news_df = pd.concat(news_series.tolist(), ignore_index = True)
    news_df.to_csv('news.csv', index = False)       # don't write the index, because if read than Unnamed 0:
    return news_df






