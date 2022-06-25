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
    shares = shamir.generate_shares(n, t, secret)
    logging.warning(f'Shares: {", ".join(str(share) for share in shares)}')

    # Phase II: Secret Reconstruction
    # Picking t shares randomly for
    # reconstruction
    pool = random.sample(shares, t)
    mail.send_email(receiver_address=receiver_email_id, message=pool)
    logging.warning(f'Combining shares: {", ".join(str(share) for share in pool)}')
    logging.warning(f'Reconstructed secret: {shamir.reconstruct_secret(pool)}')
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
    logging.warning(f'Reconstructed secret: {shamir.reconstruct_secret(pool)}')
    return jsonify({"data": shamir.reconstruct_secret(pool)})


@app.route('/encrypt/aes', methods=['POST'])
def aes_encryption():
    my_key = str(random.randint(10000, 10000000))
    AESCipher = aes.AESCipher(my_key)
    
    is_text = request.args.get('is_pdf')
    
    # File Encryption
    if is_text:
        file = request.files['file']
        file.save(file.filename)
        plain_text = open(filename, "r").read()
        receiver_email_id = request.headers['user_email']
    # Text Feild Encryption
    else:
        data = request.json
        plain_text = data['data_to_encrypt']
        receiver_email_id = data['email']
    
    cipher_text = AESCipher.encrypt(plain_text)
    mail.send_email(receiver_address=receiver_email_id, message=cipher_text)
    db.write_data_in_db(
        {
            "cipher_text": cipher_text.decode("utf-8"),
            "key": my_key,
            "plain_text": plain_text
        })
    return jsonify({"data": cipher_text.decode("utf-8")})


@app.route('/decrypt/aes', methods=['POST'])
def aes_decryption():
    
    data = request.json
    cipher_text = data['encrypted_data']
    
    # Get corresponding key for the given encrypted data in mongodb
    key = db.query_data_from_db(cipher_text)[0]['key']
    AESCipher = aes.AESCipher(key)
    
    cipher_text = cipher_text.encode()
    plain_text = AESCipher.decrypt(cipher_text)
    
    logging.warning("plain_text")
    logging.warning(plain_text)
    return jsonify({"data": plain_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port='5000', threaded=True, debug=True)