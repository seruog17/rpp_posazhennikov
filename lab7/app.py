from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import os
import threading
import tempfile

DATA_FILE = "data.json"
app = Flask(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per day"]
)
limiter.init_app(app)

def load_data():
    global data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    else:
        data = {}

def save_data():
    dir_name = os.path.dirname(os.path.abspath(DATA_FILE)) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dir_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmpf:
            json.dump(data, tmpf, ensure_ascii=False, indent=2)
        os.replace(tmp_path, DATA_FILE)
    except Exception:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

load_data()

data_lock = threading.Lock()

@app.route("/")
def index():
    return jsonify({"msg": "Key-Value store running"})

@app.route("/set", methods=["POST"])
@limiter.limit("10 per minute")
def set_value():
    payload = request.get_json(force=True, silent=True) or {}
    key = payload.get("key")
    value = payload.get("value")
    if key is None or value is None:
        return jsonify({"error": "key and value required"}), 400
    with data_lock:
        data[str(key)] = value
        save_data()
    return jsonify({"result": "ok", "key": key})

@app.route("/delete/<key>", methods=["DELETE"])
@limiter.limit("10 per minute")
def delete_value(key):
    with data_lock:
        if key in data:
            del data[key]
            save_data()
            return jsonify({"result": "deleted", "key": key})
    return jsonify({"error": "not found"}), 404

@app.route("/exists/<key>", methods=["GET"])
def exists_value(key):
    with data_lock:
        return jsonify({"key": key, "exists": key in data})
    
@app.route("/get/<key>", methods=["GET"])
def get_value(key):
    with data_lock:
        if key in data:
            return jsonify({"key": key, "value": data[key]})
    return jsonify({"error": "not found"}), 404

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
