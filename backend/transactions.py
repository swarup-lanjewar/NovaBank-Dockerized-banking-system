from flask import Blueprint, request, jsonify, g
from db import get_connection
from jwt_utils import token_required
import uuid

transactions_bp = Blueprint("transactions", __name__)


# ----------------------------
# DEPOSIT
# ----------------------------
@transactions_bp.route("/deposit", methods=["POST"])
@token_required
def deposit():

    data = request.get_json()

    try:
        amount = float(data.get("amount"))
    except (TypeError, ValueError):
        return jsonify({"message": "Invalid amount"}), 400
    remarks = data.get("remarks", "Deposit")

    if amount <= 0:
        return jsonify({"message": "Invalid amount"}), 400

    account = g.user["account_number"]

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute(
                """
                UPDATE accounts
                SET balance = balance + %s
                WHERE account_number=%s
                """,
                (amount, account)
            )

            cursor.execute(
                """
                INSERT INTO transactions
                (
                    receiver_account,
                    transaction_type,
                    amount,
                    remarks,
                    reference_id
                )
                VALUES
                (%s,'Deposit',%s,%s,%s)
                """,
                (
                    account,
                    amount,
                    remarks,
                    str(uuid.uuid4())
                )
            )

        conn.commit()

        return jsonify({"message": "Deposit Successful"}), 200

    except Exception as e:

        conn.rollback()

        return jsonify({"message": str(e)}), 500

    finally:
        conn.close()


# ----------------------------
# WITHDRAW
# ----------------------------
@transactions_bp.route("/withdraw", methods=["POST"])
@token_required
def withdraw():

    data = request.get_json()

    try:
        amount = float(data.get("amount"))
    except (TypeError, ValueError):
        return jsonify({"message": "Invalid amount"}), 400
    remarks = data.get("remarks", "Withdraw")

    if amount <= 0:
        return jsonify({"message": "Invalid amount"}), 400

    account = g.user["account_number"]

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT balance
                FROM accounts
                WHERE account_number=%s
                """,
                (account,)
            )

            balance = cursor.fetchone()["balance"]

            if balance < amount:
                return jsonify({"message":"Insufficient Balance"}),400

            cursor.execute(
                """
                UPDATE accounts
                SET balance=balance-%s
                WHERE account_number=%s
                """,
                (amount, account)
            )

            cursor.execute(
                """
                INSERT INTO transactions
                (
                    sender_account,
                    transaction_type,
                    amount,
                    remarks,
                    reference_id
                )
                VALUES
                (%s,'Withdraw',%s,%s,%s)
                """,
                (
                    account,
                    amount,
                    remarks,
                    str(uuid.uuid4())
                )
            )

        conn.commit()

        return jsonify({"message":"Withdrawal Successful"})

    except Exception as e:

        conn.rollback()

        return jsonify({"message":str(e)}),500

    finally:
        conn.close()


# ----------------------------
# TRANSFER
# ----------------------------
@transactions_bp.route("/transfer", methods=["POST"])
@token_required
def transfer():

    data = request.get_json()

    receiver = data.get("receiver_account")
    try:
        amount = float(data.get("amount"))
    except (TypeError, ValueError):
        return jsonify({"message": "Invalid amount"}), 400
    remarks = data.get("remarks", "Transfer")

    sender = g.user["account_number"]

    if amount <= 0:
        return jsonify({"message":"Invalid Amount"}),400

    if sender == receiver:
        return jsonify({"message":"Cannot transfer to same account"}),400

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute(
                "SELECT balance FROM accounts WHERE account_number=%s",
                (sender,)
            )

            sender_data = cursor.fetchone()

            if sender_data is None:
                return jsonify({"message":"Sender not found"}),404

            if sender_data["balance"] < amount:
                return jsonify({"message":"Insufficient Balance"}),400

            cursor.execute(
                "SELECT id FROM accounts WHERE account_number=%s",
                (receiver,)
            )

            if cursor.fetchone() is None:
                return jsonify({"message":"Receiver not found"}),404

            cursor.execute(
                """
                UPDATE accounts
                SET balance=balance-%s
                WHERE account_number=%s
                """,
                (amount, sender)
            )

            cursor.execute(
                """
                UPDATE accounts
                SET balance=balance+%s
                WHERE account_number=%s
                """,
                (amount, receiver)
            )

            cursor.execute(
                """
                INSERT INTO transactions
                (
                    sender_account,
                    receiver_account,
                    transaction_type,
                    amount,
                    remarks,
                    reference_id
                )
                VALUES
                (%s,%s,'Transfer',%s,%s,%s)
                """,
                (
                    sender,
                    receiver,
                    amount,
                    remarks,
                    str(uuid.uuid4())
                )
            )

        conn.commit()

        return jsonify({"message":"Transfer Successful"})

    except Exception as e:

        conn.rollback()

        return jsonify({"message":str(e)}),500

    finally:
        conn.close()


# ----------------------------
# HISTORY
# ----------------------------
@transactions_bp.route("/transactions", methods=["GET"])
@token_required
def history():

    account = g.user["account_number"]

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    transaction_type,
                    sender_account,
                    receiver_account,
                    amount,
                    remarks,
                    status,
                    reference_id,
                    created_at
                FROM transactions
                WHERE sender_account=%s
                   OR receiver_account=%s
                ORDER BY created_at DESC
                """,
                (account, account)
            )

            history = cursor.fetchall()

        return jsonify(history)

    finally:
        conn.close()
