"""
QNX Sentinel - Core Data Models
Provides structured dataclasses and Enums for findings, project metrics,
target environments, diagnostic reports, and test results.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Optional, Any
import json
import datetime


class Severity(str, Enum):
    CRITICAL = "CRITICAL"          # Blocks compilation or causes runtime failure on QNX
    WARNING = "WARNING"            # Portability issue, non-standard POSIX, deprecated feature
    INFO = "INFO"                  # Informational notice or minor optimization opportunity
    BEST_PRACTICE = "BEST_PRACTICE"# Recommended QNX 8.0 architectural idiom (microkernel, IPC, slog2)


class FindingCategory(str, Enum):
    LINUX_SPECIFIC_SYSCALL = "LINUX_SPECIFIC_SYSCALL"
    GNU_EXTENSION = "GNU_EXTENSION"
    FILESYSTEM_PROCFS = "FILESYSTEM_PROCFS"
    THREADING_SCHEDULING = "THREADING_SCHEDULING"
    IPC_SYNCHRONIZATION = "IPC_SYNCHRONIZATION"
    COMPILER_TOOLCHAIN = "COMPILER_TOOLCHAIN"
    BUILD_CONFIGURATION = "BUILD_CONFIGURATION"
    QNX_MICROKERNEL_IDIOM = "QNX_MICROKERNEL_IDIOM"


@dataclass
class Finding:
    rule_id: str
    category: FindingCategory
    severity: Severity
    title: str
    description: str
    file_path: str
    line_number: int
    column_number: Optional[int] = None
    code_snippet: str = ""
    remediation: str = ""
    remediation_code: Optional[str] = None
    documentation_url: str = ""
    rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["category"] = self.category.value
        d["severity"] = self.severity.value
        return d


@dataclass
class ProjectMetrics:
    total_files: int = 0
    c_files: int = 0
    cpp_files: int = 0
    header_files: int = 0
    build_files: int = 0
    lines_of_code: int = 0


@dataclass
class ProjectStructure:
    root_path: str
    project_name: str
    build_systems: List[str] = field(default_factory=list)
    source_files: List[str] = field(default_factory=list)
    header_files: List[str] = field(default_factory=list)
    build_files: List[str] = field(default_factory=list)
    detected_configs: List[str] = field(default_factory=list)
    missing_configs: List[str] = field(default_factory=list)
    incompatible_dependencies: List[str] = field(default_factory=list)
    suspicious_platform_assumptions: List[str] = field(default_factory=list)
    metrics: ProjectMetrics = field(default_factory=ProjectMetrics)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SDKEnvironment:
    is_qnx_sdp_detected: bool = False
    sdp_version: Optional[str] = None
    qnx_host: Optional[str] = None
    qnx_target: Optional[str] = None
    qnx_configuration: Optional[str] = None
    qcc_path: Optional[str] = None
    qcc_version_raw: Optional[str] = None
    supported_targets: List[str] = field(default_factory=list)
    qemu_available: bool = False
    qemu_binary: Optional[str] = None
    mkqnximage_available: bool = False
    mkqnximage_path: Optional[str] = None
    env_script_suggested: Optional[str] = None
    diagnostic_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TargetEnvironment:
    target_type: str = "SIMULATED"  # "HARDWARE", "QEMU", "SIMULATED", "UNCONFIGURED"
    architecture: str = "aarch64le" # "aarch64le", "x86_64"
    hostname_or_ip: Optional[str] = None
    ssh_port: int = 22
    is_simulated: bool = True
    qemu_command: Optional[str] = None
    status: str = "UNKNOWN"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DiagnosticExplanation:
    error_signature: str
    category: str
    matched_pattern: str
    explanation: str
    remediation_steps: List[str] = field(default_factory=list)
    suggested_diff: Optional[str] = None
    official_doc_link: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TestResultItem:
    name: str
    status: str  # "PASSED", "FAILED", "SKIPPED", "ERROR"
    duration_ms: float = 0.0
    stdout: str = ""
    stderr: str = ""
    error_message: Optional[str] = None


@dataclass
class TestRunReport:
    suite_name: str
    execution_mode: str  # "ACTUAL_HARDWARE", "ACTUAL_QEMU", "SIMULATED_TARGET", "HOST_SANDBOX"
    is_simulated: bool
    target_arch: str
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    tests: List[TestResultItem] = field(default_factory=list)
    raw_output: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AnalysisReport:
    project_name: str
    project_path: str
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    sdk_status: SDKEnvironment = field(default_factory=SDKEnvironment)
    project_structure: ProjectStructure = field(default_factory=lambda: ProjectStructure("", ""))
    findings: List[Finding] = field(default_factory=list)
    score: float = 100.0
    grade: str = "A"
    summary: Dict[str, int] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

    def calculate_score(self) -> None:
        """
        Computes the QNX 8.0 Readiness Index (0 - 100).
        Deductions:
          - CRITICAL: -15 pts each
          - WARNING: -5 pts each
          - BEST_PRACTICE: -2 pts each
          - INFO: -1 pt each
          - Missing Toolchain / Config: -10 pts
        """
        deductions = 0.0
        counts: Dict[str, int] = {
            "CRITICAL": 0,
            "WARNING": 0,
            "INFO": 0,
            "BEST_PRACTICE": 0,
            "TOTAL": len(self.findings)
        }

        for f in self.findings:
            sev = f.severity.value
            counts[sev] = counts.get(sev, 0) + 1
            if sev == "CRITICAL":
                deductions += 15.0
            elif sev == "WARNING":
                deductions += 5.0
            elif sev == "BEST_PRACTICE":
                deductions += 2.0
            elif sev == "INFO":
                deductions += 1.0

        if self.project_structure.missing_configs:
            deductions += min(20.0, len(self.project_structure.missing_configs) * 5.0)

        raw_score = max(0.0, 100.0 - deductions)
        self.score = round(raw_score, 1)

        if self.score >= 90:
            self.grade = "A"
        elif self.score >= 80:
            self.grade = "B"
        elif self.score >= 70:
            self.grade = "C"
        elif self.score >= 60:
            self.grade = "D"
        else:
            self.grade = "F"

        self.summary = counts

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "project_path": self.project_path,
            "timestamp": self.timestamp,
            "score": self.score,
            "grade": self.grade,
            "summary": self.summary,
            "sdk_status": self.sdk_status.to_dict(),
            "project_structure": self.project_structure.to_dict(),
            "findings": [f.to_dict() for f in self.findings],
            "recommendations": self.recommendations
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
