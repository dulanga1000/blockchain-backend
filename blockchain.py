import hashlib, datetime
from ecdsa import SigningKey, SECP256k1

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount
        }

class Block:
    def __init__(self, index, transactions, prev_hash):
        self.index = index
        self.timestamp = str(datetime.datetime.now())
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.nonce = 0
        self.hash = self.mine()

    def calc_hash(self):
        data = str(self.index)+self.timestamp+str(self.transactions)+self.prev_hash+str(self.nonce)
        return hashlib.sha256(data.encode()).hexdigest()

    def mine(self):
        while True:
            h = self.calc_hash()
            if h.startswith("000"):
                return h
            self.nonce += 1

class Blockchain:
    def __init__(self):
        self.chain = [Block(0, [], "0")]
        self.pending = []
        self.wallets = {}

    def create_wallet(self):
        sk = SigningKey.generate(curve=SECP256k1)
        addr = sk.verifying_key.to_string().hex()
        self.wallets[addr] = 100
        return {"public": addr}

    def add_tx(self, sender, receiver, amount):
        if sender != "SYSTEM" and self.wallets.get(sender,0) < amount:
            return False
        self.pending.append(Transaction(sender,receiver,amount).to_dict())
        return True

    def mine(self, miner):
        self.pending.append(Transaction("SYSTEM",miner,10).to_dict())
        block = Block(len(self.chain), self.pending, self.chain[-1].hash)
        self.chain.append(block)

        for t in self.pending:
            if t["sender"] != "SYSTEM":
                self.wallets[t["sender"]] -= t["amount"]
            self.wallets[t["receiver"]] = self.wallets.get(t["receiver"],0)+t["amount"]

        self.pending=[]
        return block

    def get_chain(self):
        return [{
            "index": b.index,
            "hash": b.hash,
            "prev_hash": b.prev_hash,
            "tx": b.transactions
        } for b in self.chain]