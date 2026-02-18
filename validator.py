class BookingValidator:
    REQUIRED_FIELDS = ["area_code", "source_code", "clinician", "sample_id"]

    def __init__(self, area_codes: list[dict], source_codes: list[dict]):
        self.area_codes = area_codes
        self.source_codes = source_codes

    def find_area(self, code: str):
        return next((a for a in self.area_codes if a["code"] == code), None)

    def find_source(self, code: str):
        return next((s for s in self.source_codes if s["code"] == code), None)

    def validate(self, payload: dict) -> tuple[bool, dict]:
        """
        Returns (is_valid, result)
        - If valid: (True, {"area": ..., "source": ...})
        - If invalid: (False, {"http_status": int, "error_code": str, "message": str, "details": dict})
        """
        if not payload:
            return False, {
                "http_status": 400,
                "error_code": "INVALID_JSON",
                "message": "Request body must be valid JSON.",
                "details": {}
            }

        missing = [f for f in self.REQUIRED_FIELDS if not payload.get(f)]
        if missing:
            return False, {
                "http_status": 400,
                "error_code": "MISSING_FIELDS",
                "message": "Missing required fields.",
                "details": {"missing": missing}
            }

        area_code = payload["area_code"]
        source_code = payload["source_code"]

        area = self.find_area(area_code)
        if not area:
            return False, {
                "http_status": 422,
                "error_code": "AREA_CODE_NOT_FOUND",
                "message": f"Area code '{area_code}' does not exist.",
                "details": {"hint": "Use GET /area-codes to see valid codes."}
            }

        if not area["active"]:
            return False, {
                "http_status": 409,
                "error_code": "AREA_CODE_INACTIVE",
                "message": f"Area code '{area_code}' is inactive and cannot be used.",
                "details": {}
            }

        source = self.find_source(source_code)
        if not source:
            return False, {
                "http_status": 422,
                "error_code": "SOURCE_CODE_NOT_FOUND",
                "message": f"Source code '{source_code}' does not exist.",
                "details": {"hint": "Use GET /source-codes to see valid codes."}
            }

        if not source["active"]:
            return False, {
                "http_status": 409,
                "error_code": "SOURCE_CODE_INACTIVE",
                "message": f"Source code '{source_code}' is inactive and cannot be used.",
                "details": {"example": "Old GP source codes often become inactive after updates."}
            }

        if source["area_code"] != area_code:
            return False, {
                "http_status": 409,
                "error_code": "PARENT_KEY_MISMATCH",
                "message": "The provided source_code does not belong to the provided area_code.",
                "details": {"source_area_code": source["area_code"], "provided_area_code": area_code}
            }

        return True, {"area": area, "source": source}
