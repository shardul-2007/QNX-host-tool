"""
Integration tests for CLI commands.
"""

import unittest
from pathlib import Path
from qnx_sentinel.cli import build_parser, cmd_audit, cmd_analyze, cmd_build, cmd_test, cmd_diagnose


class TestCLI(unittest.TestCase):

    def setUp(self):
        self.parser = build_parser()
        self.samples_dir = Path(__file__).resolve().parent.parent / "samples"
        self.clean_proj = self.samples_dir / "qnx8_sensor_service"
        self.legacy_proj = self.samples_dir / "legacy_linux_telematics"

    def test_audit_cli(self):
        args = self.parser.parse_args(["audit"])
        code = cmd_audit(args)
        self.assertEqual(code, 0)

    def test_analyze_clean_project(self):
        args = self.parser.parse_args(["analyze", str(self.clean_proj), "--format", "terminal"])
        code = cmd_analyze(args)
        self.assertEqual(code, 0)

    def test_analyze_fail_under(self):
        # Legacy project scores 0, should fail with exit code 2 when fail-under is 50
        args = self.parser.parse_args(["analyze", str(self.legacy_proj), "--fail-under", "50", "--format", "terminal"])
        code = cmd_analyze(args)
        self.assertEqual(code, 2)

    def test_diagnose_cli(self):
        args = self.parser.parse_args(["diagnose", "fatal error: sys/epoll.h: No such file or directory"])
        code = cmd_diagnose(args)
        self.assertEqual(code, 0)

    def test_build_simulated(self):
        args = self.parser.parse_args(["build", str(self.clean_proj), "--dry-run"])
        code = cmd_build(args)
        self.assertEqual(code, 0)

    def test_test_simulated(self):
        args = self.parser.parse_args(["test", str(self.clean_proj), "--force-simulation"])
        code = cmd_test(args)
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
