from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from pymongo import MongoClient

from werkzeug.security import generate_password_hash, check_password_hash

from blockchain.blockchain import Blockchain
from blockchain.wallet import Wallet
from blockchain.transaction import Transaction

app = Flask(__name__)
CORS(app)


MONGO_URI = os.environ.get("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["blockchain_db"] 

users_collection = db["users"]
chain_collection = db["chain"]

blockchain = Blockchain(chain_collection)


@app.route('/')
def home():
    return "🚀 Advanced Cloud-Connected Blockchain API Running"

@app.route('/create_wallet', methods=['POST'])
def create_wallet():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password") 

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400
        
    if users_collection.find_one({"username": username}):
        return jsonify({"error": f"User '{username}' already exists!"}), 400

    wallet = Wallet()
    
    tx = Transaction(sender="SYSTEM", receiver=wallet.public_key, amount=10000)
    blockchain.add_transaction(tx.to_dict())
    blockchain.mine_block() 
    

    hashed_password = generate_password_hash(password)
    
    wallet_data = {
        "username": username,
        "password": hashed_password,
        "public_key": wallet.public_key,
        "private_key": wallet.private_key
    }
    
    users_collection.insert_one(wallet_data.copy())
    
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
    password = data.get("password") 
    
    user_data = users_collection.find_one({"username": username})
    
    if not user_data:
        return jsonify({"error": "User not found. Please register first."}), 404
        

    if not check_password_hash(user_data["password"], password):
        return jsonify({"error": "Incorrect password. Access denied."}), 401
        
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
    
    all_users = users_collection.find({}, {"_id": 0, "private_key": 0, "password": 0})
    
    for user in all_users:
        balance = blockchain.get_balance(user['public_key'])
        wallets_list.append({
            "username": user['username'],
            "public_key": user['public_key'],
            "balance": balance
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
    block = blockchain.mine_block()
    if "_id" in block:
        del block["_id"]
    return jsonify(block)

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