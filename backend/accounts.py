from flask import Blueprint, jsonify, g
from db import get_connection
from jwt_utils import token_required

accounts_bp = Blueprint("accounts", __name__)


@accounts_bp.route("/balance", methods=["GET"])
@token_required
def get_balance():

    account_number = request.user["account_number"]

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    account_number,
                    balance,
                    status,
                    created_at
                FROM accounts
                WHERE account_number=%s
                """,
                (account_number,)
            )

            account = cursor.fetchone()

            if account is None:
                return jsonify({
                    "message": "Account not found"
                }), 404

            return jsonify(account), 200

    finally:
        conn.close()