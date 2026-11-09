"""
Script to generate sample diagnostic reports for both clean and legacy sample projects.
"""

import sys
from pathlib import Path

# Add project root to path for standalone execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from qnx_sentinel.audit.sdk_auditor import SDKAuditor
from qnx_sentinel.analyzer.project_analyzer import ProjectAnalyzer
from qnx_sentinel.analyzer.compatibility_engine import CompatibilityEngine
from qnx_sentinel.reporter.json_reporter import JSONReporter
from qnx_sentinel.reporter.markdown_reporter import MarkdownReporter
from qnx_sentinel.reporter.html_reporter import HTMLReporter
from qnx_sentinel.core.models import AnalysisReport

def generate_for_project(proj_path: Path, out_dir: Path):
    auditor = SDKAuditor()
    sdk = auditor.audit()

    analyzer = ProjectAnalyzer(proj_path)
    struct = analyzer.analyze()

    engine = CompatibilityEngine()
    findings = engine.scan_files(struct.source_files + struct.header_files + struct.build_files, proj_path)
    recs = engine.generate_recommendations(findings)

    report = AnalysisReport(
        project_name=struct.project_name,
        project_path=str(proj_path),
        sdk_status=sdk,
        project_structure=struct,
        findings=findings,
        recommendations=recs,
    )
    report.calculate_score()

    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = JSONReporter.save(report, out_dir / f"{struct.project_name}_report.json")
    md_path = MarkdownReporter.save(report, out_dir / f"{struct.project_name}_report.md")
    html_path = HTMLReporter.save(report, out_dir / f"{struct.project_name}_report.html")

    print(f"[+] Generated: {json_path}")
    print(f"[+] Generated: {md_path}")
    print(f"[+] Generated: {html_path}")
    print(f"    Score: {report.score}/100 [{report.grade}] | Total findings: {len(report.findings)}")

def main():
    root = Path(__file__).resolve().parent.parent
    samples_dir = root / "samples"
    reports_dir = root / "reports"

    print("\n=== Generating QNX Sentinel Sample Reports ===\n")
    generate_for_project(samples_dir / "qnx8_sensor_service", reports_dir)
    generate_for_project(samples_dir / "legacy_linux_telematics", reports_dir)
    print("\n[+] Done!\n")

if __name__ == "__main__":
    main()
