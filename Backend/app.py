from crypt import methods
import logging
from flask import Flask
from flask import request
from flask_cors import CORS
import random

from utils import shamir
from utils import mail

app = Flask(__name__)
CORS(app)

@app.route('/encrypt/shamir', methods=['POST'])
def shamir_secret_share():
		# (3,5) sharing scheme
		data = request.json
		t, n = 3, 5
		secret = int(data['data_to_encrypt'])
		receiver_email_id = data['email']
		print(f'Original Secret: {secret}')
		# Phase I: Generation of shares
		shares = shamir.generate_shares(n, t, secret)
		print(f'Shares: {", ".join(str(share) for share in shares)}')

		# Phase II: Secret Reconstruction
		# Picking t shares randomly for
		# reconstruction
		pool = random.sample(shares, t)
		mail.send_email(receiver_address=receiver_email_id, message=pool)
		print(f'Combining shares: {", ".join(str(share) for share in pool)}')
		print(f'Reconstructed secret: {shamir.reconstruct_secret(pool)}')
		return {"data": pool}
	
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
	print(f'Reconstructed secret: {shamir.reconstruct_secret(pool)}')
	return {"data": shamir.reconstruct_secret(pool)}

