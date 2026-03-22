import ecdsa


class Wallet:
    def __init__(self):
        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()

        self.private_key = sk.to_string().hex()
        self.public_key = vk.to_string().hex()