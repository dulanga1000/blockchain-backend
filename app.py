from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from blockchain.blockchain import Blockchain

# ✅ CREATE APP FIRST
app = Flask(__name__)
CORS(app)

blockchain = Blockchain()


# ✅ ROOT ROUTE
@app.route('/')
def home():
    return "🚀 Blockchain API Running"


# ✅ CREATE WALLET (optional)
@app.route('/create_wallet', methods=['GET'])
def create_wallet():
    return jsonify({"message": "Wallet endpoint working"})


# ✅ ADD TRANSACTION (MANUAL INPUT)
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.get_json()

    sender = data.get("sender")
    receiver = data.get("receiver")
    amount = data.get("amount")

    if not sender or not receiver or not amount:
        return jsonify({"error": "Missing fields"}), 400

    transaction = {
        "sender": sender,
        "receiver": receiver,
        "amount": amount
    }

    blockchain.add_transaction(transaction)

    return jsonify({
        "message": "Transaction added to mempool"
    })


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