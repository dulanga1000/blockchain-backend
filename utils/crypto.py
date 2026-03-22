import hashlib
import json
import ecdsa


def sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()


def hash_block(block):
    encoded = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def sign_data(private_key_hex, data):
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key_hex), curve=ecdsa.SECP256k1)
    return sk.sign(data.encode()).hex()


def verify_signature(public_key_hex, data, signature_hex):
    try:
        vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=ecdsa.SECP256k1)
        return vk.verify(bytes.fromhex(signature_hex), data.encode())
    except:
        return False