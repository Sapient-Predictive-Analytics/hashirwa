import json
import subprocess
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.get("/health")
def health():
    return jsonify({"ok": True})

@app.post("/functions/run")
def run_functions():
    payload = request.get_json(silent=True) or {}
    args = payload.get("args", [])

    cmd = ["node", "functions/send.js"]
    if args:
        cmd += ["--"] + [str(a) for a in args]

    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode != 0:
        return jsonify({
            "ok": False,
            "error": "Functions runner failed",
            "stderr": proc.stderr.strip(),
            "stdout": proc.stdout.strip()
        }), 500

    out = proc.stdout.strip()
    try:
        data = json.loads(out)
    except Exception:
        data = {"raw": out}

    return jsonify({"ok": True, "data": data})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
