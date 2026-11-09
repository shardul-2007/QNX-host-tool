"""
QNX Sentinel - QNX Microkernel Idioms & Best Practices
Encourages production-grade QNX patterns: slog2 logging, proper Neutrino
channel management, and real-time pulse handling.
"""

import re
from typing import List
from qnx_sentinel.analyzer.rules.base_rule import BaseRule
from qnx_sentinel.core.models import Finding, FindingCategory, Severity
from qnx_sentinel.core.config import DOC_LINKS


class Slog2AdoptionRule(BaseRule):
    rule_id = "QNX-060-SLOG2-ADOPTION"
    category = FindingCategory.QNX_MICROKERNEL_IDIOM
    severity = Severity.BEST_PRACTICE
    title = "Consider QNX System Logger (slog2) for Embedded Daemons"
    description = (
        "Daemon and service code using printf() or fprintf(stderr, ...) to output logs "
        "may experience high latency or lost messages in headless or safety-critical deployments."
    )
    documentation_url = DOC_LINKS["slog2_logging"]
    rationale = (
        "QNX slog2 provides zero-copy, lock-free ring buffers with severity levels "
        "(SLOG2_DEBUG1, SLOG2_INFO, SLOG2_WARNING, SLOG2_ERROR) captured by slog2info."
    )

    PATTERNS = [
        re.compile(r"\bprintf\s*\(\s*\"\[(ERROR|WARN|INFO|DEBUG)\]"),
        re.compile(r"\bfprintf\s*\(\s*stderr\s*,"),
    ]

    def analyze_file(self, content: str, file_path: str) -> List[Finding]:
        findings: List[Finding] = []
        # Only suggest if file looks like a service/daemon (has main or server loop)
        if "main(" not in content and "run(" not in content:
            return findings

        # If already using slog2, don't flag
        if "slog2" in content or "sys/slog2.h" in content:
            return findings

        for idx, line in enumerate(content.splitlines(), start=1):
            for pat in self.PATTERNS:
                if pat.search(line):
                    findings.append(
                        self.create_finding(
                            file_path=file_path,
                            line_number=idx,
                            code_snippet=line,
                            remediation="Integrate QNX slog2 for deterministic, zero-allocation logging into system buffers.",
                            remediation_code=(
                                "#include <sys/slog2.h>\n"
                                "slog2_buffer_set_config_t config;\n"
                                "slog2_buffer_t buffer_handle;\n"
                                "// slog2_register(&config, &buffer_handle, 0);\n"
                                "slog2c(buffer_handle, 0, SLOG2_ERROR, \"Fatal failure\");"
                            ),
                            custom_desc="Standard printf/fprintf used for daemon logging instead of QNX slog2.",
                        )
                    )
                    break
        return findings
