import hashlib
import json
from time import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.transactions,
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.transactions = []
        self.chain.append(block)
        return block

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def hash(self, block):
        encoded = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()

    def mine_block(self):
        previous_block = self.chain[-1]
        previous_hash = self.hash(previous_block)
        proof = 1

        while True:
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_block['proof']**2).encode()
            ).hexdigest()

            if hash_operation[:4] == '0000':
                break
            proof += 1

        return self.create_block(proof, previous_hash)