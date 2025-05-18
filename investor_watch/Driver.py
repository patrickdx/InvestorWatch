from pymongo import MongoClient

class Driver:
    '''
    Allows communication between application and MongoDB
    '''
    def __init__(self):
        self.client = MongoClient("localhost", 27017)
        self.db = self.client.stocks 
        self.collection = self.db.articles                   # a database stores collections which in turn stores a bunch of documents.         

    # def insert_document(self):
    #     sample_doc = {"name": "Investor A", "investment": 10000, "active": True}
    #     result = self.collection.insert_one(sample_doc)
    #     print(f"Inserted document with _id: {result.inserted_id}")

    # def print_all_documents(self):
    #     for doc in self.collection.find():
    #         print(doc)

