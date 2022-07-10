import datetime
import pymongo
import json
from bson.objectid import ObjectId
import logging
from bson.json_util import dumps


myclient = pymongo.MongoClient("mongodb://mongodb:27017/")
mydb = myclient["shyamDB"]


def write_data_in_db(data, tableName):
    mycol = mydb[tableName]
    if not data['is_login_register']:
        data['cipher_text'] = str(data['cipher_text'])
    else:
        data.pop('is_login_register')
    data['created_at'] = datetime.datetime.now()+datetime.timedelta(2)
    return mycol.insert_one(data)


def query_data_from_db(query, tableName):
    "Find the given cipher text from given table"
    return json.loads(dumps(
        mydb[tableName].find({
        'cipher_text': str(query)}
                          )))

def get_user_from_db(user_id, email):
    # If the user_id is given then query using user_id
    if user_id:
        return json.loads(dumps(
            mydb['USER'].find({'_id': ObjectId(user_id)})))
    # If the email is given then query using email
    elif email:
        return json.loads(dumps(
            mydb['USER'].find({'email': email})))
    # If both email and user_id is not given then query all users
    else:
        return json.loads(dumps(mydb['USER'].find({})))
    
    
def request_to_connect(connecting_user_id, user_id, user1_pub_key, user2_pub_key, P, G):
    mydb['CONNECT'].insert_one(
        {
            "user_id": user_id,
            "connecting_user_id": connecting_user_id,
            "user1_public_key": user1_pub_key,
            "user2_pub_key": user2_pub_key,
            "P": P,
            "G": G,
            'created_at': datetime.datetime.now()+datetime.timedelta(2),
            'deleted_at': None,
            "is_requested": True,
            "is_connected": False
        }
    )
    return


def get_connections_by_user_id(user_id):
    return json.loads(dumps(
            mydb['CONNECT'].find(
                { '$or': [ { 'user_id': user_id }, { 'connecting_user_id': user_id } ] } 
                )))

def accept_connection(data):
    # Filter connecting_user and user_id from CONNECT TABLE
    filter = {'connecting_user_id': str(data.get('user_id')), 'user_id': str(data.get('userid_to_accept'))}
    # Set is_requested as False and is_connected as True in CONNECT TABLE
    newvalues = { "$set": { 'is_requested': False, 'is_connected': True }}
    mydb['CONNECT'].update_many(filter, newvalues)
    return
    