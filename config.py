# insert preferences and api credentials here

# reddit creds
client_id = ''
client_secret = ''
user_agent = 'stonks/v1.0.0 (by patrickdx)'   # unique id for reddit for identifying source of network requests.
api_key = ''
cloud_id = ''
password = ''

# elasticsearch localhost creds
es_user = ''
es_password = ''
es_host = ""
es_port = 9200
 
mapping = {
    "mappings": {
        "properties": {
            "date": {
                "type": "date"
            },
            "title": {               
                "type": "text",     
            },
            "polarity": {
                "type": "float"
            },
            "sentiment": {
                "type": "keyword"     # https://www.elastic.co/blog/strings-are-dead-long-live-strings
            },
            "url":{
                "type": "keyword"
            }, 
            "publisher":{
                "type": "keyword"
            },
            "price" : {
                "type": "float"
            }
        }        
    }
}


# list of stock tickers to gather information on 
stocks = {
        'AAPL': ['APPL', '$APPL', 'Apple', 'IPhone'], 
        'NVDA': ['NVDA', '$NVDA', 'Nvidia', 'CUDA', 'Artifical Intelligence', 'Jensen Huang'],
        'MSFT': ['MSFT', '$MSFT', 'Microsoft', 'Satya Nadella', 'OpenAI'],
        'GOOGL': ['GOOGL', '$GOOG', '$GOOGL', 'Google', 'Alphabet', 'Gemini'],
        'TSLA': ['TSLA', '$TSLA', 'Tesla', 'Cybertruck', 'Starlink'],
        'AMZN': ['AMZN', '$AMZN', 'Amazon', 'Jeff Bezos', 'Prime'] 
    }

author_blacklist = ["Motley Fool", "Insider Monkey", "Investor's Business Daily"]

