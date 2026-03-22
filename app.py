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