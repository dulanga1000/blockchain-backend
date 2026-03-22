import time


class Block:
    def __init__(self, index, transactions, proof, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.proof = proof
        self.previous_hash = previous_hash

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "proof": self.proof,
            "previous_hash": self.previous_hash
        }