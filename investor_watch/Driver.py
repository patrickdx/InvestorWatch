import os
from pymongo import MongoClient
from util import ROOT_DIR
import json 
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Driver:
    '''
    Allows communication between application and MongoDB
    Uses environment variables for secure credential management
    '''
    def __init__(self):    
        # Get MongoDB credentials from environment variables
        username = os.getenv('MONGODB_USERNAME')
        password = os.getenv('MONGODB_PASSWORD')
        cluster = os.getenv('MONGODB_CLUSTER', 'cluster0.kuebdam.mongodb.net')
        database = os.getenv('MONGODB_DATABASE', 'stocks')
        collection_name = os.getenv('MONGODB_COLLECTION', 'articles')
        
        if not username or not password:
            raise ValueError("MongoDB credentials not found. Please set MONGODB_USERNAME and MONGODB_PASSWORD environment variables.")
        
        # MongoDB setup
        uri = f"mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority&appName=Cluster0"

        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi('1'))

        # Send a ping to confirm a successful connection
        try:
            client.admin.command('ping')
            print("Pinged your deployment. MongoDB connection successful.")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise

        self.db = client[database]
        self.collection = self.db[collection_name]         

Driver()