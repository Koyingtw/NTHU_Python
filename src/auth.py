import hashlib
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


import os
from dotenv import load_dotenv
load_dotenv()

import getpass # For password input

class Account:
    username = ""
    password = ""
    client = None
    db = None
    status = "logout"
    
    
    def __init__(self): # Initialize, connect to MongoDB Atlas
        print("Connecting to MongoDB Atlas...")
        uri = os.getenv('MONGODB_URI')
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.db = self.client.pymoney
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)
            
    def __del__(self): # Disconnect from MongoDB Atlas
        self.client.close()
        print("Disconnected from MongoDB Atlas.")
    
    def login(self): # login to your account and check if the password is correct
        self.username = input("Please enter your username: ")
        self.password = hashlib.md5(getpass.getpass("Please enter your password: ").encode(encoding='UTF-8')).hexdigest() 
                
        collection = self.db.users
        user = collection.find_one({"username": self.username})
        
        if user is None:
            print("User not found!")
        else:
            print(user["password"], self.password)
            if user["password"] == self.password:
                self.status = "login"
                print("Login successfully!")
            else:
                print("Wrong password!")
        
    def logout(self):
        self.username = ""
        self.password = ""
        self.status = "logout"
        
    def register(self):
        self.username = input("Please enter your username: ")
        self.password = hashlib.md5(getpass.getpass("Please enter your password: ").encode(encoding='UTF-8')).hexdigest() 
        
        collection = self.db.users
        user = collection.find_one({"username": self.username})
        if user is None:
            balance = int(input("How much money do you have? "))
            collection.insert_one({"username": self.username, "password": self.password, "balance": balance})
            self.db.create_collection(self.username)
            print("Register successfully!")
            
            self.login()
        else:
            print("User already exists!")

if __name__ == "__main__":
    account = Account()