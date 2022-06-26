# from crypt import methods
from fileinput import filename
import logging
from flask import Flask
from flask import request
from flask_cors import CORS
import random
from flask import jsonify
import random


from utils import shamir
from utils import mail
from utils import aes
from utils import db
from utils import elgamal

app = Flask(__name__)
CORS(app)


@app.route('/encrypt/shamir', methods=['POST'])
def shamir_secret_share():
    # (3,5) sharing scheme
    data = request.json
    t, n = 3, 5
    secret = int(data['data_to_encrypt'])
    receiver_email_id = data['email']
    logging.warning(f'Original Secret: {secret}')
    # Phase I: Generation of shares
    shares = shamir.encrypt(n, t, secret)
    logging.warning(f'Shares: {", ".join(str(share) for share in shares)}')

    # Phase II: Secret Reconstruction
    # Picking t shares randomly for
    # reconstruction
    pool = random.sample(shares, t)
    mail.send_email(receiver_address=receiver_email_id, message=pool, subject="Shamir Algorithm")
    logging.warning(f'Combining shares: {", ".join(str(share) for share in pool)}')
    logging.warning(f'Reconstructed secret: {shamir.decrypt(pool)}')
    return jsonify({"data": pool})


@app.route('/decrypt/shamir', methods=['POST'])
def shamir_secret_decrypt():
    data = request.json
    logging.warn(data)
    poolcpy = data['encrypted_data']
    logging.warn(poolcpy)
    logging.warn(type(poolcpy))
    # poolcpy =  pool

    pool = []
    while poolcpy:
        start_index = poolcpy.find("(")
        end_index = poolcpy.find(")")
        cut_pool = poolcpy[start_index: end_index+1].strip("()").split(',')
        cut_pool = tuple([int(ele) for ele in cut_pool])
        pool.append(cut_pool)
        poolcpy = poolcpy[end_index+2:]
        if poolcpy.find('(') == -1:
            break
    logging.warning(f'Reconstructed secret: {shamir.decrypt(pool)}')
    return jsonify({"data": shamir.decrypt(pool)})


@app.route('/encrypt/aes', methods=['POST'])
def aes_encryption():
    my_key = str(random.randint(10000, 10000000))
    AESCipher = aes.AESCipher(my_key)
    
    data = request.json
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
        }, dbName="AES")
    return jsonify({"data": cipher_text.decode("utf-8")})


@app.route('/decrypt/aes', methods=['POST'])
def aes_decryption():
    
    data = request.json
    cipher_text = data['encrypted_data']
    
    # Get corresponding key for the given encrypted data in mongodb
    key = db.query_data_from_db(cipher_text, dbName="AES")[0]['key']
    AESCipher = aes.AESCipher(key)
    
    cipher_text = cipher_text.encode()
    plain_text = AESCipher.decrypt(cipher_text)
    
    return jsonify({"data": plain_text})


@app.route('/encrypt/elgamal', methods=['POST'])
def elgamal_encryption():
    
    data = request.json
    plain_text = data['data_to_encrypt']
    receiver_email_id = data['email']
    
    q = random.randint(pow(10, 20), pow(10, 50))
    g = random.randint(2, q)
 
    key = elgamal.gen_key(q)# Private key for receiver
    h = elgamal.power(g, key, q)
    cipher_text, p = elgamal.encrypt(plain_text, q, h, g)
    mail.send_email(
        receiver_address=receiver_email_id,
        message=cipher_text
    , subject="Elgamal Algorithm")
    db.write_data_in_db(
        {
            "cipher_text": cipher_text,
            "q": str(q),
            "g": str(g),
            "key": str(key),
            "h": str(h),
            "p": str(p),
            "plain_text": plain_text
        }, dbName="ELGAMAL")
    return jsonify(
        {
            "data": cipher_text
        })


@app.route('/decrypt/elgamal', methods=['POST'])
def elgamal_decryption():
    
    data = request.json
    cipher_text = data['encrypted_data']
    data = db.query_data_from_db(cipher_text, dbName="ELGAMAL")[0]
    
    p = int(data['p'])
    key = int(data['key'])
    q = int(data['q'])
    
    list_int_cipher = [int(ele) for ele in cipher_text[1: -1].split(', ')]
    plain_text = elgamal.decrypt(list_int_cipher, p, key, q)
    
    return jsonify({"data": ''.join(plain_text)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port='5000', threaded=True, debug=True)