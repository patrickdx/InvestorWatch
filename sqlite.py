import sqlite3
import pandas as pd
from source import stocks, news
import source
import os 
from util import logger

FILENAME = 'stocks.db'

def setup():
    '''
    For first time setup of the database...
    '''
    logger.info("Setting up database...")

    db = sqlite3.connect(FILENAME)
    cursor = db.cursor()            
    
    # setup schema
    cursor.execute(
    '''    
        CREATE TABLE IF NOT EXISTS stocks (
        ticker text PRIMARY KEY,
        company text NOT NULL, 
        sector text NOT NULL, 
        industry text not NULL, 
        country text not NULL, 
        market_cap real, 
        price real, 
        volume INTEGER, 
        alias text 
        );
    ''') 

    cursor.execute(
    '''
        CREATE TABLE IF NOT EXISTS news (
            article_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique identifier for each article
            ticker TEXT,                                  -- Foreign key referencing the stocks table
            date DATE,                                    -- Publication date of the article
            title TEXT NOT NULL,                          -- Title of the article
            link TEXT NOT NULL,                           -- URL of the article
            source TEXT,                                  -- Source or publisher of the article
            FOREIGN KEY (ticker) REFERENCES stocks(ticker)  -- Foreign key constraint (optional)
            
    );
    ''')

    stocks = source.get_stock_list() 
    stocks.to_sql('stocks', db, if_exists='append', index = False)
    return db, cursor
    

def update(db, cursor): 
    '''
    update db with newly generated articles
    '''

    news = source.get_news(DEBUG = False)

    def check_unique(row):
        '''check if news article is already indexed into db'''
        title = row['Title']
        ticker = row['Ticker']

        sql = f"SELECT * from news where title = \"{title}\" and ticker = \"{ticker}\""
        results = cursor.execute(sql).fetchall()
        string = f"{ticker}: {title}"
        if len(results) != 0: 
            logger.info('dupe found %s', string)
            return False
        logger.info('indexed %s', string)
        return True
    
    unique = news[news.apply(check_unique, axis=1)]
    unique.to_sql('news', db, if_exists='append', index = False)

    return unique

        

def table_exists(name) -> bool:
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{name}'")
    return bool(cursor.fetchone())




if not os.path.exists(FILENAME):    # need to always have the preconfig schema set before
    db, cursor = setup()
else:
    db = sqlite3.connect(FILENAME)
    cursor = db.cursor()            

df = update(db,cursor)



db.commit()
db.close() 