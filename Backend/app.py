# Default Packages
from crypt import methods
import logging
import random

# Downloaded Packages
from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS # For cross platform access[Cros Origin Resource Sharing]


# Own created Libraries
from utils import mail
from utils import aes
from utils import db
from utils import helpers
from utils import diffi

app = Flask(__name__) # Creating a flask app
CORS(app)


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user_in_db = db.get_user_from_db(user_id = None, email = data['email'])
    if(data['password'] != user_in_db[0]['password']):
        return jsonify({'data': 'incorrect password'})
    return helpers.getUserFromDB(user_in_db=user_in_db, db=db)


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    data['private_key'] = str(random.randint(10000, 10000000))
    data['is_login_register'] = True
    data['is_logged_in'] = False
    db.write_data_in_db(data, tableName="USER")
    return jsonify({'data': 'success'})

@app.route('/user', methods=['POST'])
def user():
    data = request.json
    user_in_db = db.get_user_from_db(user_id = None, email = data['email'])
    return helpers.getUserFromDB(user_in_db=user_in_db, db=db)


@app.route('/users', methods=['GET'])
def users():
    users = db.get_user_from_db(user_id = None, email = None)
    return jsonify({'data': users})


@app.route('/request/connect', methods=['POST'])
def requestConnect():
    data = request.json
    current_user_id = data['current_user_id']
    requesting_user_id = data['requesting_user_id']
    
    user1_private_key = db.get_user_from_db(user_id=current_user_id, email=None)[0]['private_key']
    user2_private_key = db.get_user_from_db(user_id=requesting_user_id, email=None)[0]['private_key']
    # Call Diffi Helmen key exchage to generate public key for both users converation
    DIFFI = diffi.Diffi()
    user1_pub_key, user2_pub_key, P, G = DIFFI.createPublicKey(user1_private_key, user2_private_key)
    db.request_to_connect(requesting_user_id, current_user_id, user1_pub_key, user2_pub_key, P, G)
    return jsonify({'data': 'success'})

@app.route('/accept/connect', methods=['POST'])
def acceptConnect():
    data=request.json
    db.accept_connection(data)
    user_in_db = db.get_user_from_db(user_id = data['user_id'], email = None)
    connections = db.get_connections_by_user_id(user_id=data['user_id'])
    return {'users': user_in_db, 'connections': connections}


@app.route('/encrypt/aes', methods=['POST'])
def aes_encryption():
    
    data = request.json # Body from api
    receiver_public_key = int(data['receiver_pub_key'])
    sender_public_key = int(data['sender_public_key'])
    plain_text = data['data_to_encrypt']
    receiver_email_id = data['email']
    
    user_details = db.get_user_from_db(user_id = data['sender_id'], email = None)
    connection_details = db.get_connections_by_user_id(user_id=data['sender_id'])
    
    sender_private_key = int(user_details[0]['private_key'])
    P = int(connection_details[0]['P'])
    
    DIFFI = diffi.Diffi()
    secret_key = DIFFI.getSecretKey(sender_private_key, receiver_public_key, P)
    
    # Creating the object for the class AESCipher, where init method will be called
    AESCipher = aes.AESCipher(str(secret_key))
    
    
    cipher_text = AESCipher.encrypt(plain_text)
    mail.send_email(
        receiver_address=receiver_email_id,
        message=cipher_text.decode(),
        public_key=str(sender_public_key),
        subject="AES Algorithm")
    db.write_data_in_db(
        {
            "cipher_text": cipher_text.decode("utf-8"),
            "key": secret_key,
            "plain_text": plain_text,
            "is_login_register": None
        }, tableName="AES")
    return jsonify({"data": cipher_text.decode("utf-8")})


@app.route('/decrypt/aes', methods=['POST'])
def aes_decryption():
    
    data = request.json
    cipher_text = data['encrypted_data']
    sender_public_key = int(data['sender_public_key'])
    user_details = db.get_user_from_db(user_id = data['user_id'], email = None)
    connection_details = db.get_connections_by_user_id(user_id=data['user_id'])
    receiver_private_key = int(user_details[0]['private_key'])
    P = int(connection_details[0]['P'])
    
    DIFFI = diffi.Diffi()
    secret_key = DIFFI.getSecretKey(receiver_private_key, sender_public_key, P)
    
    AESCipher = aes.AESCipher(str(secret_key))
    
    # Encode the cipher text from string
    cipher_text = cipher_text.encode()
    # Call decrypt method to get plain text
    plain_text = AESCipher.decrypt(cipher_text)
    
    return jsonify({"data": plain_text})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port='5000', threaded=True, debug=True)