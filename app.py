from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from blockchain.blockchain import Blockchain
from blockchain.wallet import Wallet
from blockchain.transaction import Transaction

# ✅ CREATE APP
app = Flask(__name__)
CORS(app)

blockchain = Blockchain()

# 🗄️ IN-MEMORY DATABASE FOR DEMO PURPOSES
# Maps username -> wallet data
users_db = {} 

@app.route('/')
def home():
    return "🚀 Advanced Cryptographic Blockchain API Running"

# ✅ CREATE WALLET (NOW REQUIRES USERNAME)
@app.route('/create_wallet', methods=['POST'])
def create_wallet():
    data = request.get_json()
    username = data.get("username")

    if not username:
        return jsonify({"error": "Username is required."}), 400
    if username in users_db:
        return jsonify({"error": f"User '{username}' already exists!"}), 400

    # Generate real ECDSA keys
    wallet = Wallet()
    
    wallet_data = {
        "username": username,
        "public_key": wallet.public_key,
        "private_key": wallet.private_key
    }
    
    # Store in our mock database
    users_db[username] = wallet_data

    return jsonify(wallet_data)

# ✅ GET ALL WALLETS (FOR THE DROPDOWN MENUS)
@app.route('/wallets', methods=['GET'])
def get_wallets():
    # Returns a list of all created wallets
    return jsonify(list(users_db.values()))

# ✅ ADD TRANSACTION
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))