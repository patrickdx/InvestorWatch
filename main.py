import config
import praw 
import logging
import requests 

logging.basicConfig(format = '')
logger = logging.getLogger("yfinance")
logger.setLevel(logging.INFO)


reddit = praw.Reddit(
        client_id = config.client_id,
        client_secret = config.client_secret,
        user_agent= config.user_agent
)

keywords = {
    'AAPL': ['APPL', '$APPL', 'Apple', 'IPhone'], 
    'NVDA': ['NVDA', '$NVDA', 'Nvidia', 'CUDA', 'Artifical Intelligence', 'Jensen Huang'],
    'MSFT': ['MSFT', '$MSFT', 'Microsoft', 'Satya Nadella', 'OpenAI'],
    'GOOGL': ['GOOGL', '$GOOG', '$GOOGL', 'Google', 'Alphabet', 'Gemini'],
    'TSLA': ['TSLA', '$TSLA', 'Tesla', 'Cybertruck', 'Starlink'],
    'AMZN': ['AMZN', '$AMZN', 'Amazon', 'Jeff Bezos', 'Prime'] 
}



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

    # https://github.com/cjhutto/vaderSentiment?tab=readme-ov-file#about-the-scoring
    if vader['compound'] >= 0.05  and textblob.polarity >= 0: 
        sentiment = 'positive'
    
    elif vader['compound'] <= -0.05 and textblob.polarity <= 0: 
        sentiment = 'negative'

    else: sentiment = 'netural'
    
    avg_polarity = (vader['compound'] + textblob.polarity) / 2
    logger.info(f"{sentiment}, {vader['compound']} , {textblob.polarity}")
    return sentiment, avg_polarity
    


class NewsHeadlineIndexer: 
    import yfinance as yf 
    
    def __init__(self):
        source = 'https://finance.yahoo.com/quote/%s/news?p=%s'


    def news_headlines(self, ticker):
        ''' 
        Indexes news headline document into its corresponding ticker index in elasticsearch. 
        '''
        # TODO: Get a more accurate price quote, based on the time of release of an article.
        
        import datetime

        blacklist = ["Motley Fool", "Insider Monkey"] # "Investor's Business Daily"
        stock = self.yf.Ticker(ticker)
        index_name = self.create_index(ticker)
        
        logger.info(f"{ticker} news: " + str([news['title'] for news in stock.news]))

        for news in stock.news: 

            # filter out low-quality articles 
            for word in keywords[ticker]: 
                if word.lower() in news['title'].lower() and news['publisher'] not in blacklist:

                    epoch = news['providerPublishTime']          # The time the article was published, represented as a Unix timestamp.
                    date = datetime.datetime.fromtimestamp(epoch).isoformat()

                    logger.info(f"{date}, {news['title']}, {news['link']}, {news['publisher']}")
                    sentiment = find_sentiment(news['title'])

                    # add to elasticsearch, assign unique uuid to prevent duplicates
                    es.index(index = index_name, id = news['uuid'], 
                        body = {
                            'date': date, 
                            'title': news['title'],
                            'polarity': sentiment[1],
                            'sentiment': sentiment[0],
                            'url': news['link'],
                            'publisher' : news['publisher'],
                            'price': stock.info['currentPrice']     
                        })
                    
                    break 



    def create_index(self, ticker):
        from elasticsearch.exceptions import BadRequestError
        index_name = 'stock-%s' % ticker.lower()
        try: 
            es.indices.create(index= index_name, body=config.mapping)    
        except BadRequestError:
            logger.debug(f"index {index_name} already exists")

        return index_name        

    def stock_quote(ticker, timestamp): 

        
        pass          



# for submission in reddit.subreddit("stocks").top(time_filter="month"):
#     for stock in whitelist:
#         for word in whitelist[stock]: 
#             if word in submission.title:
#                 # reddit_log.info(f'{stock}: {submission.title}')
#                 find_sentiment(submission.title)
#                 break 
    
# news_headlines('NVDA')


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
    or just visit http://localhost:9200/stock-tsla/_search?pretty in your browser
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
    for stock in keywords: 
        news_headlines(stock)

