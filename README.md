# Laboratory Access Audit API

## Overview

The **Laboratory Access Audit API** is a RESTful API built with Flask that simulates how laboratory information systems (such as WinPath) validate sample bookings and handle common data integrity errors.

The project is inspired by real-world laboratory workflows and errors encountered during sample booking, including:

- Inactive reference codes
- Parent–child (foreign key) mismatches
- Invalid or missing booking data

The API validates booking requests, rejects invalid data with clear error responses, and records all actions in an audit log.

---

## Key Features

- RESTful API using Flask
- Realistic laboratory reference data (area codes & source codes)
- Booking validation with meaningful error messages
- Audit trail of accepted and rejected bookings
- Separation of concerns using classes
- Clear HTTP status codes

---

## Technologies Used

- Python 3
- Flask
- JSON
- Postman (for API testing)

---

## API Endpoints

### Health Check

**GET** `/health`

Returns the service health status.

Example response:

```json
{
  "status": "ok",
  "service": "laboratory-access-audit-api"
}

### List Area Codes

**GET** `/area-codes`

Returns all laboratory area codes.

Optional query parameters:
- `active=true` – return only active area codes


### List Source Codes

**GET** `/source-codes`

Returns laboratory source codes.

Optional query parameters:
- `active=true`
- `area_code=RDZ`


### Create Booking

**POST** `/bookings`

Simulates booking a laboratory sample.

Example request:
```json
{
  "area_code": "RDZ",
  "source_code": "SHORE_456",
  "clinician": "Dr Tim",
  "sample_id": "26B987654"
}
