import re
from datetime import date
from flask import Flask, jsonify, request

app = Flask(__name__)

DEGREE_DURATION_YEARS = 4
ACADEMIC_YEAR_START_MONTH = 7
SEMESTERS_PER_YEAR = 2
MAX_SEMESTER = DEGREE_DURATION_YEARS * SEMESTERS_PER_YEAR  # 8

# Last enrollment year whose batch has officially passed out.
# Update this value when the college confirms a new batch has graduated.
PASSED_OUT_CUTOFF_YEAR = 2022

BRANCH_MAP = {
    "BCP": "Computer Engineering",
    "BIT": "Information and Communication Technology (ICT)",
    "BME": "Mechanical Engineering",
    "BCL": "Civil Engineering",
    "BEC": "Electronics and Communication Engineering",
    "BCH": "Chemical Engineering",
    "BEE": "Electrical Engineering",
    "BBT": "Biotechnology",
    "BPE": "Petroleum Engineering",
    "BCB": "Computer Science and Business Systems (CSBS)",
    "BCT": "Climate Technology",
}

ROLL_NUMBER_PATTERN = re.compile(r"^(\d{2})([A-Z]{3})(\d+)(D?)$", re.IGNORECASE)


def parse_roll_number(raw):
    if not isinstance(raw, str):
        raise ValueError("Roll number must be a string.")
    cleaned = raw.strip().upper()
    if not cleaned:
        raise ValueError("Roll number must not be empty or whitespace-only.")
    match = ROLL_NUMBER_PATTERN.match(cleaned)
    if not match:
        raise ValueError(
            f"'{cleaned}' does not match the expected format YYBBBNNN "
            "(e.g. 23BCP242 or 24BCP424D)."
        )
    year_digits, branch_code, seq_number, d_suffix = match.groups()
    return {
        "roll_number": cleaned,
        "year_digits": year_digits,
        "branch_code": branch_code.upper(),
        "seq_number": seq_number,
        "has_d_suffix": d_suffix.upper() == "D",
    }


def get_branch_name(branch_code):
    if branch_code not in BRANCH_MAP:
        supported = ", ".join(sorted(BRANCH_MAP.keys()))
        raise ValueError(
            f"Branch code '{branch_code}' is not supported. "
            f"Supported codes: {supported}."
        )
    return BRANCH_MAP[branch_code]


def get_enrollment_year(year_digits):
    return 2000 + int(year_digits)


def get_expected_completion_year(enrollment_year):
    return enrollment_year + DEGREE_DURATION_YEARS


def calculate_semester(enrollment_year, reference_date=None):
    if reference_date is None:
        reference_date = date.today()

    current_year = reference_date.year
    current_month = reference_date.month

    if enrollment_year > current_year:
        raise ValueError(
            f"Enrollment year {enrollment_year} is in the future "
            f"(current year: {current_year})."
        )

    if current_month >= ACADEMIC_YEAR_START_MONTH:
        semester = SEMESTERS_PER_YEAR * (current_year - enrollment_year) + 1
    else:
        semester = SEMESTERS_PER_YEAR * (current_year - enrollment_year)

    if semester < 1:
        raise ValueError(
            f"Calculated semester ({semester}) is less than 1. "
            "The student may not have started yet."
        )

    return min(semester, MAX_SEMESTER)


def error_response(message, details="", status=400):
    body = {"error": message}
    if details:
        body["details"] = details
    return jsonify(body), status


@app.route("/decode", methods=["POST"])
def decode():
    if not request.is_json:
        return error_response(
            "Invalid request",
            "Request body must be JSON with Content-Type: application/json.",
        )

    data = request.get_json(silent=True)
    if data is None:
        return error_response("Invalid JSON", "The request body could not be parsed as valid JSON.")

    if "roll_number" not in data:
        return error_response("Missing field", "The 'roll_number' field is required in the request body.")

    raw_roll = data["roll_number"]

    if raw_roll is None:
        return error_response("Invalid roll number", "The 'roll_number' field must not be null.")

    try:
        parsed = parse_roll_number(raw_roll)
    except ValueError as exc:
        return error_response("Invalid roll number", str(exc))

    try:
        branch = get_branch_name(parsed["branch_code"])
    except ValueError as exc:
        return error_response("Unsupported branch code", str(exc))

    enrollment_year = get_enrollment_year(parsed["year_digits"])
    completion_year = get_expected_completion_year(enrollment_year)

    if enrollment_year <= PASSED_OUT_CUTOFF_YEAR:
        return jsonify({
            "roll_number": parsed["roll_number"],
            "branch": branch,
            "enrollment_year": enrollment_year,
            "semester": None,
            "expected_degree_completion_year": completion_year,
            "status": "College Completed",
            "message": "Roll number decoded successfully",
        }), 200

    try:
        semester = calculate_semester(enrollment_year)
    except ValueError as exc:
        return error_response("Invalid enrollment year", str(exc))

    return jsonify({
        "roll_number": parsed["roll_number"],
        "branch": branch,
        "enrollment_year": enrollment_year,
        "semester": semester,
        "expected_degree_completion_year": completion_year,
        "status": "Currently Studying",
        "message": "Roll number decoded successfully",
    }), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "Student Roll Number Decoder API is running.",
    }), 200


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
