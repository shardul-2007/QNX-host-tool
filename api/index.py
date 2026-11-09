"""
Vercel Serverless Function Handler for QNX Sentinel
Provides REST API endpoints for project analysis, build simulation,
test execution, and diagnostic intelligence.
"""

from http.server import BaseHTTPRequestHandler
import json
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Add repository root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from qnx_sentinel.audit.sdk_auditor import SDKAuditor
from qnx_sentinel.analyzer.project_analyzer import ProjectAnalyzer
from qnx_sentinel.analyzer.compatibility_engine import CompatibilityEngine
from qnx_sentinel.builder.build_runner import BuildRunner
from qnx_sentinel.builder.config_assistant import ConfigAssistant
from qnx_sentinel.tester.test_runner import TestRunner
from qnx_sentinel.diagnostics.error_explainer import ErrorExplainer
from qnx_sentinel.core.models import AnalysisReport


def get_project_dir(proj_name: str) -> Path:
    samples_dir = ROOT_DIR / "samples"
    if proj_name == "qnx8_sensor_service":
        return samples_dir / "qnx8_sensor_service"
    return samples_dir / "legacy_linux_telematics"


def analyze_project(proj_dir: Path) -> AnalysisReport:
    auditor = SDKAuditor()
    sdk = auditor.audit()
    analyzer = ProjectAnalyzer(proj_dir)
    structure = analyzer.analyze()
    engine = CompatibilityEngine()
    findings = engine.scan_files(structure.source_files + structure.header_files + structure.build_files, proj_dir)
    recommendations = engine.generate_recommendations(findings)
    report = AnalysisReport(
        project_name=structure.project_name,
        project_path=str(proj_dir),
        sdk_status=sdk,
        project_structure=structure,
        findings=findings,
        recommendations=recommendations,
    )
    report.calculate_score()
    return report


class handler(BaseHTTPRequestHandler):
    """Serverless request handler compatible with Vercel Python runtime."""

    def log_message(self, format, *args):
        return

    def _send_json(self, data: dict, status: int = 200):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        proj_name = params.get("project", ["legacy_linux_telematics"])[0]
        proj_dir = get_project_dir(proj_name)

        if parsed.path.endswith("/report") or parsed.path == "/api" or parsed.path == "/api/":
            report = analyze_project(proj_dir)
            self._send_json(report.to_dict())
        elif parsed.path.endswith("/audit"):
            sdk = SDKAuditor().audit()
            self._send_json(sdk.to_dict())
        else:
            # Fallback to report
            report = analyze_project(proj_dir)
            self._send_json(report.to_dict())

    def do_POST(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        proj_name = params.get("project", ["legacy_linux_telematics"])[0]
        proj_dir = get_project_dir(proj_name)

        if parsed.path.endswith("/build"):
            runner = BuildRunner(proj_dir)
            arch = params.get("arch", ["aarch64le"])[0]
            result = runner.build(target_arch=arch)
            self._send_json(result)
        elif parsed.path.endswith("/test"):
            runner = TestRunner(proj_dir)
            report = runner.run_tests(force_simulation=True)
            self._send_json(report.to_dict())
        elif parsed.path.endswith("/apply-config"):
            assistant = ConfigAssistant(proj_dir)
            report = analyze_project(proj_dir)
            plans = assistant.plan_changes(report.project_structure)
            # In serverless environment, return simulated plan application
            applied = [f"CONFIGURED: {name} -> {item['reason']}" for name, item in plans.items()]
            self._send_json({"applied": applied, "score": 95.0, "status": "SIMULATED_SERVERLESS_SUCCESS"})
        elif parsed.path.endswith("/diagnose"):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else ""
            try:
                data = json.loads(body)
                log_text = data.get("log", "fatal error: sys/epoll.h: No such file or directory")
            except Exception:
                log_text = body or "fatal error: sys/epoll.h: No such file or directory"

            explainer = ErrorExplainer()
            res = explainer.explain_log(log_text)
            self._send_json({"explanations": [e.to_dict() for e in res]})
        else:
            self.send_error(404, "Endpoint Not Found")
