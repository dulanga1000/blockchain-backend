from flask import Flask, request, jsonify
from flask_cors import CORS
from blockchain import Blockchain
import os

app = Flask(__name__)
CORS(app)

bc = Blockchain()

@app.route("/")
def home():
    return "API Running 🚀"

@app.route("/wallet", methods=["POST"])
def wallet():
    return jsonify(bc.create_wallet())

@app.route("/wallets")
def wallets():
    return jsonify(bc.wallets)

@app.route("/transaction", methods=["POST"])
def tx():
    d = request.json
    ok = bc.add_tx(d["sender"], d["receiver"], d["amount"])
    return jsonify({"success": ok})

@app.route("/mine", methods=["POST"])
def mine():
    miner = request.json["miner"]
    b = bc.mine(miner)
    return jsonify({"index": b.index})

@app.route("/chain")
def chain():
    return jsonify(bc.get_chain())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))