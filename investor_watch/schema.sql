-- Schema for stock database 

-- Stocks table
CREATE TABLE IF NOT EXISTS stocks (
    ticker VARCHAR(10) PRIMARY KEY,
    company VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap NUMERIC(15, 2),  -- In billions
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- News articles table
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) REFERENCES stocks(ticker) ON DELETE CASCADE,
    date TIMESTAMP NOT NULL,
    title VARCHAR(500) NOT NULL,
    link TEXT NOT NULL,
    source VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, link)  -- Prevent duplicate articles
);


