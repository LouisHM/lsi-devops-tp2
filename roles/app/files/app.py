import os

from flask import Flask, jsonify
import pymysql

app = Flask(__name__)


def get_db_connection():
    return pymysql.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "appuser"),
        password=os.environ.get("DB_PASSWORD", "apppassword"),
        database=os.environ.get("DB_NAME", "devopsapp"),
        connect_timeout=5,
    )


@app.route("/")
def index():
    return "Hello DevOps!\n"


@app.route("/health")
def health():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "ok", "db": "connected"})
    except Exception as exc:
        return jsonify({"status": "error", "db": str(exc)}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("APP_PORT", 5000)))
