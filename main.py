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
    'APPL': ['APPL', '$APPL', 'Apple', 'IPhone'], 
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
    vader = analyzer.polarity_scores(sentence)      #
    # https://github.com/cjhutto/vaderSentiment?tab=readme-ov-file#about-the-scoring
    if vader['compound'] >= 0.05  and textblob.polarity >= 0: 
        sentiment = 'positive'
    
    elif vader['compound'] <= -0.05 and textblob.polarity <= 0: 
        sentiment = 'negative'

    else: sentiment = 'netural'

    
    avg_polarity = (vader['compound'] + textblob.polarity) / 2
    logger.info(f"{sentiment}, {vader['compound']} , {textblob.polarity}")
    return sentiment, avg_polarity
    

def elastic_index(ticker : str):
    from elasticsearch.exceptions import BadRequestError
    index_name = 'stock-%s' % ticker.lower()
    try: 
        es.indices.create(index= index_name, body=config.mapping)    
    except BadRequestError:
        logger.info(f"index {index_name} already exists")

    return index_name


def news_headlines(ticker : str):
    import yfinance as yf    
    import datetime

    source = 'https://finance.yahoo.com/quote/%s/news?p=%s' % (ticker, ticker)
    blacklist = ["Motley Fool", "Insider Monkey", "Investor's Business Daily"]
    stock = yf.Ticker(ticker)
    index_name = elastic_index(ticker)
    
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
                        'publisher' : news['publisher']
                    })
                
                break 

        





# for submission in reddit.subreddit("stocks").top(time_filter="month"):
#     for stock in whitelist:
#         for word in whitelist[stock]: 
#             if word in submission.title:
#                 # reddit_log.info(f'{stock}: {submission.title}')
#                 find_sentiment(submission.title)
#                 break 
    
# news_headlines('NVDA')




from elasticsearch import Elasticsearch

es = Elasticsearch(
    cloud_id = config.cloud_id,
    basic_auth =('elastic', config.password)
)

# populate elasticsearch indices with news documents 
for stock in keywords: 
    news_headlines(stock)