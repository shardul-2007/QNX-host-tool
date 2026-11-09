"""
QNX Sentinel - Compatibility Engine
Coordinates static code inspection across source and build files using modular rules.
Generates ordered findings and high-level architectural recommendations.
"""

from pathlib import Path
from typing import List, Optional

from qnx_sentinel.core.models import Finding, Severity, FindingCategory
from qnx_sentinel.analyzer.rules import DEFAULT_RULES, BaseRule


class CompatibilityEngine:
    """Orchestrates static analysis across all project files."""

    def __init__(self, rules: Optional[List[BaseRule]] = None) -> None:
        self.rules = rules if rules is not None else list(DEFAULT_RULES)

    def scan_files(self, file_paths: List[str], base_dir: Path) -> List[Finding]:
        """Scans a list of relative or absolute file paths against all active rules."""
        all_findings: List[Finding] = []

        for rel_path in file_paths:
            full_path = base_dir / rel_path
            if not full_path.is_file():
                continue

            try:
                content = full_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            for rule in self.rules:
                findings = rule.analyze_file(content, rel_path)
                all_findings.extend(findings)

        # Sort findings: CRITICAL -> WARNING -> BEST_PRACTICE -> INFO, then by file and line
        severity_rank = {
            Severity.CRITICAL: 0,
            Severity.WARNING: 1,
            Severity.BEST_PRACTICE: 2,
            Severity.INFO: 3,
        }

        all_findings.sort(
            key=lambda f: (severity_rank.get(f.severity, 99), f.file_path, f.line_number)
        )
        return all_findings

    def generate_recommendations(self, findings: List[Finding]) -> List[str]:
        """Synthesizes high-level actionable steps from the set of detected findings."""
        recommendations: List[str] = []
        categories = {f.category for f in findings}
        rule_ids = {f.rule_id for f in findings}

        if "QNX-001-EPOLL" in rule_ids:
            recommendations.append(
                "Refactor epoll loops to standard POSIX poll() or leverage QNX ionotify() with pulses for event notification."
            )
        if "QNX-002-TIMERFD" in rule_ids:
            recommendations.append(
                "Convert Linux timerfd usage to POSIX timer_create() coupled with QNX SIGEV_PULSE delivered to a Neutrino channel."
            )
        if "QNX-003-EVENTFD" in rule_ids:
            recommendations.append(
                "Replace eventfd inter-thread signaling with POSIX pipes or lightweight non-blocking QNX Pulses."
            )
        if "QNX-010-PTHREAD-YIELD" in rule_ids:
            recommendations.append(
                "Replace non-standard pthread_yield() calls with standard POSIX sched_yield() from <sched.h>."
            )
        if "QNX-020-PROC-SELF-EXE" in rule_ids:
            recommendations.append(
                "Replace /proc/self/exe resolution with the QNX _cmdname global pointer or argv[0] path resolution."
            )
        if "QNX-030-PRCTL" in rule_ids:
            recommendations.append(
                "Replace Linux prctl() calls with standard pthread_setname_np() for thread names and QNX ThreadCtl() for process controls."
            )
        if "QNX-050-LANG-CPP" in rule_ids:
            recommendations.append(
                "Remove deprecated '-lang-c++' flags from build files; configure CMAKE_CXX_COMPILER to point to 'q++'."
            )
        if "QNX-051-HOST-LIBRARIES" in rule_ids:
            recommendations.append(
                "Remove explicit '-lpthread', '-ldl', and '-lrt' from linker flags; these are integrated into QNX libc.so."
            )

        if not recommendations and findings:
            recommendations.append(
                "Address identified portability issues and re-run analysis to verify QNX 8.0 readiness."
            )
        elif not findings:
            recommendations.append(
                "Project conforms cleanly to verified QNX 8.0 POSIX and microkernel standards! Proceed to cross-compilation."
            )

        return recommendations
