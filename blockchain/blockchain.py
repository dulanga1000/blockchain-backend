import hashlib
import json
from time import time

class Blockchain:
    def __init__(self, db_collection):
        self.transactions = []
        self.collection = db_collection
        db_chain = list(self.collection.find({}, {"_id": 0}).sort("index", 1))
        
        if len(db_chain) > 0 and db_chain[0].get("index") == 1:
            self.chain = db_chain
        else:
            self.collection.delete_many({})
            self.chain = []
            self.create_genesis_block()

    def create_genesis_block(self):
        self.transactions.append({
            "sender": "SYSTEM",
            "receiver": "NETWORK_GENESIS",
            "amount": 0
        })
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.transactions,
            "proof": proof,
            "previous_hash": previous_hash
        }
        block["hash"] = self.hash(block)
        self.transactions = []
        self.chain.append(block)
        
        self.collection.insert_one(block.copy())
        
        return block

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def hash(self, block):
        block_copy = dict(block)
        block_copy.pop("hash", None)
        block_copy.pop("_id", None)
        encoded = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()

    def mine_block(self):
        previous_block = self.chain[-1]
        previous_hash = previous_block["hash"]
        proof = 1
        while True:
            hash_operation = hashlib.sha256(str(proof**2 - previous_block['proof']**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                break
            proof += 1
        return self.create_block(proof, previous_hash)

    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for tx in block['transactions']:
                if tx['sender'] == address:
                    balance -= tx['amount']
                if tx['receiver'] == address:
                    balance += tx['amount']
        for tx in self.transactions:
            if tx['sender'] == address:
                balance -= tx['amount']
            if tx['receiver'] == address:
                balance += tx['amount']
        return balance

    def get_transaction_history(self, address):
        history = []
        for block in self.chain:
            for tx in block['transactions']:
                if tx['sender'] == address or tx['receiver'] == address:
                    tx_copy = dict(tx)
                    tx_copy['status'] = 'Confirmed'
                    tx_copy['block_index'] = block['index']
                    history.append(tx_copy)
                    
        for tx in self.transactions:
            if tx['sender'] == address or tx['receiver'] == address:
                tx_copy = dict(tx)
                tx_copy['status'] = 'Pending'
                history.append(tx_copy)
                
        return history[::-1]

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != previous_block['hash']:
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True