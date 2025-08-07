import pandas as pd
from Driver import Driver
from datetime import datetime

'''
Script to export 500 article titles from the MongoDB database to a CSV file.
Useful for analysis, sentiment analysis, or data exploration.
'''

def export_titles_to_csv(limit=100, output_file='article_titles.csv'):
    """
    Exports article titles from MongoDB to a CSV file.
    
    Args:
        limit (int): Number of titles to export (default: 500)
        output_file (str): Name of the output CSV file
    """
    print(f"Connecting to database and fetching {limit} article titles...")
    
    try:
        # Initialize database connection
        driver = Driver()
        
        # Query the database for articles, limiting to specified number
        # Sort by date (newest first) to get most recent articles
        cursor = driver.collection.find(
            {},  # No filter - get all articles
            {
                'title': 1,
                'ticker': 1, 
                'date': 1,
                'source': 1,
                'link': 1,
                '_id': 0  # Exclude MongoDB's _id field
            }
        ).sort('date', -1).limit(limit)
        
        # Convert cursor to list
        articles = list(cursor)
        
        if not articles:
            print("No articles found in the database.")
            return
        
        # Create DataFrame
        df = pd.DataFrame(articles)
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        
        print(f"Successfully exported {len(articles)} article titles to '{output_file}'")
        print(f"Columns: {list(df.columns)}")
        
        # Display sample of the data
        print("\nSample of exported data:")
        print(df.head())
        
    except Exception as e:
        print(f"Error exporting titles: {e}")

def export_titles_by_ticker(ticker, limit=100, output_file=None):
    """
    Exports article titles for a specific ticker.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')
        limit (int): Number of titles to export
        output_file (str): Output filename (auto-generated if None)
    """
    if output_file is None:
        output_file = f'{ticker}_titles.csv'
    
    print(f"Fetching {limit} article titles for {ticker}...")
    
    try:
        driver = Driver()
        
        # Query for specific ticker
        cursor = driver.collection.find(
            {'ticker': ticker},
            {
                'title': 1,
                'ticker': 1,
                'date': 1,
                'source': 1,
                'link': 1,
                '_id': 0
            }
        ).sort('date', -1).limit(limit)
        
        articles = list(cursor)
        
        if not articles:
            print(f"No articles found for ticker {ticker}")
            return
        
        df = pd.DataFrame(articles)
        df.to_csv(output_file, index=False)
        
        print(f"Successfully exported {len(articles)} titles for {ticker} to '{output_file}'")
        
    except Exception as e:
        print(f"Error exporting titles for {ticker}: {e}")

def export_recent_titles(days=30, output_file='recent_titles.csv'):
    """
    Exports article titles from the last N days.
    
    Args:
        days (int): Number of days back to fetch articles
        output_file (str): Output filename
    """
    from datetime import datetime, timedelta
    
    # Calculate date threshold
    date_threshold = datetime.now() - timedelta(days=days)
    
    print(f"Fetching article titles from the last {days} days...")
    
    try:
        driver = Driver()
        
        cursor = driver.collection.find(
            {'date': {'$gte': date_threshold}},
            {
                'title': 1,
                'ticker': 1,
                'date': 1,
                'source': 1,
                'link': 1,
                '_id': 0
            }
        ).sort('date', -1)
        
        articles = list(cursor)
        
        if not articles:
            print(f"No articles found in the last {days} days")
            return
        
        df = pd.DataFrame(articles)
        df.to_csv(output_file, index=False)
        
        print(f"Successfully exported {len(articles)} recent titles to '{output_file}'")
        
    except Exception as e:
        print(f"Error exporting recent titles: {e}")

if __name__ == '__main__':
    # Default: Export 500 titles
    export_titles_to_csv()
    
    # Uncomment below for other export options:
    
    # Export titles for a specific stock
    # export_titles_by_ticker('AAPL', limit=50)
    
    # Export recent titles (last 7 days)
    # export_recent_titles(days=7)
