from flask import Flask, jsonify, request
from datetime import datetime, timezone
from db import insert_booking, insert_audit
from validator import BookingValidator
from dotenv import load_dotenv
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
        "version": "0.2.0"
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

# Audit endpoint


@app.route("/audit", methods=["GET"])
def get_audit():
    # Optional filter: ?event_type=BOOKING_REJECTED
    event_type = request.args.get("event_type")
    data = AUDIT_LOG

    if event_type:
        data = [e for e in data if e["event_type"] == event_type]

    return jsonify({"data": data})


if __name__ == "__main__":
    app.run(debug=True, port=5001)



