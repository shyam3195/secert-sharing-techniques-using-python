from random import randint
import random
import logging

class Diffi():
    def __init__(self) -> None:
        pass
    
    def primesInRange(self, x, y):
        prime_list = []
        for n in range(x, y):
            isPrime = True

            for num in range(2, n):
                if n % num == 0:
                    isPrime = False

            if isPrime:
                prime_list.append(n)
                
        return prime_list

    def getPublicKeys(self):
        P = random.choice(self.primesInRange(10000, 10600))
        G = random.randint(1, 10000)
        return P, G

    def createPublicKey(self, user1_private_key, user2_private_key):
        P, G = self.getPublicKeys()
        user1_private_key = int(user1_private_key)
        user2_private_key = int(user2_private_key)
        user1_public_key = int(pow(G,user1_private_key,P)) 
        user2_public_key = int(pow(G,user2_private_key,P)) 
        return user1_public_key, user2_public_key, P, G
    
    def getSecretKey(self, private_key, public_key, P):
        secert_key = int(pow(public_key,private_key,P))
        return secert_key
    
    def checkSecretKey(self, user1_private_key, user2_private_key, user1_public_key, user2_public_key, P):
        ka = int(pow(user2_public_key,user1_private_key,P))
        kb = int(pow(user1_public_key,user2_private_key,P))
        if ka == kb:
            return ka
        else:
            return "error in secret key generation"