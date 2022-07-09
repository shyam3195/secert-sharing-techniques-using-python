from flask import jsonify

def getUserFromDB(user_in_db, db):
    if len(user_in_db) > 0:
        user_in_db = user_in_db[0]
        user_in_db['user_id'] = user_in_db['_id']['$oid']
        user_in_db.pop('_id')
        user_in_db.pop('private_key')
        user_in_db.pop('password')
        connections = db.get_connections_by_user_id(user_id=user_in_db['user_id'])
        return jsonify({'data': user_in_db, 'connections': connections})
    else:
        return jsonify({'data': 'error'})