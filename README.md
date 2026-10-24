# Student Roll Number Decoder — PDEU SOA Assignment

## Project Title
**Student Roll Number Decoder** — A Flask REST API that decodes a PDEU student roll number and returns the branch, enrollment year, current semester, expected degree-completion year, and academic status in JSON format.

---

## Assignment Objective
Design a Flask application that:
- Accepts a **POST** request containing a student roll number.
- Decodes the roll number into meaningful academic information.
- Returns the result as a structured JSON response.
- Can be tested using **Postman**.

**Course**: Service-Oriented Architecture (SOA) — B.Tech Sem 7
**Institute**: Pandit Deendayal Energy University (PDEU), Gandhinagar

---

## Technologies Used
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Core language |
| Flask | 3.x | REST API framework |
| pytest | 8.x | Automated testing |
| Postman | Any | Manual API testing |

---

## Roll-Number Structure
```
YYBBBNNN  or  YYBBBNNND
│ │  │  └─── Optional literal suffix (D)
│ │  └────── Student sequence number (leading zeroes preserved)
│ └───────── Branch code (3 uppercase letters)
└─────────── Two-digit enrollment year (e.g., 23 → 2023)
```

**Examples**
```
23BCP242   →  2023 | BCP (Computer Engineering)  | seq 242
23BIT187   →  2023 | BIT (ICT)                   | seq 187
24BCP424D  →  2024 | BCP (Computer Engineering)  | seq 424 | D suffix
25BCL041   →  2025 | BCL (Civil Engineering)      | seq 041
```

---

## Branch Mapping Table
| Code | Branch Name |
|------|-------------|
| BCP  | Computer Engineering |
| BIT  | Information and Communication Technology (ICT) |
| BME  | Mechanical Engineering |
| BCL  | Civil Engineering |
| BEC  | Electronics and Communication Engineering |
| BCH  | Chemical Engineering |
| BEE  | Electrical Engineering |
| BBT  | Biotechnology |
| BPE  | Petroleum Engineering |
| BCB  | Computer Science and Business Systems (CSBS) |
| BCT  | Climate Technology |

> Codes not listed above return HTTP 400.

---

## Academic Status — Passed-Out Batches

The 2022 B.Tech batch and all earlier batches have officially passed out.

| Enrollment Year | Status |
|-----------------|--------|
| 2022 or earlier | `"College Completed"` — `semester` is `null` |
| 2023 or later   | `"Currently Studying"` — `semester` calculated dynamically |

The cutoff year (`PASSED_OUT_CUTOFF_YEAR = 2022`) is configurable in `app.py`. Update it when the college confirms a new batch has graduated.

---

## Semester Formula

Academic year starts in **July** (configurable). Two semesters per year.

```
If current month >= 7 (July–December):
    semester = 2 × (current_year − enrollment_year) + 1

If current month < 7 (January–June):
    semester = 2 × (current_year − enrollment_year)

Maximum semester = 8
```

**Expected values on 25 October 2026:**
| Enrollment Year | Semester | Status |
|-----------------|----------|--------|
| 2026 | 1 | Currently Studying |
| 2025 | 3 | Currently Studying |
| 2024 | 5 | Currently Studying |
| 2023 | 7 | Currently Studying |
| 2022 | null | College Completed |
| 2021 | null | College Completed |

> This formula gives the **expected** semester for a normally-progressing student. It cannot account for backlogs, repeated semesters, or special academic arrangements.

---

## Expected Degree Completion Year
```
expected_degree_completion_year = enrollment_year + 4
```

---

## API Endpoint

### POST /decode
**URL**: `http://127.0.0.1:5000/decode`

#### Request
```json
{
  "roll_number": "23BCP242"
}
```

#### Successful Response — Currently Studying (HTTP 200)
```json
{
  "roll_number": "23BCP242",
  "branch": "Computer Engineering",
  "enrollment_year": 2023,
  "semester": 7,
  "expected_degree_completion_year": 2027,
  "status": "Currently Studying",
  "message": "Roll number decoded successfully"
}
```

#### Successful Response — College Completed (HTTP 200)
```json
{
  "roll_number": "22BIT187",
  "branch": "Information and Communication Technology (ICT)",
  "enrollment_year": 2022,
  "semester": null,
  "expected_degree_completion_year": 2026,
  "status": "College Completed",
  "message": "Roll number decoded successfully"
}
```

### GET /health
**URL**: `http://127.0.0.1:5000/health`

**Response (HTTP 200)**:
```json
{
  "status": "ok",
  "message": "Student Roll Number Decoder API is running."
}
```

---

## Error Response Examples

### Missing field (HTTP 400)
```json
{
  "error": "Missing field",
  "details": "The 'roll_number' field is required in the request body."
}
```

### Invalid format (HTTP 400)
```json
{
  "error": "Invalid roll number",
  "details": "'INVALID123' does not match the expected format YYBBBNNN."
}
```

### Unsupported branch (HTTP 400)
```json
{
  "error": "Unsupported branch code",
  "details": "Branch code 'XYZ' is not supported. Supported codes: BBT, BCB, ..."
}
```

---

## Project Structure
```
Student-Roll-Number-Decoder/
├── app.py
├── requirements.txt
├── README.md
├── ASSIGNMENT_REPORT.md
├── .gitignore
├── postman_collection.json
├── tests/
│   └── test_app.py
└── screenshots/
    └── README.txt
```

---

## Windows Installation and Execution

### Step 1 — Create and activate virtual environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### Step 2 — Install dependencies
```powershell
pip install -r requirements.txt
```

### Step 3 — Start the Flask server
```powershell
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

> **Keep this terminal open** while testing in Postman.

---

## Running Automated Tests

Open a second terminal (Flask does not need to be running for tests):

```powershell
pytest
```

Or with verbose output:
```powershell
pytest -v
```

---

## Importing and Running the Postman Collection

1. Open **Postman**.
2. Click **Import** → **Upload Files** → select `postman_collection.json`.
3. Make sure `python app.py` is running.
4. Click each request → **Send**.

---

## Conclusion

This application demonstrates a Flask REST API with input validation, configurable business logic, dynamic semester calculation, and academic status based on the college's actual graduation records. Automated tests cover all batch years and edge cases.
