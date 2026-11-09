"""
QNX Sentinel - Markdown Reporter
Generates comprehensive GitHub Flavored Markdown diagnostic reports.
"""

from pathlib import Path
from typing import List
from qnx_sentinel.core.models import AnalysisReport, Severity


class MarkdownReporter:
    """Exports structured analysis reports to rich Markdown format."""

    @staticmethod
    def render(report: AnalysisReport) -> str:
        lines: List[str] = []

        lines.append(f"# QNX Sentinel — Analysis Report: `{report.project_name}`")
        lines.append("")
        lines.append(f"> **Analysis Timestamp:** `{report.timestamp}`  ")
        lines.append(f"> **Project Root:** `{report.project_path}`  ")
        lines.append(f"> **QNX 8.0 Readiness Index:** **`{report.score}/100`** (Grade: **`{report.grade}`**)")
        lines.append("")

        # Executive Summary
        lines.append("## 1. Executive Summary")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|---|---|")
        lines.append(f"| **Overall Readiness Score** | **{report.score}/100 ({report.grade})** |")
        lines.append(f"| **Total Source Files** | {report.project_structure.metrics.total_files} ({report.project_structure.metrics.c_files} C, {report.project_structure.metrics.cpp_files} C++, {report.project_structure.metrics.header_files} Headers) |")
        lines.append(f"| **Lines of Code** | {report.project_structure.metrics.lines_of_code:,} LOC |")
        lines.append(f"| **Detected Build Systems** | {', '.join(report.project_structure.build_systems) or 'None'} |")
        lines.append(f"| **Critical Compatibility Blockers** | **{report.summary.get('CRITICAL', 0)}** |")
        lines.append(f"| **Portability Warnings** | {report.summary.get('WARNING', 0)} |")
        lines.append(f"| **Microkernel Best Practice Tips** | {report.summary.get('BEST_PRACTICE', 0)} |")
        lines.append(f"| **Informational Notes** | {report.summary.get('INFO', 0)} |")
        lines.append("")

        # SDK Status
        lines.append("## 2. Host QNX SDP 8.0 Environment")
        lines.append("")
        sdk = report.sdk_status
        lines.append(f"- **SDP Detected:** `{'YES' if sdk.is_qnx_sdp_detected else 'NO'}`")
        if sdk.is_qnx_sdp_detected:
            lines.append(f"- **QNX_HOST:** `{sdk.qnx_host}`")
            lines.append(f"- **QNX_TARGET:** `{sdk.qnx_target}`")
            lines.append(f"- **Compiler Driver (`qcc`):** `{sdk.qcc_path}`")
            lines.append(f"- **Supported Targets:** `{', '.join(sdk.supported_targets)}`")
        else:
            lines.append("- **Status:** Running in Host-Static Analysis & Simulation Mode")
            if sdk.env_script_suggested:
                lines.append(f"- **Activation Command:** `{sdk.env_script_suggested}`")
        lines.append(f"- **QEMU Emulator:** `{'AVAILABLE (' + sdk.qemu_binary + ')' if sdk.qemu_available else 'NOT DETECTED'}`")
        lines.append(f"- **mkqnximage Utility:** `{'AVAILABLE' if sdk.mkqnximage_available else 'NOT DETECTED'}`")
        lines.append("")

        # Missing Configurations
        if report.project_structure.missing_configs:
            lines.append("## 3. Build Configuration Status")
            lines.append("")
            lines.append("The following standard QNX 8.0 build files are missing from the project:")
            lines.append("")
            for mc in report.project_structure.missing_configs:
                lines.append(f"- [ ] **{mc}**")
            lines.append("")
            lines.append("> Use `qnx-sentinel build-assist` to automatically generate verified `qnx.toolchain.cmake` and `CMakePresets.json` templates.")
            lines.append("")

        # Unresolved Include Paths
        if report.project_structure.unresolved_includes:
            lines.append("### Unresolved Include Paths & Missing Local Headers")
            lines.append("")
            for inc in report.project_structure.unresolved_includes:
                lines.append(f"- ⚠️ `{inc}`")
            lines.append("")

        # Detailed Findings Table
        lines.append("## 4. Portability & Compatibility Findings")
        lines.append("")
        if not report.findings:
            lines.append("No compatibility issues detected! The codebase conforms cleanly to QNX SDP 8.0 standards.")
            lines.append("")
        else:
            lines.append("| # | Severity | Rule ID | Title | Location |")
            lines.append("|---|---|---|---|---|")
            for idx, f in enumerate(report.findings, start=1):
                lines.append(f"| {idx} | **`{f.severity.value}`** | `{f.rule_id}` | {f.title} | `{f.file_path}:{f.line_number}` |")
            lines.append("")

            lines.append("### Detailed Issue Analysis & Remediation")
            lines.append("")
            for idx, f in enumerate(report.findings, start=1):
                lines.append(f"#### Finding #{idx}: [{f.severity.value}] {f.title} (`{f.rule_id}`)")
                lines.append("")
                lines.append(f"- **File:** `{f.file_path}` (Line {f.line_number})")
                lines.append(f"- **Category:** `{f.category.value}`")
                lines.append(f"- **Description:** {f.description}")
                lines.append(f"- **Rationale:** {f.rationale}")
                if f.code_snippet:
                    lines.append(f"- **Offending Code:**")
                    lines.append(f"  ```c\n  {f.code_snippet}\n  ```")
                lines.append(f"- **Remediation:** {f.remediation}")
                if f.remediation_code:
                    lines.append(f"- **Recommended QNX 8.0 Implementation:**")
                    lines.append(f"  ```c\n{f.remediation_code}\n  ```")
                if f.documentation_url:
                    lines.append(f"- **Official Documentation:** [{f.documentation_url}]({f.documentation_url})")
                lines.append("")

        # Recommendations
        lines.append("## 5. Architectural Recommendations")
        lines.append("")
        for idx, rec in enumerate(report.recommendations, start=1):
            lines.append(f"{idx}. {rec}")
        lines.append("")

        lines.append("---")
        lines.append("*Generated by QNX Sentinel — Intelligent QNX Build, Test & Compatibility Analyzer*")
        return "\n".join(lines)

    @staticmethod
    def save(report: AnalysisReport, output_path: str | Path) -> Path:
        out = Path(output_path).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(MarkdownReporter.render(report), encoding="utf-8")
        return out
