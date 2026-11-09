"""
QNX Sentinel - Diagnostic Error Explainer
Parses compiler and linker outputs, identifies QNX SDP 8.0 root causes,
and produces actionable explanations with official documentation references.
"""

import re
from pathlib import Path
from typing import List, Optional

from qnx_sentinel.core.models import DiagnosticExplanation
from qnx_sentinel.diagnostics.kb import KNOWLEDGE_BASE


class ErrorExplainer:
    """Intelligently analyzes build errors and linker failures for QNX 8.0."""

    def __init__(self) -> None:
        self.kb = KNOWLEDGE_BASE

    def explain_log(self, log_text: str) -> List[DiagnosticExplanation]:
        """Scans build log text and matches against verified QNX diagnostic patterns."""
        explanations: List[DiagnosticExplanation] = []
        matched_kb_ids = set()

        for entry in self.kb:
            pat = re.compile(entry["pattern"], re.IGNORECASE)
            match = pat.search(log_text)
            if match and entry["id"] not in matched_kb_ids:
                matched_kb_ids.add(entry["id"])
                explanations.append(
                    DiagnosticExplanation(
                        error_signature=match.group(0),
                        category=entry["category"],
                        matched_pattern=entry["pattern"],
                        explanation=entry["explanation"],
                        remediation_steps=entry["remediation_steps"],
                        suggested_diff=entry.get("suggested_diff"),
                        official_doc_link=entry["doc_link"],
                    )
                )

        # Fallback for unrecognized errors
        if not explanations and ("error:" in log_text.lower() or "fatal:" in log_text.lower()):
            for line in log_text.splitlines():
                if "error:" in line.lower() or "fatal:" in line.lower():
                    explanations.append(
                        DiagnosticExplanation(
                            error_signature=line.strip(),
                            category="GENERAL_COMPILER_ERROR",
                            matched_pattern="error:",
                            explanation=(
                                "A compiler or linker error was detected during the QNX build. "
                                "Check standard C/C++ syntax and ensure all target headers are present in QNX_TARGET/usr/include."
                            ),
                            remediation_steps=[
                                "Inspect source code at the indicated line number.",
                                "Verify that QNX SDP 8.0 environment variables are sourced (QNX_HOST, QNX_TARGET).",
                                "Verify that required headers exist in the QNX target sysroot.",
                            ],
                            official_doc_link="https://www.qnx.com/developers/docs/8.0/",
                        )
                    )
                    break

        return explanations

    def explain_file(self, log_path: str | Path) -> List[DiagnosticExplanation]:
        """Reads a build log file and explains its contents."""
        path = Path(log_path).resolve()
        if not path.is_file():
            return []
        content = path.read_text(encoding="utf-8", errors="ignore")
        return self.explain_log(content)
