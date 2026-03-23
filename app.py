from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from blockchain.blockchain import Blockchain
from blockchain.wallet import Wallet
from blockchain.transaction import Transaction

app = Flask(__name__)
CORS(app)

blockchain = Blockchain()
users_db = {} 

@app.route('/')
def home():
    return "🚀 Advanced Cryptographic Blockchain API Running"

@app.route('/create_wallet', methods=['POST'])
def create_wallet():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password") # ✅ NEW: Require password

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400
    if username in users_db:
        return jsonify({"error": f"User '{username}' already exists!"}), 400

    wallet = Wallet()
    
    # Issue 10,000 coins to new user
    tx = Transaction(sender="SYSTEM", receiver=wallet.public_key, amount=10000)
    blockchain.add_transaction(tx.to_dict())
    blockchain.mine_block() 
    
    wallet_data = {
        "username": username,
        "password": password, # ✅ NEW: Store password
        "public_key": wallet.public_key,
        "private_key": wallet.private_key
    }
    
    users_db[username] = wallet_data
    
    response_data = {
        "username": username,
        "public_key": wallet.public_key,
        "private_key": wallet.private_key,
        "balance": blockchain.get_balance(wallet.public_key)
    }
    return jsonify(response_data)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password") # ✅ NEW: Require password
    
    if not username or username not in users_db:
        return jsonify({"error": "User not found. Please register first."}), 404
        
    # ✅ NEW: Verify password before returning the private key
    if users_db[username]["password"] != password:
        return jsonify({"error": "Incorrect password. Access denied."}), 401
        
    user_data = users_db[username]
    balance = blockchain.get_balance(user_data['public_key'])
    
    return jsonify({
        "username": username,
        "public_key": user_data['public_key'],
        "private_key": user_data['private_key'],
        "balance": balance
    })

@app.route('/wallets', methods=['GET'])
def get_wallets():
    wallets_list = []
    for username, data in users_db.items():
        balance = blockchain.get_balance(data['public_key'])
        wallets_list.append({
            "username": username,
            "public_key": data['public_key'],
            "balance": balance
            # Private key and Password are NOT sent here!
        })
    return jsonify(wallets_list)

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.get_json()
    sender = data.get("sender")
    receiver = data.get("receiver")
    amount = data.get("amount")
    private_key = data.get("private_key") 

    if not sender or not receiver or not amount or not private_key:
        return jsonify({"error": "Missing fields."}), 400

    sender_balance = blockchain.get_balance(sender)
    if sender_balance < amount:
        return jsonify({"error": f"Insufficient balance! Sender only has {sender_balance} coins."}), 400

    try:
        transaction = Transaction(sender, receiver, amount)
        transaction.sign_transaction(private_key)

        if not transaction.is_valid():
            return jsonify({"error": "Cryptographic Verification Failed! Invalid Signature."}), 403
            
        blockchain.add_transaction(transaction.to_dict())
        return jsonify({"message": "Transaction cryptographically verified and added to mempool!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mine', methods=['GET'])
def mine():
    return jsonify(blockchain.mine_block())

@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify({"chain": blockchain.chain, "length": len(blockchain.chain)})

@app.route('/validate', methods=['GET'])
def validate_chain():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        return jsonify({"message": "The Blockchain is valid and cryptographically secure.", "valid": True})
    else:
        return jsonify({"message": "Warning! Blockchain integrity compromised.", "valid": False})

@app.route('/balance/<address>', methods=['GET'])
def get_balance(address):
    balance = blockchain.get_balance(address)
    return jsonify({"address": address, "balance": balance})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))