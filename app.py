from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from blockchain.blockchain import Blockchain
from blockchain.transaction import Transaction
from blockchain.wallet import Wallet

app = Flask(__name__)
CORS(app)

blockchain = Blockchain()


# ✅ ROOT ROUTE (IMPORTANT FOR RENDER)
@app.route('/')
def home():
    return "🚀 Blockchain API is running!"


# ✅ CREATE WALLET
@app.route('/create_wallet', methods=['GET'])
def create_wallet():
    wallet = Wallet()
    return jsonify({
        "private_key": wallet.private_key,
        "public_key": wallet.public_key
    })


# ✅ ADD TRANSACTION WITH SIGNATURE VALIDATION
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.get_json()

    required_fields = ["sender", "receiver", "amount"]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field {field}"}), 400

    transaction = Transaction(
        data["sender"],
        data["receiver"],
        data["amount"],
        data.get("signature")
    )

    if not transaction.is_valid():
        return jsonify({"error": "Invalid transaction"}), 400

    blockchain.add_transaction(transaction.to_dict())

    return jsonify({"message": "Transaction added successfully"})


# ✅ MINE BLOCK
@app.route('/mine', methods=['GET'])
def mine():
    block = blockchain.mine_block()
    return jsonify(block)


# ✅ GET BLOCKCHAIN
@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify({
        "length": len(blockchain.chain),
        "chain": blockchain.chain
    })


# ✅ RUN FOR LOCAL + RENDER
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))