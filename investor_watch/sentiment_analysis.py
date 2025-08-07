import pandas as pd
from Driver import Driver
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import numpy as np
from tqdm import tqdm
import time

'''
Script to add sentiment analysis to article titles in the MongoDB database.
Uses cardiffnlp/twitter-roberta-base-sentiment model for classification.
'''

class SentimentAnalyzer:
    def __init__(self):
        """Initialize the sentiment analysis model."""
        print("Loading sentiment analysis model...")
        
        # Load the pre-trained model and tokenizer
        model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        # Labels for the model output
        self.labels = ['negative', 'neutral', 'positive']
        
        print("Model loaded successfully!")
    
    def analyze_sentiment(self, text):
        """
        Analyze sentiment of a given text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Contains sentiment label, confidence score, and all scores
        """
        try:
            # Tokenize and encode the text
            encoded_text = self.tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
            
            # Get model predictions
            output = self.model(**encoded_text)
            scores = output[0][0].detach().numpy()
            scores = softmax(scores)
            
            # Get the predicted sentiment
            predicted_label = self.labels[np.argmax(scores)]
            confidence = float(np.max(scores))
            
            # Create scores dictionary
            scores_dict = {
                'negative': float(scores[0]),
                'neutral': float(scores[1]),
                'positive': float(scores[2])
            }
            
            return {
                'sentiment': predicted_label,
                'confidence': confidence,
                'scores': scores_dict
            }
            
        except Exception as e:
            print(f"Error analyzing sentiment for text: {text[:50]}... Error: {e}")
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'scores': {'negative': 0.33, 'neutral': 0.34, 'positive': 0.33}
            }
    
    def batch_analyze(self, texts, batch_size=32):
        """
        Analyze sentiment for multiple texts in batches.
        """
        results = []
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Processing batches"):
            batch = texts[i:i + batch_size]
            batch_results = []
            
            for text in batch:
                result = self.analyze_sentiment(text)
                batch_results.append(result)
                
            results.extend(batch_results)            
            time.sleep(0.1)

            
        return results

def add_sentiment_to_database(limit=None, batch_size=32):
    """
    Add sentiment analysis to articles in the database.
    
    Args:
        limit (int): Limit number of articles to process (None for all)
        batch_size (int): Number of articles to process in each batch
    """
    print("Starting sentiment analysis for database articles...")
    
    try:
        # Initialize database connection and sentiment analyzer
        driver = Driver()
        analyzer = SentimentAnalyzer()
        
        # Find articles that don't have sentiment analysis yet
        query = {"sentiment": {"$exists": False}}
        
        if limit:
            cursor = driver.collection.find(query).limit(limit)
        else:
            cursor = driver.collection.find(query)
        
        articles = list(cursor)
        
        if not articles:
            print("No articles found without sentiment analysis.")
            return
        
        print(f"Found {len(articles)} articles to analyze...")
        
        # Extract titles for batch processing
        titles = [article.get('title', '') for article in articles]
        
        # Perform sentiment analysis
        sentiment_results = analyzer.batch_analyze(titles, batch_size=batch_size)
        
        # Update database with sentiment results
        print("Updating database with sentiment results...")
        
        updated_count = 0
        for article, sentiment_result in tqdm(zip(articles, sentiment_results), 
                                            desc="Updating database", 
                                            total=len(articles)):
            try:
                # Update the article with sentiment information (polarity only)
                update_data = {
                    'sentiment': sentiment_result['sentiment']
                }
                
                driver.collection.update_one(
                    {'_id': article['_id']},
                    {'$set': update_data}
                )
                updated_count += 1
                
            except Exception as e:
                print(f"Error updating article {article.get('_id')}: {e}")
        
        print(f"Successfully updated {updated_count} articles with sentiment analysis!")
        
    except Exception as e:
        print(f"Error in sentiment analysis process: {e}")

if __name__ == '__main__':
    # Add sentiment analysis to all articles without sentiment
    add_sentiment_to_database()
    
    # Uncomment below to test with a single title:
    # analyze_single_title("Apple stock soars to new record high after strong earnings report")
    
    # Uncomment below to process only a limited number of articles (for testing):
    # add_sentiment_to_database(limit=100)
