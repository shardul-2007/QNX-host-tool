"""
QNX Sentinel - Standalone HTML Reporter
Generates self-contained, offline HTML audit reports with embedded CSS/JS
for sharing as CI/CD artifacts or documentation deliverables.
"""

import json
from pathlib import Path
from qnx_sentinel.core.models import AnalysisReport


class HTMLReporter:
    """Renders a self-contained single-file HTML report with embedded analysis data."""

    @staticmethod
    def render(report: AnalysisReport) -> str:
        template_path = Path(__file__).resolve().parent.parent / "templates" / "web" / "index.html"
        if not template_path.is_file():
            return f"<html><body><h1>QNX Sentinel Report: {report.project_name}</h1><p>Score: {report.score}</p></body></html>"

        html_content = template_path.read_text(encoding="utf-8")
        report_json = report.to_json()

        # Inject report data directly into the HTML so it displays offline without fetch()
        injection = f"""
        <script>
          // Injected static report data for offline viewing
          const STATIC_EMBEDDED_REPORT = {report_json};
          window.onload = function() {{
            reportData = STATIC_EMBEDDED_REPORT;
            renderDashboard(reportData);
          }};
        </script>
        </body>
        """
        html_content = html_content.replace("window.onload = fetchReport;", "")
        html_content = html_content.replace("</body>", injection)
        return html_content

    @staticmethod
    def save(report: AnalysisReport, output_path: str | Path) -> Path:
        out = Path(output_path).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(HTMLReporter.render(report), encoding="utf-8")
        return out
