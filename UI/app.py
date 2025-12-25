from flask import Flask, jsonify, render_template, send_from_directory, abort, request
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder="templates", static_folder="static")

# Path to the directory containing the JSON files (relative to app.py)
JSON_DIR = os.path.join(os.path.dirname(__file__), "../tafsir-json")

# Allow only .json files
def allowed_filename(filename):
    return filename.lower().endswith(".json")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/files")
def api_files():
    try:
        files = [f for f in os.listdir(JSON_DIR) if os.path.isfile(os.path.join(JSON_DIR, f)) and allowed_filename(f)]
        files.sort()
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/file/<path:filename>")
def api_file(filename):
    # Secure filename
    safe = secure_filename(filename)
    if safe != filename:
        # If secure_filename changes the name, we reject it
        return jsonify({"error": "Invalid filename"}), 400

    # Path and check
    file_path = os.path.join(JSON_DIR, filename)
    if not os.path.isfile(file_path) or not allowed_filename(filename):
        return jsonify({"error": "File not found"}), 404

    try:
        # Load file as JSON (so we can validate and return nicely)
        with open(file_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return jsonify({"filename": filename, "content": data})
    except json.JSONDecodeError:
        # If the file is not valid JSON, return the raw content
        with open(file_path, "r", encoding="utf-8") as fh:
            raw = fh.read()
        return jsonify({"filename": filename, "content_raw": raw}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Optional: static files (CSS/JS)
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == "__main__":
    # Start server locally
    app.run(host="127.0.0.1", port=5000, debug=True)