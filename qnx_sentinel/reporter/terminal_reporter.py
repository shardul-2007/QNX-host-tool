"""
QNX Sentinel - Rich Terminal Reporter
Renders formatted summaries, score badges, tables, and code snippets in the console.
"""

import sys
from typing import List, Optional

from qnx_sentinel.core.models import AnalysisReport, Finding, Severity

# Initialize colorama if present on Windows
try:
    import colorama
    colorama.init()
    HAS_COLOR = True
except Exception:
    HAS_COLOR = sys.platform != "win32"

class Colors:
    RESET = "\033[0m" if HAS_COLOR else ""
    BOLD = "\033[1m" if HAS_COLOR else ""
    DIM = "\033[2m" if HAS_COLOR else ""
    RED = "\033[91m" if HAS_COLOR else ""
    GREEN = "\033[92m" if HAS_COLOR else ""
    YELLOW = "\033[93m" if HAS_COLOR else ""
    BLUE = "\033[94m" if HAS_COLOR else ""
    MAGENTA = "\033[95m" if HAS_COLOR else ""
    CYAN = "\033[96m" if HAS_COLOR else ""
    WHITE = "\033[97m" if HAS_COLOR else ""


class TerminalReporter:
    """Renders comprehensive terminal reports for QNX Sentinel."""

    @staticmethod
    def render_report(report: AnalysisReport) -> str:
        """Constructs a formatted multi-section terminal output string."""
        lines: List[str] = []

        # Banner
        lines.append(f"{Colors.BOLD}{Colors.CYAN}" + "=" * 80 + f"{Colors.RESET}")
        lines.append(f"{Colors.BOLD}{Colors.CYAN}       QNX SENTINEL — Intelligent QNX 8.0 Compatibility Analyzer{Colors.RESET}")
        lines.append(f"{Colors.BOLD}{Colors.CYAN}" + "=" * 80 + f"{Colors.RESET}")

        # Overview
        grade_color = Colors.GREEN if report.grade in ("A", "B") else (Colors.YELLOW if report.grade == "C" else Colors.RED)
        lines.append(f"  {Colors.BOLD}Target Project:{Colors.RESET}   {report.project_name} ({report.project_path})")
        lines.append(f"  {Colors.BOLD}Analysis Time:{Colors.RESET}    {report.timestamp}")
        lines.append(f"  {Colors.BOLD}Readiness Score:{Colors.RESET}  {grade_color}{report.score}/100 [Grade {report.grade}]{Colors.RESET}")
        lines.append(f"  {Colors.BOLD}Build Systems:{Colors.RESET}    {', '.join(report.project_structure.build_systems) or 'None'}")
        lines.append(f"  {Colors.BOLD}Total Files:{Colors.RESET}      {report.project_structure.metrics.total_files} ({report.project_structure.metrics.c_files} C, {report.project_structure.metrics.cpp_files} C++, {report.project_structure.metrics.header_files} Headers, {report.project_structure.metrics.lines_of_code} LOC)")
        lines.append("")

        # SDK Status
        sdk = report.sdk_status
        lines.append(f"{Colors.BOLD}--- [1] HOST QNX SDP 8.0 ENVIRONMENT STATUS ---{Colors.RESET}")
        if sdk.is_qnx_sdp_detected:
            lines.append(f"  {Colors.GREEN}[+] QNX SDP Detected:{Colors.RESET} Version {sdk.sdp_version or '8.0'}")
            lines.append(f"      QNX_HOST:   {sdk.qnx_host}")
            lines.append(f"      QNX_TARGET: {sdk.qnx_target}")
            lines.append(f"      Compiler:   {sdk.qcc_path or 'Not in PATH'}")
        else:
            lines.append(f"  {Colors.YELLOW}[!] QNX SDP 8.0 Not Active in Current Environment{Colors.RESET}")
            if sdk.env_script_suggested:
                lines.append(f"      Action Required: Run '{sdk.env_script_suggested}'")
            lines.append("      (Running in Host-Static Analysis & Simulation Mode)")

        if sdk.qemu_available:
            lines.append(f"  {Colors.GREEN}[+] QEMU Available:{Colors.RESET} {sdk.qemu_binary}")
        else:
            lines.append("  [-] QEMU Not Detected in host PATH")

        if sdk.mkqnximage_available:
            lines.append(f"  {Colors.GREEN}[+] mkqnximage Available:{Colors.RESET} {sdk.mkqnximage_path}")
        lines.append("")

        # Findings Summary
        lines.append(f"{Colors.BOLD}--- [2] COMPATIBILITY FINDINGS SUMMARY ---{Colors.RESET}")
        summary = report.summary
        lines.append(
            f"  {Colors.RED}CRITICAL: {summary.get('CRITICAL', 0)}{Colors.RESET}  |  "
            f"{Colors.YELLOW}WARNING: {summary.get('WARNING', 0)}{Colors.RESET}  |  "
            f"{Colors.CYAN}BEST_PRACTICE: {summary.get('BEST_PRACTICE', 0)}{Colors.RESET}  |  "
            f"{Colors.WHITE}INFO: {summary.get('INFO', 0)}{Colors.RESET}  |  "
            f"TOTAL: {summary.get('TOTAL', 0)}"
        )
        lines.append("")

        # Missing Configurations
        if report.project_structure.missing_configs:
            lines.append(f"{Colors.BOLD}{Colors.YELLOW}--- [3] MISSING QNX CONFIGURATIONS ---{Colors.RESET}")
            for mc in report.project_structure.missing_configs:
                lines.append(f"  {Colors.YELLOW}[!] {mc}{Colors.RESET}")
            lines.append(f"  {Colors.DIM}(Use 'qnx-sentinel build-assist' to generate verified templates){Colors.RESET}")
            lines.append("")

        # Detailed Findings List
        if report.findings:
            lines.append(f"{Colors.BOLD}--- [4] DETAILED PORTABILITY FINDINGS ---{Colors.RESET}")
            for idx, f in enumerate(report.findings, start=1):
                sev_color = (
                    Colors.RED if f.severity == Severity.CRITICAL
                    else (Colors.YELLOW if f.severity == Severity.WARNING
                          else (Colors.CYAN if f.severity == Severity.BEST_PRACTICE else Colors.WHITE))
                )
                badge = f"{sev_color}[{f.severity.value}]{Colors.RESET}"
                lines.append(f"#{idx} {badge} {Colors.BOLD}{f.title}{Colors.RESET} ({f.rule_id})")
                lines.append(f"    Location:    {f.file_path}:{f.line_number}")
                lines.append(f"    Description: {f.description}")
                if f.code_snippet:
                    lines.append(f"    Code:        {Colors.DIM}{f.code_snippet}{Colors.RESET}")
                lines.append(f"    Remediation: {Colors.GREEN}{f.remediation}{Colors.RESET}")
                if f.remediation_code:
                    code_block = "\n        ".join(f.remediation_code.splitlines())
                    lines.append(f"    Fix Example:\n        {Colors.CYAN}{code_block}{Colors.RESET}")
                if f.documentation_url:
                    lines.append(f"    Reference:   {Colors.BLUE}{f.documentation_url}{Colors.RESET}")
                lines.append("")
        else:
            lines.append(f"{Colors.GREEN}[+] No compatibility violations found! Project is clean for QNX 8.0.{Colors.RESET}\n")

        # High-level Recommendations
        lines.append(f"{Colors.BOLD}--- [5] ARCHITECTURAL RECOMMENDATIONS ---{Colors.RESET}")
        for r_idx, rec in enumerate(report.recommendations, start=1):
            lines.append(f"  {r_idx}. {rec}")
        lines.append("")

        lines.append(f"{Colors.BOLD}{Colors.CYAN}" + "=" * 80 + f"{Colors.RESET}")
        return "\n".join(lines)
