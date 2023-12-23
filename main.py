import config
import praw 
import logging
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
    textblob = TextBlob(sentence)

    # Vader is optimized for social media data and can yield good results when used with data from twitter, facebook, etc.
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer    
    analyzer = SentimentIntensityAnalyzer()
    vader = analyzer.polarity_scores(sentence)
    

    if vader['compound'] > 0  and textblob.polarity > 0: 
        sentiment = 'positive'
    
    elif vader['compound'] < 0 and textblob.polarity < 0: 
        sentiment = 'negative'

    else: sentiment = 'netural'

    print(textblob, textblob.sentiment, vader, sentiment)
    avg_polarity = (vader['compound'] + textblob.polarity) / 2
    
    return sentiment, avg_polarity
    





for submission in reddit.subreddit("stocks").top(time_filter="month"):
    for stock in whitelist:
        for word in whitelist[stock]: 
            if word in submission.title:
                # reddit_log.info(f'{stock}: {submission.title}')
                find_sentiment(submission.title)
                break 
    




