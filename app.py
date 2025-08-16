# app.py
from flask import Flask, request, jsonify
from collections import deque
import time

app = Flask(__name__)

# buffer in memoria (semplice POC)
buffer = deque(maxlen=2000)   # ultime ~2000 misure
last_item = None

@app.get("/")
def home():
    return "OK", 200

@app.route("/ingest", methods=["GET", "POST"])
def ingest():
    """L’ESP32 fa POST qui con JSON. GET solo per test."""
    global last_item
    if request.method == "GET":
        return jsonify(status="ok", method="GET"), 200

    # accetta JSON; se non è JSON, prova a salvare il grezzo come 'line'
    data = request.get_json(silent=True)
    if data is None:
        raw = request.data.decode("utf-8", "ignore")
        data = {"line": raw}

    # timestamp server-side
    data["ts"] = int(time.time())

    # log minimale su stdout (Render Logs)
    print({"ingest": data}, flush=True)

    # memorizza in RAM
    buffer.append(data)
    last_item = data

    return jsonify(ok=True), 200

@app.get("/api/last")
def api_last():
    """Ultima misura disponibile (senza auth)."""
    if not last_item:
        return jsonify(None), 204
    return jsonify(last_item), 200

@app.get("/api/history")
def api_history():
    """Storico recente, parametro ?limit=N (default 100)."""
    try:
        limit = int(request.args.get("limit", 100))
    except Exception:
        limit = 100
    data = list(buffer)[-limit:]
    return jsonify(data), 200

