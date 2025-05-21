from pymongo import MongoClient
from util import ROOT_DIR
import json 
from pymongo.server_api import ServerApi


# # Load the configuration file
# with open(ROOT_DIR / "config.json") as f: 
#     cfg = json.load(f) 


class Driver:
    '''
    Allows communication between application and MongoDB
    '''
    def __init__(self, username, password):    
        # MongoDB setup

        uri = f"mongodb+srv://{username}:{password}@cluster0.kuebdam.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi('1'))

        # Send a ping to confirm a successful connection
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)


        self.db = client['stocks']
        self.collection = self.db['articles']                               # a database stores s which in turn stores a bunch of documents.         

