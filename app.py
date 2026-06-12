from flask import Flask, jsonify, request
from datetime import datetime, timezone
from db import insert_booking, insert_audit, get_audit_log
from validator import BookingValidator
from dotenv import load_dotenv
import os
import json
import urllib.request
import urllib.error

load_dotenv()
app = Flask(__name__)

# In-memory "reference data"
# (like lookup tables in WinPath)

AREA_CODES = [
    {"code": "RHM", "name": "University Hospital Southampton NHS Foundation Trust", "active": True},
    {"code": "RDZ", "name": "The Royal Bournemouth and Christchurch Hospitals NHS Foundation Trust", "active": True},
    {"code": "OLD", "name": "Legacy / Decommissioned Trust Code", "active": False},
]

# Source codes belong to an AREA code (simulates "parent key" relationship)
SOURCE_CODES = [
    {"code": "SHORE_456", "name": "Shore Medical Practice", "area_code": "RDZ", "active": True},
    {"code": "SHORE_123", "name": "Shore Medical Practice (old code)", "area_code": "RDZ", "active": False},
    {"code": "UHS_WARD_A1", "name": "Ward A1", "area_code": "RHM", "active": True},
]

# In-memory audit log

AUDIT_LOG = []

# Create validator (first extracted class)
validator = BookingValidator(AREA_CODES, SOURCE_CODES)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def audit(event_type: str, message: str, meta: dict | None = None):
    entry = {
        "timestamp": now_iso(),
        "event_type": event_type,
        "message": message,
        "meta": meta or {},
    }
    AUDIT_LOG.append(entry)


def error_response(http_status: int, error_code: str, message: str, details: dict | None = None):
    return jsonify({
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {}
        }
    }), http_status

# Basic endpoints

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Laboratory Access Audit API is running",
        "version": "0.3.0"
    })


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "laboratory-access-audit-api"
    })

# Reference data endpoints

@app.route("/area-codes", methods=["GET"])
def list_area_codes():
    # Optional filter: ?active=true
    active_filter = request.args.get("active")
    data = AREA_CODES

    if active_filter is not None:
        want_active = active_filter.lower() == "true"
        data = [a for a in AREA_CODES if a["active"] == want_active]

    return jsonify({"data": data})


@app.route("/source-codes", methods=["GET"])
def list_source_codes():
    # Optional filters: ?active=true and/or ?area_code=RDZ
    active_filter = request.args.get("active")
    area_filter = request.args.get("area_code")

    data = SOURCE_CODES

    if active_filter is not None:
        want_active = active_filter.lower() == "true"
        data = [s for s in data if s["active"] == want_active]

    if area_filter:
        data = [s for s in data if s["area_code"] == area_filter]

    return jsonify({"data": data})

# Booking simulation endpoint

@app.route("/bookings", methods=["POST"])
def create_booking():

    print("POST/booking HIT")
    payload = request.get_json(silent=True)

    ok, result = validator.validate(payload)

    if not ok:
        insert_audit(
            "BOOKING_REJECTED",
            result["message"],
            {"payload": payload, "error": result},
        )
        return error_response(
            result["http_status"],
            result["error_code"],
            result["message"],
            result["details"],
        )

    booking_db_id = insert_booking(payload)

    booking = {
        "booking_id": f"BK-{booking_db_id:05d}",
        "sample_id": payload["sample_id"],
        "clinician": payload["clinician"],
        "area_code": payload["area_code"],
        "source_code": payload["source_code"],
        "status": "BOOKED",
        "created_at": now_iso(),
    }

    insert_audit(
        "BOOKING_CREATED",
        f"Sample '{payload['sample_id']}' booked successfully.",
        {"booking": booking},
    )

    return jsonify({"message": "Booking created", "data": booking}), 201

# Audit endpoints

@app.route("/audit", methods=["GET"])
def get_audit():
    # Optional filter: ?event_type=BOOKING_REJECTED
    event_type = request.args.get("event_type")
    data = AUDIT_LOG

    if event_type:
        data = [e for e in data if e["event_type"] == event_type]

    return jsonify({"data": data})


@app.route("/audit/summary", methods=["GET"])
def audit_summary():
    """
    Uses the Anthropic API to generate a plain-English summary of the
    current audit log, highlighting patterns such as repeated rejections,
    common error types, or suspicious activity.
    """
    try:
        audit_entries = get_audit_log(limit=100)
    except Exception as e:
        return error_response(500, "DB_ERROR", "Failed to retrieve audit log from database.", {"detail": str(e)})

    if not audit_entries:
        return jsonify({"summary": "No audit events recorded yet."}), 200

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return error_response(500, "CONFIG_ERROR", "ANTHROPIC_API_KEY is not set.")

    # Build a compact representation of the audit log for the prompt
    log_text = json.dumps(audit_entries, indent=2)

    prompt = (
        "You are an audit analyst for a laboratory information system. "
        "Below is the audit log from the Laboratory Access Audit API. "
        "Each entry has a timestamp, event_type, message, and metadata.\n\n"
        "Please provide a concise plain-English summary that:\n"
        "- States the total number of events\n"
        "- Breaks down successful bookings vs rejections\n"
        "- Highlights any notable patterns (e.g. repeated rejections from the same "
        "clinician, common error codes, mismatched source/area codes)\n"
        "- Flags anything that may warrant further investigation\n\n"
        "Keep the summary clear and professional, as if reporting to a lab manager.\n\n"
        f"Audit log:\n{log_text}"
    )

    request_body = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=request_body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            summary_text = result["content"][0]["text"]
            return jsonify({"summary": summary_text}), 200

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        return error_response(502, "AI_API_ERROR", "Failed to reach Anthropic API.", {"detail": error_body})

    except Exception as e:
        return error_response(500, "UNEXPECTED_ERROR", str(e))


if __name__ == "__main__":
    app.run(debug=True, port=5001)



