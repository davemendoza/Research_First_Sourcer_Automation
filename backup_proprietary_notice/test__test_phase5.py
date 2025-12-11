# © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved. Strictly proprietary; no copying, derivative works, reverse engineering, redistribution, or commercial/personal use permitted without written authorization. Governed by Colorado, USA law.
import unittest

# Import the correct Phase 5 module for testing
from phase5 import phase5_dashboard as automation


class TestPhase5Automation(unittest.TestCase):
    """Unit tests for the Phase 5 automation pipeline."""

    def setUp(self):
        # Example input used for testing
        self.sample_input = {"query": "AI Engineer", "region": "US"}

    def test_run_pipeline(self):
        """Ensure the automation pipeline runs without throwing errors."""
        result = automation.run_pipeline(self.sample_input)
        print("🔍 run_pipeline output:", result)
        self.assertIsNotNone(result, "Pipeline returned None")
        self.assertIn("results", result, "Missing 'results' key in output")

    def test_output_format(self):
        """Check that the pipeline output contains required keys."""
        result = automation.run_pipeline(self.sample_input)
        expected_keys = ["results", "timestamp"]
        for key in expected_keys:
            self.assertIn(key, result, f"Missing key '{key}' in output")


if __name__ == "__main__":
    print("✅ Starting Phase5 automation tests...")
    unittest.main(verbosity=2)

Proprietary Rights Notice
------------------------
All code, scripts, GitHub repositories, documentation, data, and GPT-integrated components of the AI Talent Engine – Signal Intelligence and Research_First_Sourcer_Automation Python Automation Sourcing Framework are strictly proprietary. All intellectual property rights, copyrights, trademarks, and related rights are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.
No individual or entity may copy, reproduce, distribute, modify, create derivative works, reverse engineer, decompile, or otherwise use any part of this system, software, or associated materials for personal or commercial purposes without explicit written authorization from Dave Mendoza.
All rights reserved. Unauthorized use may result in legal action.
This statement is governed by the laws of the State of Colorado, USA.
