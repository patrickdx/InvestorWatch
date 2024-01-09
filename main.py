import config
import praw 
import logging
import requests 
import datetime
import time
import nltk

logging.basicConfig(format = '')
logger = logging.getLogger("yfinance")
logger.setLevel(logging.INFO)







def find_sentiment(sentence):   # TODO: Improve accuracy of these models or use a self-made one
    '''
    Determines the emotional value of a given expression in natural language. 
    Uses textblob and Vader https://neptune.ai/blog/sentiment-analysis-python-textblob-vs-vader-vs-flair
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

        # self.keywords = config.keywords 
        self.keywords = {
            'AAPL': ['APPL', '$APPL', 'Apple', 'IPhone'], 
            'NVDA': ['NVDA', '$NVDA', 'Nvidia', 'CUDA', 'Artifical Intelligence', 'Jensen Huang'],
            'MSFT': ['MSFT', '$MSFT', 'Microsoft', 'Satya Nadella', 'OpenAI'],
            'GOOGL': ['GOOGL', '$GOOG', '$GOOGL', 'Google', 'Alphabet', 'Gemini'],
            'TSLA': ['TSLA', '$TSLA', 'Tesla', 'Cybertruck', 'Starlink'],
            'AMZN': ['AMZN', '$AMZN', 'Amazon', 'Jeff Bezos', 'Prime'] 
        }

        self.blacklist = ["Motley Fool", "Insider Monkey", "Investor's Business Daily"]




    def news_headlines(self, ticker):
        ''' 
        Indexes news headline document into its corresponding ticker index in elasticsearch. 
        '''
        

        stock = self.yf.Ticker(ticker)
        index_name = self.create_index(ticker)
        
        logger.info(f"\n{ticker} news: " + str([news['title'] for news in stock.news]))

        for news in stock.news: 

            # filter out low-quality articles, subject to change
            tokens = nltk.word_tokenize(news['title'])
            match_tokens = self.keywords[ticker]

            for word in keywords[ticker]:                
                if word.lower() in news['title'].lower() and news['publisher'] not in self.blacklist:

                    logger.info('\n')
                    epoch = news['providerPublishTime']          # The time the article was published, represented as a Unix timestamp.
                    date = datetime.datetime.fromtimestamp(epoch) 

                    logger.info(f"{date}, {news['title']}, {news['link']}, {news['publisher']}")
                    sentiment = find_sentiment(news['title'])

                    if sentiment['subjectivity'] >= 0.75: 
                        # Avoid: Magnificent Seven Stocks To Buy And Watch: Nvidia Stock Hits More Record Highs
                        logger.info("Article is too subjective, discarding...")
                        self.filtered += 1
                        break
                   
                    stockPrice = self.stock_quote(stock, date)

                    # add to elasticsearch, assign unique uuid to prevent duplicates
                    logger.info(es.index(index = index_name, id = news['uuid'], 
                        body = {
                            'date': date.isoformat(), 
                            'title': news['title'],
                            'polarity': sentiment[1],
                            'sentiment': sentiment[0],
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
            logger.debug(f"index {index_name} already exists")

        return index_name        

    def stock_quote(self, stock, date : datetime):           
        '''
        TODO: Get a more accurate price quote, based on the time of release of an article.
        '''
        df = stock.history(start = date, interval = '1m')

        if len(df) > 0: 
            price_quote = df[df.index.time == date.time()].iloc[0]               # filter for time of published article
            # print(type(price_quote))
            return price_quote['Close']

        else:   # return last close price if markets are closed
            return stock.info['currentPrice']
        


class RedditIndexer: 
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id = config.client_id,
            client_secret = config.client_secret,
            user_agent= config.user_agent
        )    

    def get_posts(subreddit):
        for submission in reddit.subreddit("stocks").top(time_filter="month"):
            for stock in whitelist:
                for word in whitelist[stock]: 
                    if word in submission.title:
                        # reddit_log.info(f'{stock}: {submission.title}')
                        find_sentiment(submission.title)
                        break 
                        #  index here
                



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

if __name__ == '__main__':      
    # populate elasticsearch indices with news documents 
    news = NewsHeadlineIndexer()

    for stock in news.keywords: 
        news.news_headlines(stock)      # TODO: add summary of articles added to each index


