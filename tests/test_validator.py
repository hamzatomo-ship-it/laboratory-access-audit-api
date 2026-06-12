
import unittest
from validator import BookingValidator


class TestBookingValidator(unittest.TestCase):
    def setUp(self):
        # fresh test data for every test (so tests don't affect each other)
        self.area_codes = [
            {"code": "RHM", "name": "University Hospital Southampton NHS Foundation Trust", "active": True},
            {"code": "RDZ", "name": "The Royal Bournemouth and Christchurch Hospitals NHS Foundation Trust", "active": True},
            {"code": "OLD", "name": "Legacy / Decommissioned Trust Code", "active": False},
        ]

        self.source_codes = [
            {"code": "SHORE_456", "name": "Shore Medical Practice", "area_code": "RDZ", "active": True},
            {"code": "SHORE_123", "name": "Shore Medical Practice (old code)", "area_code": "RDZ", "active": False},
            {"code": "UHS_WARD_A1", "name": "Ward A1", "area_code": "RHM", "active": True},
        ]

        self.validator = BookingValidator(self.area_codes, self.source_codes)

    def test_invalid_json_is_rejected(self):
        payload = None  # simulates no JSON sent

        ok, result = self.validator.validate(payload)

        self.assertFalse(ok)
        self.assertEqual(result["error_code"], "INVALID_JSON")

    def test_missing_fields_returns_error(self):
        payload = {
            "area_code": "RDZ"
        }

        ok, result = self.validator.validate(payload)

        self.assertFalse(ok)
        self.assertEqual(result["error_code"], "MISSING_FIELDS")

    def test_source_code_not_found(self):
        payload ={
            "area_code": "RDZ",
            "source_code": "FAKE_999",  # does not exist
            "clinician": "Dr Tim",
            "sample_id": "26B000004"
        }
        ok, result = self.validator.validate(payload)

        self.assertFalse(ok)
        self.assertEqual(result["error_code"], "SOURCE_CODE_NOT_FOUND")

    def test_inactive_source_is_rejected(self):
        payload = {
            "area_code": "RDZ",
            "source_code": "SHORE_123",  # inactive
            "clinician": "Dr Tim",
            "sample_id": "26B000001"
        }

        ok, result = self.validator.validate(payload)

        self.assertFalse(ok)
        self.assertEqual(result["error_code"], "SOURCE_CODE_INACTIVE")

    def test_parent_key_mismatch(self):
        payload = {
            "area_code": "RHM",
            "source_code": "SHORE_456",  # belongs to RDZ, not RHM
            "clinician": "Dr Tim",
            "sample_id": "26B000002"
        }

        ok, result = self.validator.validate(payload)

        self.assertFalse(ok)
        self.assertEqual(result["error_code"], "PARENT_KEY_MISMATCH")

    def test_valid_booking_passes(self):
        payload = {
            "area_code": "RDZ",
            "source_code": "SHORE_456",
            "clinician": "Dr Tim",
            "sample_id": "26B000003"
        }

        ok, result = self.validator.validate(payload)

        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()