import config
import praw 
import logging
import requests 
import datetime
import time
import nltk


def find_sentiment(sentence):   # TODO: Improve accuracy of these models or use a self-made one
    '''
    Determines the emotional value of a given expression in natural language. Uses textblob and Vader.
    Vader is optimized for social media data and can yield good results when used with data from twitter, facebook, etc, however more centric
    around words and not overall context of the sentence.
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
    import yfinance as yf 
    
    
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
        stock = self.yf.Ticker(ticker)
        index_name = self.create_index(ticker)
        
        yf_logger.info(f"\n{ticker} news: " + str([news['title'] for news in stock.news]))

        for news in stock.news: 

            # filter out low-quality articles, subject to change
            # tokens = nltk.word_tokenize(news['title'])
            match_tokens = self.stocks[ticker]

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
                   
                    stockPrice = self.stock_quote(stock, date)

                    # add to elasticsearch, assign unique uuid to prevent duplicates
                    yf_logger.info(es.index(index = index_name, id = news['uuid'], 
                        body = {
                            'date': date.isoformat(), 
                            'title': news['title'],
                            'polarity': sentiment['polarity'],
                            'sentiment': sentiment['sentiment'],
                            'url': news['link'],
                            'publisher' : news['publisher'],
                            'price': stockPrice     
                        }))

                    self.accepted += 1
                    time.sleep(0.5)
                    break 
                else:
                    self.filtered += 1
    

    def create_index(self, ticker):
        from elasticsearch.exceptions import BadRequestError
        index_name = 'stock-%s' % ticker.lower()
        try: 
            es.indices.create(index= index_name, body=config.mapping)    
        except BadRequestError:
            yf_logger.debug(f"index {index_name} already exists")

        return index_name        



class RedditIndexer: 
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id = config.client_id,
            client_secret = config.client_secret,
            user_agent= config.user_agent
        )    
        self.stocks = config.tickers

    def get_posts(self, subreddit):
        reddit = self.reddit 
        for submission in reddit.subreddit(subreddit).top(time_filter="month"):
            for ticker, keywords in self.stocks.items():
                for word in keywords:  
                    if word in submission.title:    #  index here

                        reddit_logger.info(f'{ticker}: {submission.title}')
                        sentiment = find_sentiment(submission.title)
                        index_name = self.create_index(ticker)
                        date = datetime.datetime.fromtimestamp(submission.created_utc)          # created_utc is unix timestamp 

                        # add to elasticsearch, assign unique uuid to prevent duplicates
                        yf_logger.info(es.index(index = index_name, id = submission.id, 
                            body = {
                                'date': date.isoformat(), 
                                'title': submission.title,
                                'polarity': sentiment['polarity'],
                                'sentiment': sentiment['sentiment'],
                                'url': submission.url, 
                                'publisher' : submission.author.name,
                                'price': stock_quote(ticker)      
                            }))

                        self.accepted += 1
                        time.sleep(0.5)
                        break 


# Setup elasticsearch, uncomment if you are using the cloud version. 

# es = Elasticsearch(     # for cloud subscription
#     cloud_id = config.cloud_id,
#     basic_auth =('elastic', config.password)
# )

from elasticsearch import Elasticsearch
es = Elasticsearch(hosts=[{'host': 'localhost', 'port': 9200, 'scheme': 'http'}],
                basic_auth =(config.es_user, config.es_password))



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


def stock_quote(self, stock : Ticker, date : datetime = None):           
    '''
    Gets a more accurate price quote, based on the time of release of an article.
    '''
    
    if date: date = date.replace(second = 0)         # strip leading seconds 
    df = stock.history(start = date, interval = '1m')

    if len(df) > 0: 
        price_quote = df[df.index.time == date.time()].iloc[0]        # filter for time of published article
        print(date, price_quote, price_quote['Close'])
        # print(type(price_quote))
        return round(price_quote['Close'], 2)

    else:   # return last close price if markets are closed
        return round(stock.info['currentPrice'], 2)
        


if __name__ == '__main__':      
    # populate elasticsearch indices with news documents 
    

    # setup logging 
    logging.basicConfig(format = '') 

    logger = logging.getLogger("investorwatch")
    logger.setLevel(logging.INFO)
    yf_logger = logging.getLogger("yfinance")
    yf_logger.setLevel(logging.INFO)
    reddit_logger = logging.getLogger("reddit")
    reddit_logger.setLevel(logging.INFO)
    

    headlines = NewsHeadlineIndexer()
    reddits = RedditIndexer() 
    for t in headlines.stocks:
        headlines.news_headlines(t)          # TODO: add logging summary of articles added to each index

