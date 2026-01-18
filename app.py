from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")

app = Flask(__name__)
CORS(app)

client = MongoClient(MONGO_URL)
db = client["hr_db"]

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
    app.run(debug=True, port=8000)
