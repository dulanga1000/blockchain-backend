from flask import Flask, jsonify, request
from flask_cors import CORS
from blockchain import Blockchain, Wallet, Transaction, MerkleTree, sha256
import json
import traceback

app = Flask(__name__)
CORS(app)  # Required: frontend is on a different origin (Vercel)

# ── In-memory state ────────────────────────────────────────────────────────
blockchain   = Blockchain()
wallets      = {}   # address -> Wallet
pending_txs  = []   # list of Transaction


# ── Health ─────────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Blockchain API running"})


# ── Wallets ────────────────────────────────────────────────────────────────
@app.route("/wallet/create", methods=["POST"])
def create_wallet():
    data = request.get_json() or {}
    name = data.get("name", "Unnamed").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400
    w = Wallet(name)
    wallets[w.address] = w
    return jsonify({
        "name":        w.name,
        "address":     w.address,
        "public_key":  w.public_key,
        "private_key": w.private_key,
    }), 201


@app.route("/wallet/list", methods=["GET"])
def list_wallets():
    return jsonify([
        {"name": w.name, "address": w.address, "public_key": w.public_key}
        for w in wallets.values()
    ])


# ── Transactions ───────────────────────────────────────────────────────────
@app.route("/transaction/create", methods=["POST"])
def create_transaction():
    data = request.get_json() or {}
    for field in ["sender_address", "recipient_address", "amount"]:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    sender_address = data["sender_address"]
    if sender_address not in wallets:
        return jsonify({"error": "Sender wallet not found on this server"}), 404

    tx = Transaction(wallets[sender_address], data["recipient_address"], float(data["amount"]))
    tx.sign()
    pending_txs.append(tx)

    return jsonify({
        "tx_id":     tx.tx_id,
        "sender":    tx.sender,
        "recipient": tx.recipient,
        "amount":    tx.amount,
        "timestamp": tx.timestamp,
        "signature": tx.signature,
        "valid":     tx.is_valid(),
    }), 201


@app.route("/transaction/pending", methods=["GET"])
def get_pending():
    return jsonify([
        {"tx_id": tx.tx_id, "sender": tx.sender,
         "recipient": tx.recipient, "amount": tx.amount,
         "timestamp": tx.timestamp, "valid": tx.is_valid()}
        for tx in pending_txs
    ])


@app.route("/transaction/verify", methods=["POST"])
def verify_transaction():
    data  = request.get_json() or {}
    tx_id = data.get("tx_id")

    tx = next((t for t in pending_txs if t.tx_id == tx_id), None)
    if not tx:
        for block in blockchain.chain:
            tx = next((t for t in block.transactions if t.tx_id == tx_id), None)
            if tx:
                break
    if not tx:
        return jsonify({"error": "Transaction not found"}), 404

    return jsonify({"tx_id": tx.tx_id, "valid": tx.is_valid()})


# ── Mining ─────────────────────────────────────────────────────────────────
@app.route("/mine", methods=["POST"])
def mine():
    if not pending_txs:
        return jsonify({"error": "No pending transactions to mine"}), 400
    try:
        txs_to_mine = list(pending_txs)
        block, attempts, elapsed = blockchain.add_block(txs_to_mine)
        pending_txs.clear()
        return jsonify({
            "block_index":   block.index,
            "hash":          block.hash,
            "previous_hash": block.previous_hash,
            "merkle_root":   block.merkle_root,
            "nonce":         block.nonce,
            "difficulty":    block.difficulty,
            "attempts":      attempts,
            "elapsed_sec":   round(elapsed, 4),
            "tx_count":      len(txs_to_mine),
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Chain ──────────────────────────────────────────────────────────────────
@app.route("/chain", methods=["GET"])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            "index":         block.index,
            "hash":          block.hash,
            "previous_hash": block.previous_hash,
            "merkle_root":   block.merkle_root,
            "timestamp":     block.timestamp,
            "nonce":         block.nonce,
            "difficulty":    block.difficulty,
            "transactions":  [
                {"tx_id": tx.tx_id, "sender": tx.sender,
                 "recipient": tx.recipient, "amount": tx.amount,
                 "timestamp": tx.timestamp, "valid": tx.is_valid()}
                for tx in block.transactions
            ],
        })
    valid, msg = blockchain.is_valid()
    return jsonify({"length": len(blockchain.chain), "valid": valid,
                    "message": msg, "chain": chain_data})


@app.route("/chain/validate", methods=["GET"])
def validate_chain():
    valid, msg = blockchain.is_valid()
    return jsonify({"valid": valid, "message": msg, "length": len(blockchain.chain)})


@app.route("/chain/tamper", methods=["POST"])
def tamper_chain():
    data       = request.get_json() or {}
    bi         = int(data.get("block_index", 1))
    ti         = int(data.get("tx_index", 0))
    new_amount = float(data.get("new_amount", 999.9))

    if bi >= len(blockchain.chain):
        return jsonify({"error": "Block index out of range"}), 400
    block = blockchain.chain[bi]
    if not block.transactions or ti >= len(block.transactions):
        return jsonify({"error": "No transactions in this block"}), 400

    original = block.transactions[ti].amount
    block.transactions[ti].amount = new_amount
    block.merkle_root = MerkleTree(block.transactions).root
    block.hash = sha256(json.dumps({
        "index": block.index, "previous_hash": block.previous_hash,
        "timestamp": block.timestamp, "merkle_root": block.merkle_root,
        "nonce": block.nonce,
    }, sort_keys=True))

    valid, msg = blockchain.is_valid()
    return jsonify({
        "original_amount": original,
        "tampered_amount": new_amount,
        "chain_valid":     valid,
        "detection":       msg,
        "explanation": (
            "Changing TX data changes the Merkle root, which changes the block hash, "
            "which breaks the previous_hash link in the next block. "
            "The attacker would need to re-mine ALL subsequent blocks to fix this — "
            "the 51% attack requirement (Report Section 3.4.1)."
        ),
    })


@app.route("/chain/reset", methods=["POST"])
def reset_chain():
    global blockchain, wallets, pending_txs
    blockchain  = Blockchain()
    wallets     = {}
    pending_txs = []
    return jsonify({"message": "Blockchain reset to genesis"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
