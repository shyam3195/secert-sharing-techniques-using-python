import datetime
import pymongo
import json
import logging
from bson.json_util import dumps


myclient = pymongo.MongoClient("mongodb://mongodb:27017/")
mydb = myclient["shyamDB"]


def write_data_in_db(data, tableName):
    logging.warning(myclient)
    mycol = mydb[tableName]
    data['cipher_text'] = str(data['cipher_text'])
    data['created_at'] = datetime.datetime.now()+datetime.timedelta(2)
    return mycol.insert_one(data)


def query_data_from_db(query, tableName):
    "Find the given cipher text from given table"
    return json.loads(dumps(
        mydb[tableName].find({
        'cipher_text': str(query)}
                          )))
