import json
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from app import (
    app,
    calculate_semester,
    get_branch_name,
    get_enrollment_year,
    get_expected_completion_year,
    parse_roll_number,
)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def post_decode(client, body, content_type="application/json"):
    return client.post("/decode", data=json.dumps(body), content_type=content_type)


OCT_2026 = date(2026, 10, 25)
FEB_2026 = date(2026, 2, 15)


class TestParseRollNumber:
    def test_valid_standard(self):
        result = parse_roll_number("23BCP242")
        assert result["year_digits"] == "23"
        assert result["branch_code"] == "BCP"
        assert result["seq_number"] == "242"
        assert result["has_d_suffix"] is False
        assert result["roll_number"] == "23BCP242"

    def test_leading_zeroes_preserved(self):
        result = parse_roll_number("23BIT003")
        assert result["seq_number"] == "003"

    def test_optional_d_suffix(self):
        result = parse_roll_number("24BCP424D")
        assert result["has_d_suffix"] is True
        assert result["branch_code"] == "BCP"
        assert result["year_digits"] == "24"

    def test_normalisation_lowercase_input(self):
        result = parse_roll_number("  23bcp242  ")
        assert result["roll_number"] == "23BCP242"

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match="does not match"):
            parse_roll_number("INVALID123")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="empty or whitespace"):
            parse_roll_number("   ")

    def test_non_string_raises(self):
        with pytest.raises(ValueError, match="must be a string"):
            parse_roll_number(23242)


class TestGetEnrollmentYear:
    def test_year_23(self):
        assert get_enrollment_year("23") == 2023

    def test_year_24(self):
        assert get_enrollment_year("24") == 2024

    def test_year_25(self):
        assert get_enrollment_year("25") == 2025

    def test_year_26(self):
        assert get_enrollment_year("26") == 2026


class TestGetBranchName:
    def test_bcp(self):
        assert get_branch_name("BCP") == "Computer Engineering"

    def test_bit(self):
        assert get_branch_name("BIT") == "Information and Communication Technology (ICT)"

    def test_bme(self):
        assert get_branch_name("BME") == "Mechanical Engineering"

    def test_unknown_branch_raises(self):
        with pytest.raises(ValueError, match="not supported"):
            get_branch_name("XYZ")


class TestGetExpectedCompletionYear:
    def test_2023_enrollment(self):
        assert get_expected_completion_year(2023) == 2027

    def test_2024_enrollment(self):
        assert get_expected_completion_year(2024) == 2028

    def test_2025_enrollment(self):
        assert get_expected_completion_year(2025) == 2029

    def test_2026_enrollment(self):
        assert get_expected_completion_year(2026) == 2030


class TestCalculateSemester:
    def test_oct2026_enrollment2026_sem1(self):
        assert calculate_semester(2026, OCT_2026) == 1

    def test_oct2026_enrollment2025_sem3(self):
        assert calculate_semester(2025, OCT_2026) == 3

    def test_oct2026_enrollment2024_sem5(self):
        assert calculate_semester(2024, OCT_2026) == 5

    def test_oct2026_enrollment2023_sem7(self):
        assert calculate_semester(2023, OCT_2026) == 7

    def test_feb2026_enrollment2026_raises(self):
        with pytest.raises(ValueError):
            calculate_semester(2026, FEB_2026)

    def test_feb2026_enrollment2025_sem2(self):
        assert calculate_semester(2025, FEB_2026) == 2

    def test_feb2026_enrollment2024_sem4(self):
        assert calculate_semester(2024, FEB_2026) == 4

    def test_feb2026_enrollment2023_sem6(self):
        assert calculate_semester(2023, FEB_2026) == 6

    def test_future_enrollment_raises(self):
        with pytest.raises(ValueError, match="future"):
            calculate_semester(2030, OCT_2026)

    def test_default_date_does_not_crash(self):
        result = calculate_semester(2020)
        assert isinstance(result, int)


class TestDecodeEndpoint:
    def test_23bcp242_success(self, client):
        resp = post_decode(client, {"roll_number": "23BCP242"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["branch"] == "Computer Engineering"
        assert data["enrollment_year"] == 2023
        assert data["expected_degree_completion_year"] == 2027
        assert data["status"] == "Currently Studying"
        assert data["semester"] is not None

    def test_22bit187_college_completed(self, client):
        resp = post_decode(client, {"roll_number": "22BIT187"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["enrollment_year"] == 2022
        assert data["semester"] is None
        assert data["status"] == "College Completed"
        assert data["expected_degree_completion_year"] == 2026

    def test_21bcp100_college_completed(self, client):
        resp = post_decode(client, {"roll_number": "21BCP100"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["semester"] is None
        assert data["status"] == "College Completed"

    def test_23bcp_currently_studying(self, client):
        resp = post_decode(client, {"roll_number": "23BCP242"})
        data = resp.get_json()
        assert data["status"] == "Currently Studying"
        assert data["semester"] is not None

    def test_24bcp_currently_studying(self, client):
        resp = post_decode(client, {"roll_number": "24BCP045"})
        data = resp.get_json()
        assert data["status"] == "Currently Studying"
        assert data["enrollment_year"] == 2024
        assert data["expected_degree_completion_year"] == 2028

    def test_25bit003_currently_studying(self, client):
        resp = post_decode(client, {"roll_number": "25BIT003"})
        data = resp.get_json()
        assert data["status"] == "Currently Studying"
        assert data["enrollment_year"] == 2025
        assert data["expected_degree_completion_year"] == 2029

    def test_26bcp036_currently_studying(self, client):
        resp = post_decode(client, {"roll_number": "26BCP036"})
        data = resp.get_json()
        assert data["status"] == "Currently Studying"
        assert data["enrollment_year"] == 2026
        assert data["expected_degree_completion_year"] == 2030

    def test_d_suffix_supported(self, client):
        resp = post_decode(client, {"roll_number": "24BCP424D"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["branch"] == "Computer Engineering"
        assert data["enrollment_year"] == 2024

    def test_leading_zeroes_in_seq(self, client):
        resp = post_decode(client, {"roll_number": "23BIT003"})
        assert resp.status_code == 200
        assert resp.get_json()["roll_number"] == "23BIT003"

    def test_lowercase_input_normalised(self, client):
        resp = post_decode(client, {"roll_number": "  23bcp242  "})
        assert resp.status_code == 200
        assert resp.get_json()["roll_number"] == "23BCP242"

    def test_missing_roll_number_field(self, client):
        resp = post_decode(client, {})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_null_roll_number(self, client):
        resp = post_decode(client, {"roll_number": None})
        assert resp.status_code == 400

    def test_empty_roll_number(self, client):
        resp = post_decode(client, {"roll_number": ""})
        assert resp.status_code == 400

    def test_whitespace_roll_number(self, client):
        resp = post_decode(client, {"roll_number": "   "})
        assert resp.status_code == 400

    def test_invalid_format(self, client):
        resp = post_decode(client, {"roll_number": "INVALID123"})
        assert resp.status_code == 400

    def test_unknown_branch_code(self, client):
        resp = post_decode(client, {"roll_number": "23XYZ001"})
        assert resp.status_code == 400

    def test_invalid_json_body(self, client):
        resp = client.post("/decode", data='{"roll_number":', content_type="application/json")
        assert resp.status_code == 400

    def test_wrong_content_type(self, client):
        resp = client.post("/decode", data="roll_number=23BCP242", content_type="application/x-www-form-urlencoded")
        assert resp.status_code == 400

    def test_get_decode_returns_405(self, client):
        resp = client.get("/decode")
        assert resp.status_code == 405


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_returns_json(self, client):
        data = client.get("/health").get_json()
        assert data["status"] == "ok"
