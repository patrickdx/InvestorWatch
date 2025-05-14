import os
import time
from finvizfinance.screener.overview import Overview
from finvizfinance.quote import finvizfinance
import pandas as pd
from datetime import datetime
from investor_watch.Driver import Driver
from investor_watch import db


def update_stock_list():   # update list of stocks that meet search criteria
    criteria = {
        'Market Cap.': '+Large (over $10bln)',
        'Country': 'Any'
    }

    foverview = Overview()
    foverview.set_filter(filters_dict=criteria)
    df = foverview.screener_view()
    df['Market Cap'] = df['Market Cap'] / 1e9
    df.drop(columns = ['P/E', 'Change', 'Volume'], inplace = True)

    # stock_list = db.read_stocks()
    # stock_list = pd.concat([df,stock_list]).drop_duplicates(subset=['Ticker'])        # dropped duplicates will be the older ones (in stock_list)
    return df
    
def gather_news(ticker):       # sinks new news sources to csv files
    try:
        time.sleep(0.2)
        whitelist = ['Bloomberg', 'Reuters']
        news_df = finvizfinance(ticker).ticker_news()
        news_df = news_df[news_df['Source'].isin(whitelist)]
        news_df['Ticker'] = ticker

        # get the latest date from the existing articles
        article_df = db.read_articles(ticker)
        
        # Check if article_df is empty before trying to get max date
        if not article_df.empty:
            latest_date = article_df['Date'].max()
            news_df = news_df[news_df['Date'] > latest_date]            # Filter news_df to only include new articles
        
        print(f'Found {len(news_df)} new sources of ${ticker} ...')
        return news_df

    except Exception as e:
        print("Error gathering news: ", ticker, e)
        return pd.DataFrame()  



def main():
    """Main function to update stocks and news."""
    print("Updating stocks and gathering news...")

    stock_list = update_stock_list()
    db.write_stocks(stock_list)
    stock_list = db.read_stocks()

    for ticker in stock_list['Ticker']:
        news_df = gather_news(ticker)
        db.write_articles(news_df)



# the entry point of the script
if __name__ == '__main__':
    main()
