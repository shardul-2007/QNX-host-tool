"""
QNX Sentinel - Base Compatibility Rule
Defines the abstract interface for all static analysis rules.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from qnx_sentinel.core.models import Finding, FindingCategory, Severity


class BaseRule(ABC):
    """Abstract base class for all QNX 8.0 compatibility rules."""

    rule_id: str
    category: FindingCategory
    severity: Severity
    title: str
    description: str
    documentation_url: str
    rationale: str

    @abstractmethod
    def analyze_file(self, content: str, file_path: str) -> List[Finding]:
        """
        Inspects file content and returns a list of Findings.
        Implementations should record accurate 1-based line numbers and code snippets.
        """
        pass

    def create_finding(
        self,
        file_path: str,
        line_number: int,
        code_snippet: str,
        remediation: str,
        remediation_code: Optional[str] = None,
        custom_desc: Optional[str] = None,
    ) -> Finding:
        """Helper to instantiate a Finding from rule metadata."""
        return Finding(
            rule_id=self.rule_id,
            category=self.category,
            severity=self.severity,
            title=self.title,
            description=custom_desc or self.description,
            file_path=file_path,
            line_number=line_number,
            code_snippet=code_snippet.strip(),
            remediation=remediation,
            remediation_code=remediation_code,
            documentation_url=self.documentation_url,
            rationale=self.rationale,
        )
