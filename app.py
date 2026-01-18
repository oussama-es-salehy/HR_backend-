from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import importlib
import json
import threading

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")

app = Flask(__name__)
CORS(app)

client = MongoClient(
    MONGO_URL,
    serverSelectionTimeoutMS=3000,
    connectTimeoutMS=3000,
    socketTimeoutMS=5000,
)
db = client["hr_db"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _load_json(rel_path: str):
    path = rel_path if os.path.isabs(rel_path) else os.path.join(BASE_DIR, rel_path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _ensure_seed():
    try:
        jobs_count = db.jobs.estimated_document_count()
        candidates_count = db.candidates.estimated_document_count()
        if jobs_count == 0 or candidates_count == 0:
            try:
                jobs = _load_json(os.path.join("data", "jobs.json"))
                candidates = _load_json(os.path.join("data", "candidates.json"))
                if jobs_count == 0 and jobs:
                    db.jobs.insert_many(jobs)
                if candidates_count == 0 and candidates:
                    db.candidates.insert_many(candidates)
            except FileNotFoundError:
                # Fallback: try external seed module if available
                seed_module = importlib.import_module("seed")
                if hasattr(seed_module, "seed"):
                    # ensure seed module uses the same connection if it relies on env
                    os.environ.setdefault("MONGO_URL", MONGO_URL)
                    seed_module.seed()
    except Exception:
        pass

_seed_lock = threading.Lock()
_seed_started = False

def _start_seed_async():
    def _run():
        try:
            _ensure_seed()
        except Exception:
            pass
    t = threading.Thread(target=_run, daemon=True)
    t.start()

def _maybe_seed_once():
    global _seed_started
    if _seed_started:
        return
    with _seed_lock:
        if _seed_started:
            return
        _seed_started = True
        _start_seed_async()

@app.before_request
def _init_data_once():
    _maybe_seed_once()

# Run once at startup as well (in case no requests yet)
_maybe_seed_once()

@app.route("/")
def root():
    return jsonify({"status": "ok"})

@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})

# 1️⃣ Liste des jobs
@app.route("/api/jobs", methods=["GET"])
def get_jobs():
    jobs = list(db.jobs.find({}, {"_id": 0}))
    return jsonify(jobs)

# 2️⃣ Candidats par job
@app.route("/api/jobs/<job_id>/candidates", methods=["GET"])
def get_candidates(job_id):
    candidates = list(
        db.candidates.find(
            {"applied_jobs": job_id},
            {"_id": 0}
        )
    )
    return jsonify(candidates)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
