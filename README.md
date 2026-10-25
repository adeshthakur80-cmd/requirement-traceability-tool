Requirement-to-Test Traceability Tool (RTM)

1. Problem Overview
A common pitfall in software engineering is the disconnect between specification and verification.
This tool automates the **Requirements Traceability Matrix (RTM)** workflow:
1. Connects requirements directly to test cases (M:N mapping).
2. Distinguishes **Test Coverage** (whether a requirement has test cases) from **Test Outcome** (whether those tests passed or failed).
3. Automatically identifies **Coverage Gaps** (untested requirements) and **Orphan Tests** (tests without requirements).
4. Generates an interactive, filterable Traceability Matrix with instant CSV export.

2. Technical Architecture & Tech Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Frontend / Dashboard** | **Streamlit (Python)** | Rapid development, reactive UI, native dataframes, Plotly charts, zero-build tooling. |
| **Backend / Logic** | **Python 3.13** | Traceability graph rollup calculations, gap analysis engine, reverse mapping. |
| **Database** | **SQLite3** | Embedded, zero-configuration relational database with foreign key cascading. |
| **Visualizations** | **Plotly Express** | Donut charts for coverage and interactive bar charts for test verdicts. |

Relational Schema (SQLite):
- `requirements`: `(req_id PK, title, description, priority, module, created_at)`
- `test_cases`: `(test_id PK, title, description, test_type, execution_status, execution_notes, last_executed)`
- `req_test_links`: `(req_id FK, test_id FK, linked_at)` — Composite PK supporting many-to-many relationships.

3. Features Implemented

- [x] **Executive Dashboard:** Live KPI metrics (Total Reqs, Total Tests, Coverage %, Pass Rate %) with Donut & Bar charts.
- [x] **Critical Gap Alerts:** Automatic banner highlighting untested High-Priority requirements and failing tests.
- [x] **Interactive Forward RTM:** Full matrix showing Requirement $\rightarrow$ Test Cases $\rightarrow$ Verdicts $\rightarrow$ Overall Health.
- [x] **Reverse Traceability Matrix:** Test Cases $\rightarrow$ Requirements, detecting **Orphan Tests**.
- [x] **Search & Multi-Filters:** Instant filtering by Keyword, Coverage Status (Covered vs Untested), Outcome (Passed/Failed/Blocked/Not Run), and Priority.
- [x] **Requirement & Test Case CRUD:** Complete management UI to add, update, and delete requirements and tests.
- [x] **Quick Execution Tracker:** One-click update of test execution status (Passed, Failed, Blocked, Not Run) with bug/notes.
- [x] **Interactive Linker:** Easy UI to link and unlink test cases to requirements.
- [x] **Data Export:** Instant 1-click download of the complete RTM as a CSV file.
- [x] **1-Click Demo Reset:** Built-in College Login System scenario ready for instant demonstration.

4. How to Run the Prototype

Run the Web Dashboard:
```bash
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501`.

Run Automated Unit Tests:
```bash
python test_traceability.py
```

5. Sample Demonstration Scenario (College Login System)

| Requirement | Priority | Linked Tests | Test Results | Coverage Status | Overall Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **R1 - User Login** | High | TC1, TC2 | Pass, Fail | 🟢 Covered | 🔴 **Failed** |
| **R2 - Password Reset** | High | TC3 | Pass | 🟢 Covered | 🟢 **Passed** |
| **R3 - Logout** | Medium | None | — | 🔴 **Untested** | 🔴 **No Tests** |
| **R4 - Course Registration** | High | TC4, TC5 | Pass, Not Run| 🟢 Covered | 🟡 **Partially Run** |
| **R5 - Grade View** | Medium | None | — | 🔴 **Untested** | 🔴 **No Tests** |
| **R6 - Fee Payment** | High | TC6 | Blocked | 🟢 Covered | 🟠 **Blocked** |
| **TC7 (Dark Mode)** | — | None | Pass | ⚠️ **Orphan Test** | (Detected in Reverse View) |
