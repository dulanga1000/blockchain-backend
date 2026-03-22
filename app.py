from flask import Flask, request, jsonify
from flask_cors import CORS
from blockchain import Blockchain

app = Flask(__name__)
CORS(app)

blockchain = Blockchain()

@app.route("/")
def home():
    return "Blockchain API Running 🚀"

@app.route("/chain", methods=["GET"])
def get_chain():
    data = []
    for block in blockchain.chain:
        data.append({
            "index": block.index,
            "transactions": block.transactions,
            "hash": block.hash,
            "prev_hash": block.prev_hash
        })
    return jsonify(data)

@app.route("/add", methods=["POST"])
def add_block():
    tx = request.json.get("data")
    blockchain.add_block([tx])
    return jsonify({"message": "Block added"})

@app.route("/validate", methods=["GET"])
def validate():
    return jsonify({"valid": blockchain.is_valid()})