"""
Unit tests for Compatibility Engine and individual static analysis rules.
"""

import unittest
from pathlib import Path
from qnx_sentinel.analyzer.compatibility_engine import CompatibilityEngine
from qnx_sentinel.core.models import Severity


class TestCompatibilityEngine(unittest.TestCase):

    def setUp(self):
        self.samples_dir = Path(__file__).resolve().parent.parent / "samples"
        self.clean_proj = self.samples_dir / "qnx8_sensor_service"
        self.legacy_proj = self.samples_dir / "legacy_linux_telematics"
        self.engine = CompatibilityEngine()

    def test_clean_project_findings(self):
        files = [
            "src/main.c",
            "src/sensor_mgr.c",
            "src/sensor_mgr.h",
            "CMakeLists.txt",
        ]
        findings = self.engine.scan_files(files, self.clean_proj)
        self.assertEqual(len(findings), 0)

    def test_legacy_project_findings(self):
        files = [
            "src/event_loop.c",
            "src/ipc_channel.c",
            "src/daemon.cpp",
            "src/telemetry.cpp",
            "CMakeLists.txt",
        ]
        findings = self.engine.scan_files(files, self.legacy_proj)
        self.assertGreater(len(findings), 10)

        rule_ids = {f.rule_id for f in findings}
        self.assertIn("QNX-001-EPOLL", rule_ids)
        self.assertIn("QNX-002-TIMERFD", rule_ids)
        self.assertIn("QNX-003-EVENTFD", rule_ids)
        self.assertIn("QNX-010-PTHREAD-YIELD", rule_ids)
        self.assertIn("QNX-011-GET-CURRENT-DIR-NAME", rule_ids)
        self.assertIn("QNX-020-PROC-SELF-EXE", rule_ids)
        self.assertIn("QNX-030-PRCTL", rule_ids)
        self.assertIn("QNX-040-SYSV-IPC", rule_ids)
        self.assertIn("QNX-050-LANG-CPP", rule_ids)
        self.assertIn("QNX-051-HOST-LIBRARIES", rule_ids)

        # Check severity assignment
        critical_findings = [f for f in findings if f.severity == Severity.CRITICAL]
        self.assertGreater(len(critical_findings), 0)

    def test_recommendation_generation(self):
        files = ["src/event_loop.c"]
        findings = self.engine.scan_files(files, self.legacy_proj)
        recs = self.engine.generate_recommendations(findings)
        self.assertTrue(any("epoll" in r.lower() for r in recs))
        self.assertTrue(any("timerfd" in r.lower() for r in recs))


if __name__ == "__main__":
    unittest.main()
