import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
import logging

class AESCipher(object):

    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw) # Padding so that all the data will be 16bits
        iv = Random.new().read(AES.block_size) # Generating an initialization vector. 
        cipher = AES.new(self.key, AES.MODE_CBC, iv) # Create an AES Cipher. 
        return base64.b64encode(iv + cipher.encrypt(raw.encode())) # Encrypting the msg with AES cipher

    def decrypt(self, enc):
        enc = base64.b64decode(enc) # Decode from b64
        iv = enc[:AES.block_size] # remove iv
        cipher = AES.new(self.key, AES.MODE_CBC, iv) # Create an AES Cipher. 
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8') # Decrypt the message

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]
