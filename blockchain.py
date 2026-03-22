import hashlib
import datetime

class Block:
    def __init__(self, index, transactions, prev_hash):
        self.index = index
        self.timestamp = str(datetime.datetime.now())
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.nonce = 0
        self.hash = self.mine_block()

    def calculate_hash(self):
        data = str(self.index) + self.timestamp + str(self.transactions) + self.prev_hash + str(self.nonce)
        return hashlib.sha256(data.encode()).hexdigest()

    def mine_block(self, difficulty=3):
        prefix = "0" * difficulty
        while True:
            hash_value = self.calculate_hash()
            if hash_value.startswith(prefix):
                return hash_value
            self.nonce += 1


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, ["Genesis Block"], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, transactions):
        prev = self.get_latest_block()
        new_block = Block(len(self.chain), transactions, prev.hash)
        self.chain.append(new_block)

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False

            if current.prev_hash != previous.hash:
                return False

        return True