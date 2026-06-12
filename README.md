# 🧪 Laboratory Access Audit API

A Flask REST API simulating real-world laboratory information system (LIMS) validation logic. Built to mirror the kind of data integrity, access control, and audit trail requirements found in healthcare IT systems such as WinPath.

It focuses on real-world validation problems such as:
- Inactive or deprecated reference codes
- Parent–child (foreign key) mismatches (e.g., source code belongs to a different area)
- Invalid, missing, or malformed booking data

The API validates booking requests, returns **clear error responses**, records booking attempts in a **persistent audit log**, and includes an **AI-powered summary endpoint** that automatically generates plain-English audit reports from the database.

---

## 🚀 Features

- **Health Check Endpoint** — `GET /health`
- **Reference Data Endpoints**
  - `GET /area-codes`
  - `GET /source-codes`
- **Booking Creation Endpoint**
  - `POST /bookings` — validates payload before inserting into MySQL
- **Audit Trail**
  - All booking events (successes and rejections) persisted to a dedicated `audit_log` table in MySQL
  - `GET /audit` — retrieve raw audit log entries, filterable by event type
- **AI-Powered Audit Summary** *(new in v0.3.0)*
  - `GET /audit/summary` — queries the audit log database and calls the Anthropic API to generate a structured plain-English report, identifying patterns such as repeated clinician errors, rejection categories, and prioritised recommendations
- **MySQL Persistence** — bookings and audit entries stored in MySQL
- **Secure Configuration** — all credentials loaded from environment variables
- **Unit Tests** — validation logic covered with `unittest`

---

## 🏗️ Tech Stack

- Python 3
- Flask
- MySQL
- mysql-connector-python
- python-dotenv
- Anthropic API (via Python built-in `urllib`  no extra package required)
- Postman (for testing)
- unittest (Python built-in testing framework)

---

## 📂 Project Structure

```
laboratory-access-audit-api/
│
├── app.py                  # Flask app and routes
├── db.py                   # Database connection, inserts, and audit log retrieval
├── validator.py            # Booking validation logic
├── db_test.py              # DB connectivity test script
├── tests/
│   └── test_validator.py
├── requirements.txt
├── .env                    # Environment variables (not committed)
├── .gitignore
└── README.md
```

---

## ⚙️ Environment Setup

**1️⃣ Create a virtual environment**
```bash
python -m venv .venv
source .venv/Scripts/activate   # Git Bash (Windows)
```

**2️⃣ Install dependencies**
```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

This project does not hardcode any credentials. Create a `.env` file in the project root:

```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=lab_audit_db
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

- Database credentials are used by `db.py` to connect to MySQL
- `ANTHROPIC_API_KEY` is required for the `GET /audit/summary` endpoint
- Get your Anthropic API key at: https://console.anthropic.com
- Environment variables are loaded using `python-dotenv`

---

## 🗄️ Database Setup

Create the database and tables in MySQL:

```sql
CREATE DATABASE lab_audit_db;
USE lab_audit_db;

CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id VARCHAR(20) NOT NULL,
    sample_id VARCHAR(50) NOT NULL,
    clinician VARCHAR(100) NOT NULL,
    area_code VARCHAR(10) NOT NULL,
    source_code VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'BOOKED',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    details JSON,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

> If you created `audit_log` without the `created_at` column, run:
> ```sql
> ALTER TABLE audit_log ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;
> ```

---

## ▶️ Running the Application

```bash
python app.py
```

Flask will start on:
```
http://127.0.0.1:5001
```

---

## 🔍 API Endpoints

### `GET /health`
```json
{ "status": "ok", "service": "laboratory-access-audit-api" }
```

---

### `POST /bookings`

**Request body:**
```json
{
  "area_code": "RDZ",
  "source_code": "SHORE_456",
  "clinician": "Dr Tim",
  "sample_id": "26B987654"
}
```

**Success response (201):**
```json
{
  "message": "Booking created",
  "data": {
    "booking_id": "BK-00001",
    "status": "BOOKED"
  }
}
```

**Rejection response (400/422):**
```json
{
  "error": {
    "code": "PARENT_KEY_MISMATCH",
    "message": "Source code does not belong to the given area code.",
    "details": {}
  }
}
```

---

### `GET /audit`

Returns all audit log entries. Optional filter:
```
GET /audit?event_type=BOOKING_REJECTED
```

---

### `GET /audit/summary` *(AI-powered)*

Queries the `audit_log` table and sends the data to the Anthropic API, returning a structured plain-English report.

**Example response:**
```json
{
  "summary": "Total Events: 26 | Successful Bookings: 11 | Rejected: 15 (42% success rate). Notable: Dr Jones submitted 5 rejections within 2 hours using invalid area/source code combinations — possible training gap. Dr Tim had 4 consecutive rejections due to case sensitivity ('Rhm' instead of 'RHM'). Recommendations: contact Dr Jones, review inactive source code SHORE_123, consider case-insensitive validation."
}
```

> Requires `ANTHROPIC_API_KEY` to be set in `.env`. Uses `claude-haiku-4-5` model via Python's built-in `urllib` library.

---

## ✅ Validation Rules

- All required fields must be present (`sample_id`, `clinician`, `area_code`, `source_code`)
- `area_code` must exist and be active
- `source_code` must exist, be active, and belong to the correct `area_code`
- Invalid bookings are rejected with a structured error and logged to the audit table

---

## 🛡️ Audit Trail

- All booking events (successes and rejections) are persisted to the `audit_log` MySQL table
- Survives server restarts — data is never lost between sessions
- The `/audit/summary` endpoint transforms raw log entries into actionable clinical reports
- Simulates the traceability and accountability requirements common in regulated healthcare systems

---

## 📌 Future Improvements

- Add authentication (API keys / JWT)
- Dockerise the application
- Add pagination and filtering to GET endpoints
- Expand AI summary to support date range filtering
- Add a frontend dashboard to visualise audit trends
