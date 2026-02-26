# Laboratory Access Audit API

## Overview
The **Laboratory Access Audit API** is a RESTful API built with **Flask** that simulates how laboratory information systems (e.g., WinPath/LIMS) validate sample bookings and handle common data integrity issues.

It focuses on real-world validation problems such as:
- Inactive or deprecated reference codes
- Parent–child (foreign key) mismatches (e.g., source code belongs to a different area)
- Invalid, missing, or malformed booking data

The API validates booking requests, returns **clear error responses**, and records booking attempts in an **audit log** for traceability.

---

## Key Features
- RESTful API implemented using Flask
- Reference data for **area codes** and **source codes**
- Booking validation based on realistic business rules
- Meaningful error handling with appropriate HTTP status codes
- Audit trail for accepted/rejected bookings
- Unit tests for core validation logic (Python `unittest`)

---

## Technologies Used
- Python 3
- Flask
- JSON
- unittest (Python built-in testing framework)
- Postman (manual API testing)

---

## Getting Started

### 1) Install dependencies
```bash
pip install -r requirements.txt

