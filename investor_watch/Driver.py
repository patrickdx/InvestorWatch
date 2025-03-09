import psycopg2 
import pandas as pd
from psycopg2 import sql

class Driver:
    """PostgreSQL database driver for InvestorWatch."""
    
    def __init__(self, dbname="postgres", user="postgres", password="password", host="localhost", port="5432"):
        try:
            self.conn = psycopg2.connect(
                dbname=dbname, 
                user=user, 
                password=password, 
                host=host, 
                port=port
            )
            self.cur = self.conn.cursor()
            self._create_tables()
        except Exception as e:
            print(f"Database connection error: {str(e)}")
            raise

    def _create_tables(self):
        """Create the necessary tables if they don't exist."""
        table_schema = '''
        CREATE TABLE IF NOT EXISTS stocks (
            ticker VARCHAR(10) PRIMARY KEY,
            company VARCHAR(255) NOT NULL,
            sector VARCHAR(100),
            industry VARCHAR(100),
            country VARCHAR(100),
            price NUMERIC(10, 2) CHECK (price >= 0),
            market_cap NUMERIC(10, 2) CHECK (market_cap >= 0)
        );

        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            ticker VARCHAR(10) REFERENCES stocks(ticker) ON DELETE CASCADE,
            date TIMESTAMP NOT NULL,
            title VARCHAR(255) NOT NULL,
            link TEXT NOT NULL,
            source VARCHAR(100) NOT NULL,
            UNIQUE (ticker, date, title)                                    
        );
        '''
        
        self.cur.execute(table_schema)
        self.conn.commit()
        print("Tables initialized successfully")
        return True

    def write_articles(self, articles_df):
        """Add new articles to the articles table."""
        if articles_df.empty:
            print("No articles to write")
            return 0
            
        required_columns = ['Ticker', 'Date', 'Title', 'Link', 'Source']
        if not all(col in articles_df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in articles_df.columns]
            print(f"Missing required columns: {missing}")
            return 0
            
        try:
            articles_added = 0
            for _, row in articles_df.iterrows():
                try:
                    insert_query = '''
                    INSERT INTO articles (Ticker, Date, Title, Link, Source)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (Ticker, Date, Title) DO NOTHING
                    '''
                    
                    self.cur.execute(insert_query, (
                        row['Ticker'],
                        row['Date'],
                        row['Title'],
                        row['Link'],
                        row['Source']
                    ))
                    
                    if self.cur.rowcount > 0:
                        articles_added += 1
                        
                except Exception as e:
                    print(f"Error inserting article: {str(e)}")
                    continue
                    
            self.conn.commit()
            print(f"Added {articles_added} new articles to database")
            return articles_added
            
        except Exception as e:
            self.conn.rollback()
            print(f"Error writing articles: {str(e)}")
            return 0

    def write_stocks(self, stocks_df):
        """Add new stocks to the stocks table."""
        if stocks_df.empty:
            print("No stocks to write")
            return 0
            
        required_columns = ['Ticker', 'Company']
        if not all(col in stocks_df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in stocks_df.columns]
            print(f"Missing required columns: {missing}")
            return 0
            
        try:
            stocks_added = 0
            for _, row in stocks_df.iterrows():
                try:
                    ticker = row['Ticker']
                    company = row['Company']
                    sector = row['Sector']
                    industry = row['Industry']
                    country = row['Country']
                    price = row['Price']
                    market_cap = row['Market Cap']
                    
                    insert_query = '''          
                    INSERT INTO stocks (ticker, company, sector, industry, country, price, market_cap)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (ticker) DO UPDATE SET
                        company = EXCLUDED.company,
                        sector = EXCLUDED.sector,
                        industry = EXCLUDED.industry,
                        country = EXCLUDED.country,
                        price = EXCLUDED.price,
                        market_cap = EXCLUDED.market_cap
                    '''
                    
                    self.cur.execute(insert_query, (
                        ticker, company, sector, industry, country, price, market_cap
                    ))
                    
                    if self.cur.rowcount > 0:
                        stocks_added += 1
                        
                except Exception as e:
                    print(f"Error inserting stock {row.get('Ticker', 'unknown')}: {str(e)}")
                    continue
                    
            self.conn.commit()
            print(f"Added/updated {stocks_added} stocks in database")
            return stocks_added
            
        except Exception as e:
            self.conn.rollback()
            print(f"Error writing stocks: {str(e)}")
            return 0

    def read_articles(self, ticker, limit=50):
        """Get articles for a specific stock."""
        try:
            query = '''
            SELECT a.ticker, a.date, a.title, a.link, a.source
            FROM articles a
            WHERE a.ticker = %s
            ORDER BY a.date DESC
            '''
            
            self.cur.execute(query, (ticker,))
            results = self.cur.fetchall()
            
            if not results:
                print(f"No articles found for {ticker}")
                return pd.DataFrame()
                
            df = pd.DataFrame(results, columns=['Ticker', 'Date', 'Title', 'Link', 'Source'])
            print(f"Retrieved {len(df)} articles for {ticker}")
            return df
            
        except Exception as e:
            print(f"Error getting articles for {ticker}: {str(e)}")
            return pd.DataFrame()
        
    def read_stocks(self):
        """Read all stocks from the database."""
        try:
            query = '''
            SELECT ticker, company, sector, industry, country, market_cap
            FROM stocks
            ORDER BY market_cap DESC
            '''
            
            self.cur.execute(query)
            results = self.cur.fetchall()
            
            if not results:
                print("No stocks found in database")
                return pd.DataFrame()
                
            df = pd.DataFrame(results, columns=['Ticker', 'Company', 'Sector', 'Industry', 'Country', 'Market Cap'])
            print(f"Retrieved {len(df)} stocks from database")
            return df
            
        except Exception as e:
            print(f"Error reading stocks: {str(e)}")
            return pd.DataFrame()

    def close(self):
        """Close database connection."""
        try:
            if self.cur:
                self.cur.close()
            if self.conn:
                self.conn.close()
            print("Database connection closed")
        except Exception as e:
            print(f"Error closing database connection: {str(e)}")

