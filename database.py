"""
Database & Business Logic Layer for Requirement-to-Test Traceability Tool.
SQLite-backed persistent store with full CRUD, M:N mapping, and RTM analytics.
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = "traceability.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Requirements table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS requirements (
        req_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        priority TEXT NOT NULL DEFAULT 'Medium',
        module TEXT DEFAULT 'General',
        created_at TEXT
    );
    """)

    # Test cases table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_cases (
        test_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        test_type TEXT DEFAULT 'Functional',
        execution_status TEXT NOT NULL DEFAULT 'Not Run',
        execution_notes TEXT,
        last_executed TEXT
    );
    """)

    # M:N Relationship: Requirement <-> Test Case Link table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS req_test_links (
        req_id TEXT NOT NULL,
        test_id TEXT NOT NULL,
        linked_at TEXT,
        PRIMARY KEY (req_id, test_id),
        FOREIGN KEY (req_id) REFERENCES requirements (req_id) ON DELETE CASCADE,
        FOREIGN KEY (test_id) REFERENCES test_cases (test_id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()

# ----------------- CRUD: Requirements ----------------- #

def add_requirement(req_id: str, title: str, description: str, priority: str, module: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute("""
            INSERT INTO requirements (req_id, title, description, priority, module, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (req_id.strip().upper(), title.strip(), description.strip(), priority, module.strip(), now))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def update_requirement(req_id: str, title: str, description: str, priority: str, module: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE requirements
        SET title = ?, description = ?, priority = ?, module = ?
        WHERE req_id = ?
    """, (title.strip(), description.strip(), priority, module.strip(), req_id.strip().upper()))
    conn.commit()
    rows = cursor.rowcount
    conn.close()
    return rows > 0

def delete_requirement(req_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM requirements WHERE req_id = ?", (req_id,))
    conn.commit()
    conn.close()

def get_all_requirements() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM requirements ORDER BY req_id ASC", conn)
    conn.close()
    return df

# ----------------- CRUD: Test Cases ----------------- #

def add_test_case(test_id: str, title: str, description: str, test_type: str, execution_status: str = 'Not Run', notes: str = '') -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO test_cases (test_id, title, description, test_type, execution_status, execution_notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (test_id.strip().upper(), title.strip(), description.strip(), test_type, execution_status, notes.strip()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def update_test_case(test_id: str, title: str, description: str, test_type: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE test_cases
        SET title = ?, description = ?, test_type = ?
        WHERE test_id = ?
    """, (title.strip(), description.strip(), test_type, test_id.strip().upper()))
    conn.commit()
    rows = cursor.rowcount
    conn.close()
    return rows > 0

def update_test_status(test_id: str, status: str, notes: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        UPDATE test_cases
        SET execution_status = ?, execution_notes = ?, last_executed = ?
        WHERE test_id = ?
    """, (status, notes, now, test_id))
    conn.commit()
    conn.close()

def delete_test_case(test_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM test_cases WHERE test_id = ?", (test_id,))
    conn.commit()
    conn.close()

def get_all_test_cases() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM test_cases ORDER BY test_id ASC", conn)
    conn.close()
    return df

# ----------------- Mappings (Links) ----------------- #

def link_requirement_test(req_id: str, test_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute("""
            INSERT INTO req_test_links (req_id, test_id, linked_at)
            VALUES (?, ?, ?)
        """, (req_id, test_id, now))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def unlink_requirement_test(req_id: str, test_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM req_test_links WHERE req_id = ? AND test_id = ?", (req_id, test_id))
    conn.commit()
    conn.close()

def get_all_links() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT l.req_id, r.title AS req_title, l.test_id, t.title AS test_title, t.execution_status
        FROM req_test_links l
        JOIN requirements r ON l.req_id = r.req_id
        JOIN test_cases t ON l.test_id = t.test_id
        ORDER BY l.req_id, l.test_id
    """, conn)
    conn.close()
    return df

# ----------------- Traceability Matrix & Analysis Engine ----------------- #

def calculate_traceability_matrix() -> pd.DataFrame:
    """
    Computes the Forward Traceability Matrix:
    Requirement -> Linked Test Cases -> Individual Statuses -> Aggregated Test Outcome & Coverage Status.
    """
    conn = get_connection()
    
    # Left join ensures requirements with NO tests are retained (vital for gap analysis)
    query = """
    SELECT 
        r.req_id,
        r.title AS req_title,
        r.priority,
        r.module,
        t.test_id,
        t.title AS test_title,
        t.test_type,
        t.execution_status
    FROM requirements r
    LEFT JOIN req_test_links l ON r.req_id = l.req_id
    LEFT JOIN test_cases t ON l.test_id = t.test_id
    ORDER BY r.req_id ASC, t.test_id ASC
    """
    df_raw = pd.read_sql_query(query, conn)
    conn.close()

    if df_raw.empty:
        return pd.DataFrame(columns=[
            "Requirement ID", "Requirement Title", "Priority", "Module",
            "Linked Tests", "Test Count", "Coverage Status", "Test Results", "Overall Outcome"
        ])

    matrix_rows = []
    
    for req_id, group in df_raw.groupby("req_id", sort=False):
        first_row = group.iloc[0]
        req_title = first_row["req_title"]
        priority = first_row["priority"]
        module = first_row["module"]

        # Check if tests exist
        valid_tests = group[group["test_id"].notna()]
        test_count = len(valid_tests)

        if test_count == 0:
            coverage_status = "Untested"
            overall_outcome = "No Tests"
            linked_tests_str = "None"
            results_str = "—"
        else:
            coverage_status = "Covered"
            linked_tests_str = ", ".join(valid_tests["test_id"].tolist())
            statuses = valid_tests["execution_status"].tolist()
            results_str = ", ".join(statuses)

            # Rollup logic:
            # 1. Any Fail -> Fail
            # 2. Else any Blocked -> Blocked
            # 3. Else any Not Run -> Not Run (or Partially Tested)
            # 4. If all Pass -> Pass
            if "Failed" in statuses:
                overall_outcome = "Failed"
            elif "Blocked" in statuses:
                overall_outcome = "Blocked"
            elif "Not Run" in statuses:
                if any(s == "Passed" for s in statuses):
                    overall_outcome = "Partially Run"
                else:
                    overall_outcome = "Not Run"
            elif all(s == "Passed" for s in statuses):
                overall_outcome = "Passed"
            else:
                overall_outcome = "Unknown"

        matrix_rows.append({
            "Requirement ID": req_id,
            "Requirement Title": req_title,
            "Priority": priority,
            "Module": module,
            "Linked Tests": linked_tests_str,
            "Test Count": test_count,
            "Coverage Status": coverage_status,
            "Test Results": results_str,
            "Overall Outcome": overall_outcome
        })

    return pd.DataFrame(matrix_rows)

def calculate_reverse_traceability() -> pd.DataFrame:
    """
    Computes Reverse Traceability:
    Test Case -> Linked Requirements (detects orphan tests).
    """
    conn = get_connection()
    query = """
    SELECT 
        t.test_id,
        t.title AS test_title,
        t.test_type,
        t.execution_status,
        r.req_id,
        r.title AS req_title
    FROM test_cases t
    LEFT JOIN req_test_links l ON t.test_id = l.test_id
    LEFT JOIN requirements r ON l.req_id = r.req_id
    ORDER BY t.test_id ASC
    """
    df_raw = pd.read_sql_query(query, conn)
    conn.close()

    if df_raw.empty:
        return pd.DataFrame()

    rows = []
    for test_id, group in df_raw.groupby("test_id", sort=False):
        first = group.iloc[0]
        valid_reqs = group[group["req_id"].notna()]
        req_count = len(valid_reqs)

        if req_count == 0:
            link_status = "Orphan (No Req)"
            linked_reqs = "None"
        else:
            link_status = "Linked"
            linked_reqs = ", ".join(valid_reqs["req_id"].tolist())

        rows.append({
            "Test ID": test_id,
            "Test Title": first["test_title"],
            "Test Type": first["test_type"],
            "Execution Status": first["execution_status"],
            "Linked Requirements": linked_reqs,
            "Req Count": req_count,
            "Traceability Status": link_status
        })

    return pd.DataFrame(rows)

def get_summary_metrics() -> Dict[str, Any]:
    """Computes summary statistics for KPIs and dashboards."""
    matrix_df = calculate_traceability_matrix()
    test_df = get_all_test_cases()
    req_df = get_all_requirements()

    total_reqs = len(req_df)
    total_tests = len(test_df)

    if total_reqs == 0:
        return {
            "total_reqs": 0,
            "total_tests": total_tests,
            "covered_reqs": 0,
            "untested_reqs": 0,
            "coverage_pct": 0.0,
            "passed_tests": 0,
            "failed_tests": 0,
            "not_run_tests": 0,
            "blocked_tests": 0,
            "pass_rate_pct": 0.0
        }

    covered_reqs = len(matrix_df[matrix_df["Coverage Status"] == "Covered"])
    untested_reqs = total_reqs - covered_reqs
    coverage_pct = round((covered_reqs / total_reqs) * 100, 1)

    passed_tests = len(test_df[test_df["execution_status"] == "Passed"]) if not test_df.empty else 0
    failed_tests = len(test_df[test_df["execution_status"] == "Failed"]) if not test_df.empty else 0
    not_run_tests = len(test_df[test_df["execution_status"] == "Not Run"]) if not test_df.empty else 0
    blocked_tests = len(test_df[test_df["execution_status"] == "Blocked"]) if not test_df.empty else 0

    executed_tests = passed_tests + failed_tests + blocked_tests
    pass_rate_pct = round((passed_tests / executed_tests * 100), 1) if executed_tests > 0 else 0.0

    return {
        "total_reqs": total_reqs,
        "total_tests": total_tests,
        "covered_reqs": covered_reqs,
        "untested_reqs": untested_reqs,
        "coverage_pct": coverage_pct,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "not_run_tests": not_run_tests,
        "blocked_tests": blocked_tests,
        "pass_rate_pct": pass_rate_pct
    }

# ----------------- Sample Data Seeder ----------------- #

def seed_sample_data(force: bool = False):
    """
    Pre-populates the database with realistic sample requirements, test cases,
    and links based on the user's College Login System example.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM requirements")
    count = cursor.fetchone()[0]

    if count > 0 and not force:
        conn.close()
        return

    # Clear existing if force
    if force:
        cursor.execute("DELETE FROM req_test_links")
        cursor.execute("DELETE FROM test_cases")
        cursor.execute("DELETE FROM requirements")
        conn.commit()

    sample_reqs = [
        ("R1", "User Login", "Students and faculty must be able to securely authenticate into the portal.", "High", "Authentication"),
        ("R2", "Password Reset", "Users can request a password reset link sent to their verified email.", "High", "Authentication"),
        ("R3", "Logout", "Active session must terminate cleanly and revoke user authentication tokens.", "Medium", "Authentication"),
        ("R4", "Course Registration", "Students can search, select, and enroll in available semester courses.", "High", "Academic"),
        ("R5", "Grade View", "Students can view transcript records and cumulative GPA.", "Medium", "Academic"),
        ("R6", "Fee Payment Gateway", "Support online tuition payment through debit card and UPI.", "High", "Finance"),
        ("R7", "Profile Picture Upload", "Users can upload avatar in PNG or JPG up to 2MB.", "Low", "User Profile")
    ]

    for req in sample_reqs:
        cursor.execute("""
            INSERT OR IGNORE INTO requirements (req_id, title, description, priority, module, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, req)

    sample_tests = [
        ("TC1", "Valid Credentials Login", "Enter correct student ID and password, verify dashboard loads.", "Functional", "Passed", "Verified on build 1.0"),
        ("TC2", "Incorrect Password Login", "Enter valid ID with incorrect password, expect error message.", "Functional", "Failed", "Shows 500 error instead of invalid password notice"),
        ("TC3", "Password Reset Link Request", "Submit registered email, check if secure reset token received.", "Functional", "Passed", "Token received in inbox"),
        ("TC4", "Enrollment Conflict Check", "Attempt to register for two courses at the same scheduled time.", "Functional", "Passed", "Error modal properly halts conflict"),
        ("TC5", "Course Capacity Limit", "Attempt enrollment when class seat quota is 100% full.", "Functional", "Not Run", "Scheduled for sprint QA test"),
        ("TC6", "Payment Gateway Timeout", "Simulate bank payment gateway connection drop during checkout.", "Integration", "Blocked", "Staging payment sandbox is down"),
        ("TC7", "Orphan Test - Dark Mode Toggle", "Verify switching theme to dark mode updates UI styling.", "UI", "Passed", "Theme persists across reload")
    ]

    for tc in sample_tests:
        cursor.execute("""
            INSERT OR IGNORE INTO test_cases (test_id, title, description, test_type, execution_status, execution_notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, tc)

    sample_links = [
        ("R1", "TC1"),
        ("R1", "TC2"),
        ("R2", "TC3"),
        ("R4", "TC4"),
        ("R4", "TC5"),
        ("R6", "TC6")
        # Notice:
        # R3 (Logout), R5 (Grade View), R7 (Profile Picture) have NO tests! (Untested gap detection!)
        # TC7 has NO requirement link! (Orphan test detection!)
    ]

    for req_id, test_id in sample_links:
        cursor.execute("""
            INSERT OR IGNORE INTO req_test_links (req_id, test_id, linked_at)
            VALUES (?, ?, datetime('now'))
        """, (req_id, test_id))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    seed_sample_data(force=True)
    print("Database initialized and sample data seeded successfully.")
