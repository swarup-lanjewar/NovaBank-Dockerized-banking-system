import os
import jwt
from functools import wraps
from flask import request, jsonify, g
from datetime import datetime, timedelta, UTC

SECRET_KEY = os.getenv("SECRET_KEY")


def generate_token(user_id, account_number, full_name):

    now = datetime.now(UTC)
    payload = {
    "user_id": user_id,
    "account_number": account_number,
    "full_name": full_name,
    "iat": now,
    "exp": now + timedelta(hours=1)
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm="HS256"
    )


def token_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        auth = request.headers.get("Authorization")

        if not auth:
            return jsonify({"message": "Token Missing"}), 401

        try:

            token = auth.split(" ")[1]

            decoded = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=["HS256"]
            )

            g.user = decoded

        except Exception:

            return jsonify({"message": "Invalid Token"}), 401

        return func(*args, **kwargs)

    return wrapper