from flask import Flask, request, jsonify
from flask_cors import CORS
from blockchain import Blockchain
import os

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
    data = request.get_json()

    if not data or "data" not in data:
        return jsonify({"error": "Invalid request"}), 400

    tx = data["data"]
    blockchain.add_block([tx])

    return jsonify({"message": "Block added successfully"})

@app.route("/validate", methods=["GET"])
def validate():
    return jsonify({"valid": blockchain.is_valid()})


# 🔥 IMPORTANT FOR LOCAL RUN ONLY
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)