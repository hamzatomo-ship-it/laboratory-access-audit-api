import os
import json
import mysql.connector


def get_db_connection():
    """
    Creates and returns a new MySQL database connection.
    """
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def insert_booking(payload: dict) -> int:
    """
    Inserts a validated booking into the bookings table.
    Returns the newly created booking ID.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO bookings (sample_id, clinician, area_code, source_code, status)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            payload["sample_id"],
            payload["clinician"],
            payload["area_code"],
            payload["source_code"],
            "BOOKED",
        ),
    )

    booking_id = cur.lastrowid

    conn.commit()
    cur.close()
    conn.close()

    return booking_id


def insert_audit(event_type: str, message: str, details: dict | None = None):
    """
    Inserts an audit log entry into the audit_log table.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO audit_log (event_type, message, details)
        VALUES (%s, %s, %s)
        """,
        (
            event_type,
            message,
            json.dumps(details or {}),
        ),
    )

    conn.commit()
    cur.close()
    conn.close()