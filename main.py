import config
import praw 
import logging
import requests 

logging.basicConfig(format = '', level = logging.INFO)


reddit = praw.Reddit(
        client_id = config.client_id,
        client_secret = config.client_secret,
        user_agent= config.user_agent
)

whitelist = {
    'APPL': ['$APPL', 'Apple', 'IPhone'], 
    'NVDA': ['$NVDA', 'Nvidia', 'CUDA', 'AI', '$TSMC'],
    'MSFT': ['$MSFT', 'Microsoft', 'Satya Nadella', 'OpenAI'],
    'GOOGL': ['$GOOG', '$GOOGL', 'Google', 'Alphabet', 'Gemini'],
    'TSLA': ['$TSLA', 'Tesla', 'Cybertruck']

}

reddit_log = logging.getLogger("reddit")
reddit_log.setLevel(logging.INFO)


def find_sentiment(sentence):   
    '''
    Determines the emotional value of a given expression in natural language. 
    Uses textblob and Vader https://neptune.ai/blog/sentiment-analysis-python-textblob-vs-vader-vs-flair
    '''

    from textblob import TextBlob    
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer        # Vader is optimized for social media data and can yield good results when used with data from twitter, facebook, etc.

    textblob = TextBlob(sentence)

    
    analyzer = SentimentIntensityAnalyzer()
    vader = analyzer.polarity_scores(sentence)
    

    if vader['compound'] > 0  and textblob.polarity > 0: 
        sentiment = 'positive'
    
    elif vader['compound'] < 0 and textblob.polarity < 0: 
        sentiment = 'negative'

    else: sentiment = 'netural'

    
    avg_polarity = (vader['compound'] + textblob.polarity) / 2

    print(avg_polarity, textblob)
    return sentiment, avg_polarity
    

def news_headlines(ticker):
    from bs4 import BeautifulSoup

    source = 'https://finance.yahoo.com/quote/%s/news?p=%s' % (ticker, ticker)         # scrape from yahoo finance landing page 
    header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0'}

    filter = []                                                     # to filter out the low-quality articles
    
    html = requests.get(source, headers = header)
    soup = BeautifulSoup(html.text, 'html.parser')
    soup.find_all('h3')






# for submission in reddit.subreddit("stocks").top(time_filter="month"):
#     for stock in whitelist:
#         for word in whitelist[stock]: 
#             if word in submission.title:
#                 # reddit_log.info(f'{stock}: {submission.title}')
#                 find_sentiment(submission.title)
#                 break 
    

from bs4 import BeautifulSoup
import time 

ticker = 'AAPL' 
source = 'https://finance.yahoo.com/quote/%s/news?p=%s' % (ticker, ticker)         # scrape from yahoo finance landing page 
header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0'}

filter = []                                                     # to filter out the low-quality articles

html = requests.get(source, headers = header)
time.sleep(5)
soup = BeautifulSoup(html.text, 'html.parser')
print(soup.find_all('h3'))






def main():
    pass

if __name__ == '__main__':
    main() 
