# Assignment Report
## Student Roll Number Decoder — Flask REST API

**Course**: Service-Oriented Architecture (SOA)  
**Semester**: 7  
**Institute**: Pandit Deendayal Energy University (PDEU), Gandhinagar

---

## 1. Objective

Design and implement a Flask REST API that decodes a PDEU student roll number from a POST request body and returns structured JSON data containing:
- Full branch name
- Enrollment year
- Current expected semester
- Expected degree-completion year

---

## 2. Algorithm

```
INPUT: roll_number (string, from POST body)

STEP 1  — Validate Request
         • Ensure Content-Type is application/json
         • Ensure body is valid JSON
         • Ensure roll_number field is present and non-empty

STEP 2  — Normalise Roll Number
         • Strip surrounding whitespace
         • Convert to uppercase

STEP 3  — Parse Roll Number
         • Apply regex: ^(\d{2})([A-Z]{3})(\d+)(D?)$
         • Extract: YY, BBB, NNN, optional D
         • Reject non-matching strings with HTTP 400

STEP 4  — Resolve Branch
         • Look up BBB in BRANCH_MAP dictionary
         • Return HTTP 400 with error if code not found

STEP 5  — Calculate Enrollment Year
         • enrollment_year = 2000 + int(YY)
         • Reject if enrollment_year > current year (HTTP 400)

STEP 6  — Calculate Expected Completion Year
         • completion_year = enrollment_year + 4

STEP 7  — Calculate Current Semester
         • Use system date (date.today())
         • If month >= 7:  semester = 2*(current_year - enrollment_year) + 1
         • If month < 7:   semester = 2*(current_year - enrollment_year)
         • Cap at 8 (max for 4-year B.Tech)
         • Reject semester < 1 with HTTP 400

STEP 8  — Return JSON Response (HTTP 200)
         {
           roll_number, branch, enrollment_year,
           semester, expected_degree_completion_year, message
         }
```

---

## 3. Tools Used

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Programming language |
| Flask 3.x | REST API framework |
| pytest 8.x | Automated unit & integration tests |
| Postman | Manual API testing with 13 test cases |
| `re` module | Roll-number regex validation |
| `datetime.date` | Semester calculation from system date |

---

## 4. API Endpoint

| Property | Value |
|----------|-------|
| Method | POST |
| URL | `http://127.0.0.1:5000/decode` |
| Content-Type | `application/json` |
| Health check | GET `http://127.0.0.1:5000/health` |

---

## 5. Sample Input and Output

### Input
```json
POST /decode
{
  "roll_number": "23BCP242"
}
```

### Output (25 October 2026)
```json
{
  "roll_number": "23BCP242",
  "branch": "Computer Engineering",
  "enrollment_year": 2023,
  "semester": 7,
  "expected_degree_completion_year": 2027,
  "message": "Roll number decoded successfully"
}
```

---

## 6. Test Cases

### Unit Tests (automated — pytest)
| Test | Input | Expected Output |
|------|-------|----------------|
| Valid standard roll number | `23BCP242` | parsed correctly |
| Leading zeroes preserved | `23ICT003` | seq = "003" |
| Optional D suffix | `24BCP424D` | decoded, D ignored |
| Normalisation | `  23bcp242  ` | uppercased, trimmed |
| Invalid format | `INVALID123` | ValueError |
| Empty string | `""` | ValueError |
| Unknown branch | `XYZ` | ValueError |
| Enrollment year 2023, Oct 2026 | 2023, Oct 2026 | semester = 7 |
| Enrollment year 2024, Oct 2026 | 2024, Oct 2026 | semester = 5 |
| Enrollment year 2025, Oct 2026 | 2025, Oct 2026 | semester = 3 |
| Enrollment year 2026, Oct 2026 | 2026, Oct 2026 | semester = 1 |
| Semester cap | 2022, Oct 2026 | semester = 8 |
| Future enrollment | 2030, Oct 2026 | ValueError |
| Jan-June rule | 2025, Feb 2026 | semester = 2 |

### Integration Tests (via Flask test client)
| Test | Expected HTTP Code |
|------|--------------------|
| Valid POST (23BCP242) | 200 |
| D-suffix roll number | 200 |
| Missing roll_number field | 400 |
| Empty roll_number | 400 |
| Invalid format | 400 |
| Unknown branch code | 400 |
| Malformed JSON body | 400 |
| Wrong Content-Type | 400 |
| GET /decode | 405 |
| GET /health | 200 |

### Manual Tests (Postman — 13 requests)
See `postman_collection.json` for all 13 requests with built-in test scripts.

---

## 7. Conclusion

This Flask application successfully implements a RESTful API that decodes PDEU student roll numbers into meaningful academic data. Key features include:

- **Configurable** branch mapping, degree duration, and academic year start month — all in one place.
- **Robust validation** with clear JSON error responses for all edge cases.
- **Date-injectable semester function** allowing deterministic automated tests.
- **Comprehensive test suite** (pytest) covering both unit and integration scenarios.
- **Complete Postman collection** with 13 manual test cases and automated Postman test scripts.

The application is minimal, easy to explain in a viva, and ready for submission.
