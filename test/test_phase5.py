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
