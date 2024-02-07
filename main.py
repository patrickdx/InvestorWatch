import config
import praw 
import logging
import requests 
import datetime
import time
import nltk
import yfinance as yf 
from elasticsearch import Elasticsearch

def find_sentiment(sentence):   
    '''
    Determines the emotional value of a given expression in natural language. 
    Vader is optimized for social media data and can yield good results when used with data from twitter, facebook, etc, however more centric
    around words and not overall context of the sentence.
    1. TextBlob - 55%
    2. Vader - 56%
    3. ML Model - 78%
    '''

    from textblob import TextBlob    
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer        

    textblob = TextBlob(sentence)
    sid = SentimentIntensityAnalyzer()
    vader = sid.polarity_scores(sentence)      

    # https://github.com/cjhutto/vaderSentiment?tab=readme-ov-file#about-the-scoring
    if vader['compound'] >= 0.05  and textblob.polarity >= 0: 
        sentiment = 'positive'
    
    elif vader['compound'] <= -0.05 and textblob.polarity <= 0: 
        sentiment = 'negative'

    else: sentiment = 'netural'
    
    avg_polarity = (vader['compound'] + textblob.polarity) / 2
    logger.info(f"{sentiment}, {vader['compound']} , {textblob.polarity}")

    return {'sentiment': sentiment, 'polarity': avg_polarity, 'subjectivity' : textblob.subjectivity}
    


class NewsHeadlineIndexer: 
    
    def __init__(self):
        self.source = 'https://finance.yahoo.com/quote/%s/news?p=%s'
        self.filtered =0 
        self.accepted = 0

        self.stocks = config.tickers
        self.blacklist = config.author_blacklist
        

    def news_headlines(self, ticker):
        ''' 
        Indexes news headline documents using yfinance into its corresponding ticker index in elasticsearch. 
        '''
        stock = yf.Ticker(ticker)
        
        yf_logger.info(f"\n{ticker} news: " + str([news['title'] for news in stock.news]))

        for news in stock.news: 
            for word in self.stocks[ticker]:                
                if word.lower() in news['title'].lower() and news['publisher'] not in self.blacklist:

                    yf_logger.info('\n')
                    epoch = news['providerPublishTime']          # The time the article was published, represented as a Unix timestamp.
                    date = datetime.datetime.fromtimestamp(epoch) 

                    yf_logger.info(f"{date}, {news['title']}, {news['link']}, {news['publisher']}")
                    sentiment = find_sentiment(news['title'])

                    if sentiment['subjectivity'] >= 0.75: 
                        # Avoid: Magnificent Seven Stocks To Buy And Watch: Nvidia Stock Hits More Record Highs
                        yf_logger.info("Article is too subjective, discarding...")
                        self.filtered += 1
                        break
                   
                    # add to elasticsearch, assign unique uuid to prevent duplicates
                    yf_logger.info(es.index(index = 'stock-%s' % stock.lower(), id = news['uuid'], 
                        body = {
                            'date': date.isoformat(), 
                            'title': news['title'],
                            'polarity': sentiment['polarity'],
                            'sentiment': sentiment['sentiment'],
                            'url': news['link'],
                            'publisher' : news['publisher'],
                            'price': round(stock.info['currentPrice'],2),
                            'ticker': ticker
                        }))

                    self.accepted += 1
                    time.sleep(0.5)
                    break 
                else:
                    self.filtered += 1


def viewIndex(index): 
    ''' 
    Views the indexes/documents housed in the elastic search cluster
    or just visit http://localhost:9200/stock-tsla/_search?size=10000&pretty in your browser
    '''
    elasticsearch_url = "http://%s:%s@localhost:9200%s/_search?pretty"  % (config.es_user, config.es_password, index)
    response = requests.get(elasticsearch_url) 
    print(response.text)        

def clear_indexes():
    indices = es.indices.get_alias(index = "*")

    # Delete each index
    for index_name in indices:
        es.indices.delete(index=index_name, ignore=[400, 404])

    logger.info("All indices deleted.")

def initalize_indexes(ticker):
    '''Initalizes the indexes in elasticsearch if there is a new elasticsearch instance.'''

    from elasticsearch.exceptions import BadRequestError
    index_name = 'stock-%s' % ticker.lower()
    try: 
        es.indices.create(index= index_name, body=config.mapping)    
    except BadRequestError:
        yf_logger.debug(f"index {index_name} already exists")

    return index_name        


def stock_quote(ticker_name, date = None):           
    '''
    Gets a more accurate price quote, based on the time of release of an article.
    '''
    t = yf.Ticker(ticker_name)
    return round(t.info['currentPrice'], 2)

    if date: date = date.replace(second = 0)         # strip leading seconds 
    df = stock.history(start = date, interval = '1m')

    if len(df) > 0: 
        price_quote = df[df.index.time == date.time()].iloc[0]        # filter for time of published article
        print(date, price_quote, price_quote['Close'])
        # print(type(price_quote))
        return round(price_quote['Close'], 2)

    # else:    # return last close price if markets are closed
        
        
def remove_stopwords(text):
    '''
    Removes extremely common tokens that do not contribute much to the sentiment score.
    '''
    from nltk.corpus import stopwords 
    from nltk.tokenize import word_tokenize 

    tokens = word_tokenize(text) 
    stop_words = set(stopwords.words('english'))

    clean = [word for word in tokens if word not in stop_words]
    return " ".join(clean) 


class RedditIndexer: 
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id = config.client_id,
            client_secret = config.client_secret,
            user_agent= config.user_agent
        )    
        self.stocks = config.tickers

    def index_posts(self, subreddit='stocks'):
        subreddit = 'stocks'
        reddit = self.reddit 
        for submission in reddit.subreddit(subreddit).hot(limit = 25):
            for ticker, keywords in self.stocks.items():
                for word in keywords:  
                    if word in submission.title:   

                        reddit_logger.info(f'{ticker}: {submission.title}')
                        sentiment = find_sentiment(submission.title)
                        date = datetime.datetime.fromtimestamp(submission.created_utc)          # created_utc is unix timestamp 

                        # add to elasticsearch, assign unique uuid to prevent duplicates
                        reddit_logger.info(es.index(index = 'stock-%s' % ticker.lower(), id = submission.id, 
                            body = {
                                'date': date.isoformat(), 
                                'title': submission.title,
                                'polarity': sentiment['polarity'],
                                'sentiment': sentiment['sentiment'],
                                'url': submission.url, 
                                'publisher' : submission.author.name,
                                'price': stock_quote(ticker)      
                            }))

                        time.sleep(0.5)
                        break 



if __name__ == '__main__':      

    # setup logging 
    logging.basicConfig(format = '') 

    logger = logging.getLogger("investorwatch")
    logger.setLevel(logging.INFO)
    yf_logger = logging.getLogger("yfinance")
    yf_logger.setLevel(logging.INFO)
    reddit_logger = logging.getLogger("reddit")
    reddit_logger.setLevel(logging.INFO)
    

    
    # Setup elasticsearch, uncomment if you are using the cloud version. 
    es = Elasticsearch(     
        cloud_id = config.cloud_id,
        api_key= config.api_key
    )
    print(es.info())

    # local host version
    # es = Elasticsearch(hosts=[{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])
               

    for ticker in config.tickers:                
        initalize_indexes(ticker)

    # populate elasticsearch indices with news documents 
    headlines = NewsHeadlineIndexer()
    reddits = RedditIndexer() 

    for t in headlines.stocks:
        headlines.news_headlines(t)          # TODO: add logging summary of articles added to each index
    
