from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from blockchain.blockchain import Blockchain
from blockchain.wallet import Wallet
from blockchain.transaction import Transaction

# ✅ CREATE APP FIRST
app = Flask(__name__)
CORS(app)

blockchain = Blockchain()

# ✅ ROOT ROUTE
@app.route('/')
def home():
    return "🚀 Advanced Cryptographic Blockchain API Running"

# ✅ CREATE WALLET (ECDSA CRYPTOGRAPHY)
@app.route('/create_wallet', methods=['GET'])
def create_wallet():
    wallet = Wallet()
    return jsonify({
        "public_key": wallet.public_key,
        "private_key": wallet.private_key
    })

# ✅ ADD TRANSACTION (DIGITAL SIGNATURES)
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.get_json()

    sender = data.get("sender")
    receiver = data.get("receiver")
    amount = data.get("amount")
    private_key = data.get("private_key") 

    if not sender or not receiver or not amount or not private_key:
        return jsonify({"error": "Missing fields. Public keys, amount, and private key required."}), 400

    try:
        transaction = Transaction(sender, receiver, amount)
        transaction.sign_transaction(private_key)

        if not transaction.is_valid():
            return jsonify({"error": "Cryptographic Verification Failed! Invalid Signature."}), 403
            
        blockchain.add_transaction(transaction.to_dict())

        return jsonify({
            "message": "Transaction cryptographically verified and added to mempool!"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ MINE BLOCK
@app.route('/mine', methods=['GET'])
def mine():
    block = blockchain.mine_block()
    return jsonify(block)

# ✅ GET CHAIN
@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify({
        "chain": blockchain.chain,
        "length": len(blockchain.chain)
    })

# ✅ RUN
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))