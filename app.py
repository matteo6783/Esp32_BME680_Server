# app.py
from flask import Flask, request, jsonify, abort
from collections import deque
import os, time

app = Flask(__name__)

# Token opzionale: imposta API_TOKEN nelle Environment Variables su Render
SECRET_TOKEN = os.getenv("API_TOKEN", "")

# Storage in memoria (demo/POC)
buffer = deque(maxlen=2000)   # ultime ~2000 misure
last_item = None

def check_auth():
    """Se API_TOKEN è definito, richiede header: Authorization: Bearer <token>"""
    if not SECRET_TOKEN:
        return True
    return request.headers.get("Authorization", "") == f"Bearer {SECRET_TOKEN}"

# --- Healthcheck / home ---
@app.get("/")
def home():
    return "OK", 200

# --- Ingest: l’ESP32 fa POST qui. GET è solo diagnostica veloce ---
@app.route("/ingest", methods=["POST", "GET"])
def ingest():
    global last_item
    if request.method == "GET":
        return jsonify(ok=True, count=len(buffer)), 200

    # POST: prova JSON, altrimenti cade su testo grezzo
    item = request.get_json(silent=True)
    if item is None:
        raw = request.data.decode("utf-8", "ignore")
        if not raw:
            return jsonify(ok=False, error="empty body"), 400
        item = {"line": raw}

    # aggiungi timestamp server, salva in RAM e logga
    item["ts"] = int(time.time())
    buffer.append(item)
    last_item = item
    print({"ingest": item}, flush=True)  # visibile nei Logs di Render

    return jsonify(ok=True), 200

# --- API di lettura per client (Qt/QML, ecc.) ---
@app.get("/api/last")
def api_last():
    if not check_auth():
        abort(401)
    if not last_item:
        return jsonify(None), 204
    return jsonify(last_item)

@app.get("/api/history")
def api_history():
    if not check_auth():
        abort(401)
    try:
        limit = min(1000, max(1, int(request.args.get("limit", 100))))
    except:
        limit = 100
    data = list(buffer)[-limit:]
    return jsonify(data)

