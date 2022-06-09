from crypt import methods
from flask import Flask
from flask import request
from utils import shamir
import random


app = Flask(__name__)


@app.route('/encrypt/shamir')
def shamir_secret_share():
		# (3,5) sharing scheme
		data = request.json
		t, n = 3, 5
		secret = data['data_to_encrypt']
		print(f'Original Secret: {secret}')
		# Phase I: Generation of shares
		shares = shamir.generate_shares(n, t, secret)
		print(f'Shares: {", ".join(str(share) for share in shares)}')

		# Phase II: Secret Reconstruction
		# Picking t shares randomly for
		# reconstruction
		pool = random.sample(shares, t)
		print(f'Combining shares: {", ".join(str(share) for share in pool)}')
		print(f'Reconstructed secret: {shamir.reconstruct_secret(pool)}')
		return {"data": pool}
	
@app.route('/decrypt/shamir', methods=['POST'])
def shamir_secret_decrypt():
	data = request.json
	pool = data['encrypted_data']
	print(f'Reconstructed secret: {shamir.reconstruct_secret(pool)}')
	return {"data": shamir.reconstruct_secret(pool)}

