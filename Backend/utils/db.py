import datetime
import pymongo
import json
import logging
from bson.json_util import dumps


myclient = pymongo.MongoClient("mongodb://mongodb:27017/")
mydb = myclient["shyamDB"]


def write_data_in_db(data):
    logging.warning(myclient)
    mycol = mydb["crypto"]
    data['cipher_text'] = str(data['cipher_text'])
    data['created_at'] = datetime.datetime.now()
    logging.warning(data)
    return mycol.insert_one(data)


def query_data_from_db(query):
    logging.warning("db query")
    logging.warning(type(query))
    logging.warning(query)
    logging.warning(dumps(mydb["crypto"].find({'cipher_text': str(query)})))
    return json.loads(dumps(mydb["crypto"].find({'cipher_text': str(query)})))
