"""
Automated Unit and Functional Tests for Traceability Engine
"""

import unittest
import database as db

class TestTraceabilityEngine(unittest.TestCase):
    def setUp(self):
        # Reset sample data for consistent test state
        db.seed_sample_data(force=True)

    def test_metrics_calculation(self):
        metrics = db.get_summary_metrics()
        self.assertEqual(metrics["total_reqs"], 7)
        self.assertEqual(metrics["total_tests"], 7)
        self.assertEqual(metrics["covered_reqs"], 4)
        self.assertEqual(metrics["untested_reqs"], 3)
        self.assertAlmostEqual(metrics["coverage_pct"], 57.1, places=1)

    def test_matrix_forward_traceability(self):
        matrix = db.calculate_traceability_matrix()
        
        # Test R1 (Has TC1 Passed, TC2 Failed -> Overall Outcome should be Failed, Coverage should be Covered)
        r1 = matrix[matrix["Requirement ID"] == "R1"].iloc[0]
        self.assertEqual(r1["Coverage Status"], "Covered")
        self.assertEqual(r1["Overall Outcome"], "Failed")
        self.assertEqual(r1["Test Count"], 2)

        # Test R2 (Has TC3 Passed -> Overall Outcome should be Passed, Coverage Covered)
        r2 = matrix[matrix["Requirement ID"] == "R2"].iloc[0]
        self.assertEqual(r2["Coverage Status"], "Covered")
        self.assertEqual(r2["Overall Outcome"], "Passed")

        # Test R3 (Logout - No tests -> Overall Outcome should be No Tests, Coverage Untested)
        r3 = matrix[matrix["Requirement ID"] == "R3"].iloc[0]
        self.assertEqual(r3["Coverage Status"], "Untested")
        self.assertEqual(r3["Overall Outcome"], "No Tests")
        self.assertEqual(r3["Linked Tests"], "None")

        # Test R6 (Fee Payment - Blocked test -> Overall Outcome Blocked)
        r6 = matrix[matrix["Requirement ID"] == "R6"].iloc[0]
        self.assertEqual(r6["Coverage Status"], "Covered")
        self.assertEqual(r6["Overall Outcome"], "Blocked")

    def test_orphan_test_detection(self):
        rev = db.calculate_reverse_traceability()
        tc7 = rev[rev["Test ID"] == "TC7"].iloc[0]
        self.assertEqual(tc7["Traceability Status"], "Orphan (No Req)")
        self.assertEqual(tc7["Linked Requirements"], "None")

    def test_add_and_link_workflow(self):
        # Add new requirement R8
        added_req = db.add_requirement("R8", "Audit Logging", "Log all admin actions", "High", "Security")
        self.assertTrue(added_req)

        # Add new test case TC8
        added_tc = db.add_test_case("TC8", "Admin Action Logged", "Verify log table receives action event", "Functional", "Passed")
        self.assertTrue(added_tc)

        # Link R8 to TC8
        linked = db.link_requirement_test("R8", "TC8")
        self.assertTrue(linked)

        # Recalculate
        matrix = db.calculate_traceability_matrix()
        r8 = matrix[matrix["Requirement ID"] == "R8"].iloc[0]
        self.assertEqual(r8["Coverage Status"], "Covered")
        self.assertEqual(r8["Overall Outcome"], "Passed")

if __name__ == "__main__":
    unittest.main()
