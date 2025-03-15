from flask import Flask, jsonify, send_from_directory
import os
import sys
import pandas as pd
from datetime import datetime
from investor_watch.Driver import Driver

# Add parent directory to path to import from investor_watch
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__, static_folder='.')

# Initialize database connection
db = Driver()

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Serve static files"""
    return send_from_directory('.', path)

@app.route('/api/stocks')
def get_stocks():
    """Get all stocks from the database"""
    stocks_df = db.read_stocks()
    # Convert DataFrame to a list of dictionaries and return as JSON
    return jsonify(stocks_df.to_dict(orient='records'))
    

@app.route('/api/news/<ticker>')
def get_news(ticker):
    """Get news for a specific stock"""
    try:
        ticker = ticker.upper()
        articles_df = db.read_articles(ticker)
        
        if articles_df.empty:
            return jsonify({'error': 'Stock not found'}), 404
        
        return jsonify(articles_df.to_dict(orient='records'))
    except Exception as e:
        print(f"Error fetching stock details for {ticker}: {e}")
        return jsonify({'error': str(e)}), 500

    
@app.route('/api/stock/<ticker>')
def get_stock(ticker):
    """Get stock details for a specific stock"""
    ticker = ticker.upper()
    stock_df = db.read_stocks()
    stock = stock_df[stock_df['Ticker'] == ticker]
    return jsonify(stock.to_dict(orient='records'))

        

if __name__ == '__main__':
    app.run(debug=True, port=5000) 