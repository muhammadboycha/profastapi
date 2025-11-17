import pymongo 
from pymongo import MongoClient
from dotenv import load_dotenv
import os


def dbConnect():
    dbcont =  MongoClient(os.getenv("MONGO_URI"))
    db = dbcont["mern"]
    users = db["users"] 
    return users