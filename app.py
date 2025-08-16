from flask import Flask, request, jsonify
from collections import deque
from datetime import datetime

app = Flask(__name__)
LAST = deque(maxlen=1000)

@app.route("/", methods=["GET"])
def home():
    rows = []
    for x in list(LAST)[-50:]:
        rows.append(
            f"<tr><td>{x.get('server_ts','')}</td>"
            f"<td>{x.get('t_c','')}</td>"
            f"<td>{x.get('rh','')}</td>"
            f"<td>{x.get('p_bar','')}</td>"
            f"<td>{x.get('gas_ohm','')}</td>"
            f"<td>{x.get('ms','')}</td></tr>"
        )
    return f"""
    <html><head><meta charset="utf-8"><title>ESP32 BME680</title>
    <style>body{{font-family:sans-serif;margin:24px}}
    table{{border-collapse:collapse;width:100%}}
    th,td{{border:1px solid #ccc;padding:6px;text-align:left}}
    th{{background:#f4f4f4}}</style></head><body>
      <h1>Ultimi campioni ({len(LAST)})</h1>
      <table>
        <thead><tr><th>server_ts</th><th>T (°C)</th><th>RH (%)</th><th>P (bar)</th><th>Gas (Ω)</th><th>ms</th></tr></thead>
        <tbody>{''.join(rows) or '<tr><td colspan=6>Nessun dato ancora</td></tr>'}</tbody>
      </table>
      <p>API JSON: <a href="/last">/last</a></p>
    </body></html>
    """, 200

@app.route("/ingest", methods=["POST"])
def ingest():
    obj = (request.get_json(force=True, silent=False) or {})
    obj["server_ts"] = datetime.utcnow().isoformat() + "Z"
    LAST.append(obj)
    # *** QUESTO è ciò che vuoi vedere nei log ***
    print(obj, flush=True)
    return jsonify({"status": "ok"}), 200

@app.route("/last", methods=["GET"])
def last():
    return jsonify(list(LAST)[-50:]), 200

