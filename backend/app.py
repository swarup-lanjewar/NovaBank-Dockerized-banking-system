from flask import Flask, jsonify
from flask_cors import CORS

from auth import auth_bp
from accounts import accounts_bp
from transactions import transactions_bp

app = Flask(__name__)

CORS(app)


# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(accounts_bp, url_prefix="/api")
app.register_blueprint(transactions_bp, url_prefix="/api")


@app.route("/")
def home():
    return jsonify({
        "application": "NovaBank API",
        "status": "Running"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    }), 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )