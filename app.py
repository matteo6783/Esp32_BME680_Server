from flask import Flask, request, jsonify
app = Flask(__name__)

@app.get("/")
def health():
    return "OK", 200

@app.post("/ingest")
def ingest():
    data = request.get_json(silent=True) or {"line": request.data.decode("utf-8", "ignore")}
    print(data, flush=True)  # visibile nei Logs di Render
    return jsonify(status="ok")
