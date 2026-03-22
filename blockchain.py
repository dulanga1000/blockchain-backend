"""
blockchain.py — Core cryptographic blockchain engine
"""

import hashlib
import json
import time
import hmac
import secrets
from datetime import datetime, timezone


def sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


class Wallet:
    def __init__(self, name: str):
        self.name        = name
        self.private_key = secrets.token_hex(32)
        self.public_key  = sha256(self.private_key + "pubkey")
        self.address     = sha256(self.public_key)[:40]

    def sign(self, message: str) -> str:
        return hmac.new(
            self.private_key.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()

    def verify(self, message: str, signature: str) -> bool:
        expected = hmac.new(
            self.private_key.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(signature, expected)


class Transaction:
    def __init__(self, sender_wallet: Wallet, recipient_address: str, amount: float):
        self.sender    = sender_wallet.address
        self.recipient = recipient_address
        self.amount    = amount
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.signature = None
        self.tx_id     = None
        self._wallet   = sender_wallet

    def _message(self) -> str:
        return json.dumps(
            {"sender": self.sender, "recipient": self.recipient,
             "amount": self.amount, "timestamp": self.timestamp},
            sort_keys=True,
        )

    def sign(self):
        self.signature = self._wallet.sign(self._message())
        self.tx_id     = sha256(self._message() + self.signature)[:16]

    def is_valid(self) -> bool:
        if self.signature is None:
            return False
        return self._wallet.verify(self._message(), self.signature)


class MerkleTree:
    def __init__(self, transactions: list):
        self.root = self._build(transactions)

    def _build(self, transactions: list) -> str:
        if not transactions:
            return sha256("empty")
        layer = [sha256(tx._message()) for tx in transactions]
        while len(layer) > 1:
            if len(layer) % 2 == 1:
                layer.append(layer[-1])
            layer = [sha256(layer[i] + layer[i + 1])
                     for i in range(0, len(layer), 2)]
        return layer[0]


class Block:
    def __init__(self, index: int, transactions: list,
                 previous_hash: str, difficulty: int = 3):
        self.index         = index
        self.previous_hash = previous_hash
        self.timestamp     = time.time()
        self.transactions  = transactions
        self.merkle_root   = (MerkleTree(transactions).root
                              if transactions else sha256("genesis"))
        self.difficulty    = difficulty
        self.nonce         = 0
        self.hash          = self._compute_hash()

    def _header(self) -> str:
        return json.dumps({
            "index":         self.index,
            "previous_hash": self.previous_hash,
            "timestamp":     self.timestamp,
            "merkle_root":   self.merkle_root,
            "nonce":         self.nonce,
        }, sort_keys=True)

    def _compute_hash(self) -> str:
        return sha256(self._header())

    def mine(self):
        target   = "0" * self.difficulty
        attempts = 0
        start    = time.time()
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash   = self._compute_hash()
            attempts   += 1
        return attempts, time.time() - start

    def is_valid_pow(self) -> bool:
        return (self.hash.startswith("0" * self.difficulty) and
                self.hash == self._compute_hash())


class Blockchain:
    DIFFICULTY = 3

    def __init__(self):
        self.chain = []
        genesis = Block(0, [], "0" * 64, self.DIFFICULTY)
        genesis.mine()
        self.chain.append(genesis)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, transactions: list):
        for tx in transactions:
            if not tx.is_valid():
                raise ValueError(f"Invalid transaction: {tx.tx_id}")
        block = Block(len(self.chain), transactions,
                      self.last_block.hash, self.DIFFICULTY)
        attempts, elapsed = block.mine()
        self.chain.append(block)
        return block, attempts, elapsed

    def is_valid(self) -> tuple:
        for i in range(1, len(self.chain)):
            cur  = self.chain[i]
            prev = self.chain[i - 1]
            if not cur.is_valid_pow():
                return False, f"Block #{i}: invalid proof of work"
            if cur.previous_hash != prev.hash:
                return False, f"Block #{i}: broken chain link"
            for tx in cur.transactions:
                if not tx.is_valid():
                    return False, f"Block #{i}: invalid transaction {tx.tx_id}"
        return True, "Chain integrity verified"
