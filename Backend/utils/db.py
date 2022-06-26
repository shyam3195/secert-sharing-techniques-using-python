import datetime
import pymongo
import json
import logging
from bson.json_util import dumps


myclient = pymongo.MongoClient("mongodb://mongodb:27017/")
mydb = myclient["shyamDB"]


def write_data_in_db(data, dbName):
    logging.warning(myclient)
    mycol = mydb[dbName]
    data['cipher_text'] = str(data['cipher_text'])
    data['created_at'] = datetime.datetime.now()+datetime.timedelta(2)
    return mycol.insert_one(data)


def query_data_from_db(query, dbName):
    return json.loads(dumps(mydb[dbName].find({
        'cipher_text': str(query)})))
