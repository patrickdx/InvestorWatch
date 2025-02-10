import logging
import requests 
import datetime
import time
import pandas as pd
import yfinance as yf 


stock = 'GOOGL'
PATH = 'stocks/tickers'

# lookup stock in file 
file = f'{PATH}/{stock}.csv'
df = pd.read_csv(file, parse_dates=['Date'])


# calculate daily return in yfinance
def get_intraday_return(stock):
    data = yf.download(stock, period = '1mo', interval = '1d')
    data.columns = data.columns.droplevel(1)

    data['Prev Close'] = data['Close'].shift(1)     # get previous close by shifting it down by 1
    data['% Change'] = ((data['Close'] - data['Prev Close']) / data['Prev Close'])  * 100
    data['% Change'] = data['% Change'].round(2)


    print(data)
    return data

df = get_intraday_return('GOOGL')
df.sort_values('% Change', ascending = False).head(5)











