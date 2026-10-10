import sqlite3
import time
from flask import Flask, request, jsonify

app = Flask(__name__)
DB = "payments.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn, open("schema.sql") as f:
        conn.executescript(f.read())

@app.route("/transaction", methods=["POST"])
def create_transaction():
    data = request.get_json(silent=True)
    if not data:
        return jsonify(error="Invalid JSON"), 400

    required = ["reference_id", "account_id", "amount", "type"]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify(error=f"Missing fields: {missing}"), 400

    if not isinstance(data["amount"], (int, float)) or data["amount"] <= 0:
        return jsonify(error="Amount must be a positive number"), 400
    
    if data["type"] not in ("CREDIT", "DEBIT"):
        return jsonify(error="type must be CREDIT or DEBIT"), 400

    conn = get_db()
    try:
        acc = conn.execute("SELECT * FROM accounts WHERE account_id=?",
                           (data["account_id"],)).fetchone()
        if not acc:
            return jsonify(error="Account not found"), 404

        if data["type"] == "DEBIT" and acc["balance"] < data["amount"]:
            return jsonify(error="Insufficient balance"), 422

        conn.execute(
            "INSERT INTO transactions (reference_id, account_id, amount, type, status) "
            "VALUES (?,?,?,?, 'SUCCESS')",
            (data["reference_id"], data["account_id"], data["amount"], data["type"]))

        delta = data["amount"] if data["type"] == "CREDIT" else -data["amount"]
        conn.execute("UPDATE accounts SET balance = balance + ? WHERE account_id=?",
                     (delta, data["account_id"]))
        conn.commit()
        return jsonify(message="Transaction successful"), 201

    except sqlite3.IntegrityError:
        return jsonify(error="Duplicate reference_id"), 409
    finally:
        conn.close()

@app.route("/transaction/<int:txn_id>", methods=["GET"])
def get_transaction(txn_id):
    time.sleep(8)    
    conn = get_db()
    row = conn.execute("SELECT * FROM transactions WHERE txn_id=?", (txn_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify(error="Transaction not found"), 404
    return jsonify(dict(row)), 200

@app.route("/account/<int:acc_id>", methods=["GET"])
def get_account(acc_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM accounts WHERE account_id=?", (acc_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify(error="Account not found"), 404
    return jsonify(dict(row)), 200

@app.route("/health", methods=["GET"])
def health():
    try:
        conn = get_db()
        conn.execute("SELECT 1")
        conn.close()
        return jsonify(status="ok"), 200
    except Exception:
        return jsonify(status="error"), 503

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)