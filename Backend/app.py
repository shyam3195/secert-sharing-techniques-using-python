# Default Packages
import logging
import random

# Downloaded Packages
from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS # For cross platform access[Cros Origin Resource Sharing]


# Own created Libraries
from utils import shamir
from utils import mail
from utils import aes
from utils import db
from utils import elgamal


app = Flask(__name__) # Creating a flask app
CORS(app)


@app.route('/encrypt/shamir', methods=['POST'])
def shamir_secret_share():
    # (3,5) sharing scheme
    data = request.json # Get the body from request
    t, n = 3, 5
    secret = int(data['data_to_encrypt']) # Convert the plain text to integer
    receiver_email_id = data['email']
   
    logging.warning(f'Original Secret: {secret}')
    # Phase I: Generation of shares [i.e] Encryption
    shares = shamir.encrypt(n, t, secret)
    logging.warning(f'Shares: {", ".join(str(share) for share in shares)}')

    # Phase II: Secret Reconstruction
    # Picking t shares randomly for reconstruction

    # random.sample is an inbuilt function of random module in Python that returns a particular length list of items 
    # chosen from the sequence 
    # i.e. list, tuple, string or set. 
    # Used for random sampling without replacement.
    pool = random.sample(shares, t)
    
    # Calling send_mail function to send the cipher text[pool]  
    mail.send_email(receiver_address=receiver_email_id, message=pool, subject="Shamir Algorithm")
  
    return jsonify({"data": pool})


@app.route('/decrypt/shamir', methods=['POST'])
def shamir_secret_decrypt():
    data = request.json
    poolcpy = data['encrypted_data']

    pool = []
    # Converting string to array for exampl - "[1,2,3,4]" ---> [1,2,3,4]
    
    while poolcpy:
        start_index = poolcpy.find("(")
        end_index = poolcpy.find(")")
        cut_pool = poolcpy[start_index: end_index+1].strip("()").split(',')
        cut_pool = tuple([int(ele) for ele in cut_pool])
        pool.append(cut_pool)
        poolcpy = poolcpy[end_index+2:]
        if poolcpy.find('(') == -1:
            break
    
    return jsonify({"data": shamir.decrypt(pool)})


@app.route('/encrypt/aes', methods=['POST'])
def aes_encryption():
    # Creating a key by choosing a random integer from 10000, 10000000
    # Converting the key integer to string
    my_key = str(random.randint(10000, 10000000))
    # Creating the object for the class AESCipher, where init method will be called
    AESCipher = aes.AESCipher(my_key)
    
    data = request.json # Body from api
    plain_text = data['data_to_encrypt']
    receiver_email_id = data['email']
    
    cipher_text = AESCipher.encrypt(plain_text)
    mail.send_email(
        receiver_address=receiver_email_id,
        message=cipher_text.decode()
        , subject="AES Algorithm")
    db.write_data_in_db(
        {
            "cipher_text": cipher_text.decode("utf-8"),
            "key": my_key,
            "plain_text": plain_text
        }, tableName="AES")
    return jsonify({"data": cipher_text.decode("utf-8")})


@app.route('/decrypt/aes', methods=['POST'])
def aes_decryption():
    
    data = request.json
    cipher_text = data['encrypted_data']
    
    # Get corresponding key for the given encrypted data in mongodb
    key = db.query_data_from_db(cipher_text, tableName="AES")[0]['key']
    AESCipher = aes.AESCipher(key)
    
    # Encode the cipher text from string
    cipher_text = cipher_text.encode()
    # Call decrypt method to get plain text
    plain_text = AESCipher.decrypt(cipher_text)
    
    return jsonify({"data": plain_text})


@app.route('/encrypt/elgamal', methods=['POST'])
def elgamal_encryption():
    
    data = request.json
    plain_text = data['data_to_encrypt']
    receiver_email_id = data['email']

    # Creating q as random integer from 10^20 to 10^50
    # Creating g as random integer from 2 to q
    q = random.randint(pow(10, 20), pow(10, 50))
    g = random.randint(2, q)
 
    key = elgamal.gen_key(q)# Private key for receiver
    h = elgamal.power(g, key, q)
    cipher_text, p = elgamal.encrypt(plain_text, q, h, g)
    # Send the cipher text in email
    mail.send_email(
        receiver_address=receiver_email_id,
        message=cipher_text
    , subject="Elgamal Algorithm")
    # Store all the data in database
    db.write_data_in_db(
        {
            "cipher_text": cipher_text,
            "q": str(q),
            "g": str(g),
            "key": str(key),
            "h": str(h),
            "p": str(p),
            "plain_text": plain_text
        }, tableName="ELGAMAL")
    # return the cipher text
    return jsonify(
        {
            "data": cipher_text
        })


@app.route('/decrypt/elgamal', methods=['POST'])
def elgamal_decryption():
    
    data = request.json
    cipher_text = data['encrypted_data']
    data = db.query_data_from_db(cipher_text, tableName="ELGAMAL")[0]
    
    # Convert p, key, q string into integer
    p = int(data['p'])
    key = int(data['key'])
    q = int(data['q'])
    
    # Convert cipher text string to array of integers
    list_int_cipher = [int(ele) for ele in cipher_text[1: -1].split(', ')]
    # Calling decrypt function to get the plain text
    plain_text = elgamal.decrypt(list_int_cipher, p, key, q)
    # return teh plain text
    return jsonify({"data": ''.join(plain_text)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port='5000', threaded=True, debug=True)