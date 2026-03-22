from flask import Flask, request, jsonify
from flask_cors import CORS
from blockchain.blockchain import Blockchain
from blockchain.wallet import Wallet

app = Flask(__name__)
CORS(app)

blockchain = Blockchain()

@app.route('/create_wallet', methods=['GET'])
def create_wallet():
    wallet = Wallet()
    return jsonify({
        "private_key": wallet.private_key,
        "public_key": wallet.public_key
    })

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.json
    blockchain.add_transaction(data)
    return jsonify({"message": "Transaction added"})

@app.route('/mine', methods=['GET'])
def mine():
    block = blockchain.mine_block()
    return jsonify(block)

@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify(blockchain.chain)

if __name__ == '__main__':
    app.run(debug=True)