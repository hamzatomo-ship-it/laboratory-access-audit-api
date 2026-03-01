🧪 Laboratory Access Audit API
The **Laboratory Access Audit API** is a RESTful API built with **Flask** that simulates how laboratory information systems (e.g., WinPath/LIMS) validate sample bookings and handle common data integrity issues.

It focuses on real-world validation problems such as:
- Inactive or deprecated reference codes
- Parent–child (foreign key) mismatches (e.g., source code belongs to a different area)
- Invalid, missing, or malformed booking data

The API validates booking requests, returns **clear error responses**, and records booking attempts in an **audit log** for traceability.


🚀 Features
	•	Health Check Endpoint (GET /health)
	•	Reference Data Endpoints
	•	GET /area-codes
	•	GET /source-codes
	•	Booking Creation Endpoint
	•	POST /bookings
	•	Validates payload before insert
	•	Audit Trail
	•	Logs booking rejections and key events
	•	MySQL Persistence
	•	Bookings stored in MySQL
	•	Secure Configuration
	•	Database credentials loaded from environment variables
	•	Unit Tests
	•	Validation logic covered with unittest


🏗️ Tech Stack
	•	Python 3
	•	Flask
	•	MySQL
	•	mysql-connector-python
	•	python-dotenv
	•	Postman (for testing)
	•	JSON
	•	unittest (Python built-in testing framework)


📂 Project Structure

laboratory-access-audit-api/
│
├── app.py              # Flask app and routes
├── db.py               # Database connection & inserts
├── validator.py        # Booking validation logic
├── db_test.py          # DB connectivity test script
├── tests/
│   └── test_validator.py
├── requirements.txt
├── .env                # Environment variables (not committed)
├── .gitignore
└── README.md

⚙️ Environment Setup

1️⃣ Create a virtual environment
python -m venv .venv
source .venv/Scripts/activate   # Git Bash (Windows)

2️⃣ Install dependencies
pip install -r requirements.txt

🔐 Environment Variables

This project does not hardcode database credentials. Create a .env file in the project root:
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=lab_audit_db
Environment variables are loaded using python-dotenv.

🗄️ Database Setup
Create the database and table in MySQL:

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

▶️ Running the Application

python app.py

Flask will start on:

http://127.0.0.1:5001

🔍 API Endpoints

GET /health

Response:

{
  "status": "Laboratory Audit API running"
}

Create Booking

POST /bookings


Request body:

{
  "area_code": "RDZ",
  "source_code": "SHORE_456",
  "clinician": "Dr Tim",
  "sample_id": "26B987654"
}
Success response:

{
  "message": "Booking created",
  "data": {
    "booking_id": "BK-0001",
    "status": "BOOKED"
  }
}

✅ Validation Rules
	•	All required fields must be present
	•	area_code must exist and be active
	•	source_code must exist, be active, and belong to the correct area_code
	•	Invalid bookings are rejected and audited

🛡️ Audit Trail
	•	Rejected bookings are logged via an audit insert
	•	Demonstrates security-conscious API design
	•	Simulates traceability and accountability requirements common in healthcare systems

📌 Future Improvements
	•	Persist audit logs in a dedicated audit table
	•	Add authentication (API keys / JWT)
	•	Dockerise the application
	•	Add pagination and filtering to GET endpoints