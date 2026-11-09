"""
Unit tests for Test Assistant.
"""

import unittest
from pathlib import Path
from qnx_sentinel.tester.test_runner import TestRunner
from qnx_sentinel.tester.target_detector import TargetDetector


class TestTestRunner(unittest.TestCase):

    def setUp(self):
        self.samples_dir = Path(__file__).resolve().parent.parent / "samples"
        self.clean_proj = self.samples_dir / "qnx8_sensor_service"

    def test_target_detector(self):
        detector = TargetDetector()
        targets = detector.detect_targets()
        self.assertGreater(len(targets), 0)
        sim = next(t for t in targets if t.is_simulated)
        self.assertEqual(sim.target_type, "SIMULATED")

    def test_simulated_test_execution_attribution(self):
        runner = TestRunner(self.clean_proj)
        report = runner.run_tests(force_simulation=True)
        self.assertTrue(report.is_simulated)
        self.assertEqual(report.execution_mode, "SDK_SIMULATED_TARGET")
        self.assertIn("SIMULATION NOTICE", report.raw_output)
        self.assertGreater(report.total_tests, 0)
        self.assertEqual(report.failed, 0)


if __name__ == "__main__":
    unittest.main()
