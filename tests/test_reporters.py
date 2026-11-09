"""
Unit tests for Reporters (JSON, Markdown, Terminal).
"""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from qnx_sentinel.core.models import (
    AnalysisReport,
    ProjectStructure,
    SDKEnvironment,
    Finding,
    FindingCategory,
    Severity,
)
from qnx_sentinel.reporter.terminal_reporter import TerminalReporter
from qnx_sentinel.reporter.json_reporter import JSONReporter
from qnx_sentinel.reporter.markdown_reporter import MarkdownReporter
from qnx_sentinel.reporter.html_reporter import HTMLReporter


class TestReporters(unittest.TestCase):

    def setUp(self):
        struct = ProjectStructure(root_path="/mock/proj", project_name="mock_proj")
        sdk = SDKEnvironment()
        finding = Finding(
            rule_id="QNX-001-EPOLL",
            category=FindingCategory.LINUX_SPECIFIC_SYSCALL,
            severity=Severity.CRITICAL,
            title="epoll test",
            description="test description",
            file_path="main.c",
            line_number=42,
            remediation="Use poll()",
        )
        self.report = AnalysisReport(
            project_name="mock_proj",
            project_path="/mock/proj",
            sdk_status=sdk,
            project_structure=struct,
            findings=[finding],
            recommendations=["Fix epoll"],
        )
        self.report.calculate_score()

    def test_json_reporter(self):
        with TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "report.json"
            JSONReporter.save(self.report, out_file)
            self.assertTrue(out_file.exists())
            data = json.loads(out_file.read_text(encoding="utf-8"))
            self.assertEqual(data["project_name"], "mock_proj")
            self.assertEqual(len(data["findings"]), 1)

    def test_markdown_reporter(self):
        with TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "report.md"
            MarkdownReporter.save(self.report, out_file)
            self.assertTrue(out_file.exists())
            txt = out_file.read_text(encoding="utf-8")
            self.assertIn("# QNX Sentinel", txt)
            self.assertIn("QNX-001-EPOLL", txt)

    def test_terminal_reporter(self):
        rendered = TerminalReporter.render_report(self.report)
        self.assertIn("QNX SENTINEL", rendered)
        self.assertIn("mock_proj", rendered)

    def test_html_reporter(self):
        with TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "report.html"
            HTMLReporter.save(self.report, out_file)
            self.assertTrue(out_file.exists())
            html = out_file.read_text(encoding="utf-8")
            self.assertIn("QNX Sentinel", html)
            self.assertIn("STATIC_EMBEDDED_REPORT", html)


if __name__ == "__main__":
    unittest.main()
