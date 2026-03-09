from flask import Flask, request, jsonify
from google.cloud import firestore
from datetime import datetime
from google.api_core.datetime_helpers import DatetimeWithNanoseconds
# new linw added
# another CI/CD test
app = Flask(__name__)
db = firestore.Client()
notes_ref = db.collection("notes")

def serialize_note(doc_snapshot):
    d = doc_snapshot.to_dict() if hasattr(doc_snapshot, "to_dict") else dict(doc_snapshot)
    # Normalize timestamp -> ISO 8601 string
    ts = d.get("timestamp")
    if isinstance(ts, DatetimeWithNanoseconds):
        d["timestamp"] = ts.isoformat()
    elif isinstance(ts, datetime):
        # ensure timezone-naive UTC formatted consistently
        d["timestamp"] = ts.isoformat() + "Z" if ts.tzinfo is None else ts.isoformat()
    return {**d, "id": getattr(doc_snapshot, "id", d.get("id"))}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/notes")
def get_notes():
    docs = notes_ref.stream()
    data = [serialize_note(d) for d in docs]
    return jsonify(data), 200

@app.post("/notes")
def create_note():
    body = request.get_json(force=True) or {}
    message = body.get("message")
    if not message:
        return {"error": "message is required"}, 400
    doc = {
        "message": message,
        # You can also use Firestore server timestamp if you prefer:
        # "timestamp": firestore.SERVER_TIMESTAMP,
        "timestamp": datetime.utcnow(),
        "version": "v1"
    }
    notes_ref.add(doc)
    return {"status": "created"}, 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
# test build
# trigger build Mon Mar  9 12:38:41 UTC 2026
