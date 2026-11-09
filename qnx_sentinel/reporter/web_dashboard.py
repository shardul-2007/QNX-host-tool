"""
QNX Sentinel - Interactive Local Web Dashboard Server
Zero-dependency embedded HTTP server providing a visual dashboard,
live REST API, and interactive build/test verification.
"""

import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional

from qnx_sentinel.core.models import AnalysisReport
from qnx_sentinel.builder.build_runner import BuildRunner
from qnx_sentinel.builder.config_assistant import ConfigAssistant
from qnx_sentinel.tester.test_runner import TestRunner


class DashboardHandler(BaseHTTPRequestHandler):
    """Handles REST requests and serves the single-page dashboard UI."""

    report: Optional[AnalysisReport] = None
    project_dir: Optional[Path] = None

    def log_message(self, format, *args):
        # Quiet standard HTTP access logs
        return

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/index.html"):
            self._serve_html()
        elif self.path == "/api/report":
            self._serve_report_json()
        else:
            self.send_error(404, "File Not Found")

    def do_POST(self):
        if self.path == "/api/build":
            self._handle_build()
        elif self.path == "/api/test":
            self._handle_test()
        elif self.path == "/api/apply-config":
            self._handle_apply_config()
        else:
            self.send_error(404, "Endpoint Not Found")

    def _serve_html(self):
        html_path = Path(__file__).resolve().parent.parent / "templates" / "web" / "index.html"
        if not html_path.is_file():
            self.send_error(500, "Dashboard template missing")
            return
        content = html_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _serve_report_json(self):
        if not self.report:
            self.send_error(500, "Report not initialized")
            return
        payload = self.report.to_json().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _handle_build(self):
        runner = BuildRunner(self.project_dir or Path("."))
        result = runner.build(target_arch="aarch64le")
        payload = json.dumps(result).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _handle_test(self):
        runner = TestRunner(self.project_dir or Path("."))
        report = runner.run_tests()
        payload = json.dumps(report.to_dict()).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _handle_apply_config(self):
        assistant = ConfigAssistant(self.project_dir or Path("."))
        plans = assistant.plan_changes(self.report.project_structure)
        applied = assistant.apply_plan(plans, confirmed=True)
        # Update missing configs
        self.report.project_structure.missing_configs = []
        self.report.calculate_score()
        payload = json.dumps({"applied": applied, "score": self.report.score}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def start_server(
    report: AnalysisReport,
    project_dir: Path,
    host: str = "127.0.0.1",
    port: int = 8080,
    open_browser: bool = False,
) -> None:
    """Launches the local HTTP server hosting the QNX Sentinel dashboard."""
    DashboardHandler.report = report
    DashboardHandler.project_dir = project_dir

    server_address = (host, port)
    try:
        httpd = HTTPServer(server_address, DashboardHandler)
    except OSError:
        # Fall back to alternative port if 8080 is busy
        port = 8081
        httpd = HTTPServer((host, port), DashboardHandler)

    url = f"http://{host}:{port}"
    print(f"\n[+] QNX Sentinel Interactive Dashboard running at: {url}")
    print("[+] Press Ctrl+C in terminal to stop server.\n")

    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Stopping dashboard server...")
    finally:
        httpd.server_close()
