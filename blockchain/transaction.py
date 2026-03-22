from utils.crypto import sign_data, verify_signature
import json


class Transaction:
    def __init__(self, sender, receiver, amount, signature=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.signature = signature

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount
        }

    def sign_transaction(self, private_key):
        data = json.dumps(self.to_dict(), sort_keys=True)
        self.signature = sign_data(private_key, data)

    def is_valid(self):
        if self.sender == "SYSTEM":
            return True

        if not self.signature:
            return False

        data = json.dumps(self.to_dict(), sort_keys=True)

        return verify_signature(self.sender, data, self.signature)