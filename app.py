from flask import Flask, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
import importlib
import json
import threading

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")

app = Flask(__name__, template_folder="templats")
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _load_json(rel_path: str):
    path = rel_path if os.path.isabs(rel_path) else os.path.join(BASE_DIR, rel_path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _get_all_jobs():
    return _load_json(os.path.join("data", "jobs.json"))

def _get_all_candidates():
    return _load_json(os.path.join("data", "candidates.json"))

_seed_lock = threading.Lock()

@app.route("/")
def root():
    return render_template("index.html")



# 1️⃣ Liste des jobs
@app.route("/api/jobs", methods=["GET"])
def get_jobs():
    try:
        jobs = _get_all_jobs()
        return jsonify(jobs)
    except Exception as e:
        return jsonify({"error": "data_unavailable", "detail": str(e)}), 503

# 2️⃣ Candidats par job
@app.route("/api/jobs/<job_id>/candidates", methods=["GET"])
def get_candidates(job_id):
    try:
        candidates = _get_all_candidates()
        filtered = []
        for c in candidates:
            v = c.get("applied_jobs")
            if isinstance(v, list):
                if job_id in v:
                    filtered.append(c)
            else:
                if v == job_id:
                    filtered.append(c)
        return jsonify(filtered)
    except Exception as e:
        return jsonify({"error": "data_unavailable", "detail": str(e)}), 503

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
