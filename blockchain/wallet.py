import ecdsa

class Wallet:
    def __init__(self):
        self.private_key = ecdsa.SigningKey.generate().to_string().hex()
        self.public_key = ecdsa.VerifyingKey.from_string(
            bytes.fromhex(self.private_key),
            curve=ecdsa.SECP256k1
        ).to_string().hex()