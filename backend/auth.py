from flask import Blueprint, request, jsonify
from db import get_connection
from jwt_utils import generate_token
import bcrypt
import random
import re

auth_bp = Blueprint("auth", __name__)


def generate_unique_account(cursor):

    while True:

        account = random.randint(1000000000, 9999999999)

        cursor.execute(
            "SELECT id FROM accounts WHERE account_number=%s",
            (account,)
        )

        if cursor.fetchone() is None:
            return account


# -------------------------
# REGISTER
# -------------------------

@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not full_name or not email or not password:
        return jsonify({"message": "All fields are required"}), 400

    if len(password) < 8:
        return jsonify({"message": "Password must be at least 8 characters"}), 400

    email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

    if not re.match(email_regex, email):
        return jsonify({"message": "Invalid email"}), 400

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute(
                "SELECT id FROM users WHERE email=%s",
                (email,)
            )

            if cursor.fetchone():
                return jsonify({"message": "Email already registered"}), 409

            hashed_password = bcrypt.hashpw(
                password.encode(),
                bcrypt.gensalt()
            ).decode()

            cursor.execute(
                """
                INSERT INTO users(full_name,email,password)
                VALUES(%s,%s,%s)
                """,
                (full_name, email, hashed_password)
            )

            user_id = cursor.lastrowid

            account_number = generate_unique_account(cursor)

            cursor.execute(
                """
                INSERT INTO accounts
                (user_id,account_number,balance)
                VALUES(%s,%s,%s)
                """,
                (user_id, account_number, 0)
            )

        conn.commit()

        return jsonify({
            "message": "Registration Successful",
            "account_number": account_number
        }), 201

    except Exception as e:

        conn.rollback()

        return jsonify({
            "message": str(e)
        }), 500

    finally:

        conn.close()


# -------------------------
# LOGIN
# -------------------------

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""
            SELECT
                users.id,
                users.full_name,
                users.password,
                accounts.account_number,
                accounts.status

            FROM users

            JOIN accounts
            ON users.id=accounts.user_id

            WHERE email=%s
            """, (email,))

            user = cursor.fetchone()

        if user is None:
            return jsonify({"message":"Invalid Email or Password"}),401

        if user["status"] != "ACTIVE":
            return jsonify({"message":"Account Blocked"}),403

        if not bcrypt.checkpw(
            password.encode(),
            user["password"].encode()
        ):
            return jsonify({"message":"Invalid Email or Password"}),401

        token = generate_token(
            user["id"],
            user["account_number"]
            user["full_name"]

        )

        return jsonify({

            "message":"Login Successful",

            "token":token,

            "account_number":user["account_number"],

            "name":user["full_name"]

        })

    finally:

        conn.close()