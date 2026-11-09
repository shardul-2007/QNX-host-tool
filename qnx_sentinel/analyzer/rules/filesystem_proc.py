"""
QNX Sentinel - Filesystem & procfs Portability Rules
Detects assumptions about Linux procfs (/proc/self/exe), sysfs (/sys),
and shared memory locations (/dev/shm vs /dev/shmem).
"""

import re
from typing import List
from qnx_sentinel.analyzer.rules.base_rule import BaseRule
from qnx_sentinel.core.models import Finding, FindingCategory, Severity
from qnx_sentinel.core.config import DOC_LINKS


class ProcSelfExeRule(BaseRule):
    rule_id = "QNX-020-PROC-SELF-EXE"
    category = FindingCategory.FILESYSTEM_PROCFS
    severity = Severity.WARNING
    title = "Linux /proc/self/exe Symlink Dependency"
    description = (
        "Linux exposes the running binary path via the '/proc/self/exe' symlink. "
        "QNX procfs does not provide this symlink."
    )
    documentation_url = DOC_LINKS["porting_guide"]
    rationale = (
        "On QNX, procnto provides process memory mappings via '/proc/<pid>/as'. "
        "The executable path is commonly obtained through argv[0], the global '_cmdname' variable, "
        "or by querying dtv_entry structures."
    )

    PATTERN = re.compile(r"\"/proc/self/exe\"|'/proc/self/exe'")

    def analyze_file(self, content: str, file_path: str) -> List[Finding]:
        findings: List[Finding] = []
        for idx, line in enumerate(content.splitlines(), start=1):
            if self.PATTERN.search(line):
                findings.append(
                    self.create_finding(
                        file_path=file_path,
                        line_number=idx,
                        code_snippet=line,
                        remediation="Use QNX global '_cmdname' or pass argv[0] to realpath() instead of reading /proc/self/exe.",
                        remediation_code="// In QNX, _cmdname points to the program invocation binary name:\nextern char *_cmdname;\nprintf(\"Running binary: %s\\n\", _cmdname);",
                    )
                )
        return findings


class DevShmPathRule(BaseRule):
    rule_id = "QNX-021-DEV-SHM"
    category = FindingCategory.FILESYSTEM_PROCFS
    severity = Severity.WARNING
    title = "Hardcoded Linux /dev/shm Shared Memory Path"
    description = (
        "Linux places POSIX shared memory files under '/dev/shm'. "
        "On QNX Neutrino, POSIX shared memory objects reside under '/dev/shmem'."
    )
    documentation_url = DOC_LINKS["microkernel_ipc"]
    rationale = (
        "Directly opening '/dev/shm/...' will fail with ENOENT on QNX. "
        "Always use POSIX shm_open(\"/my_shm\", O_RDWR | O_CREAT, 0666) which automatically resolves to /dev/shmem."
    )

    PATTERN = re.compile(r"\"/dev/shm[/\"]|'/dev/shm[/'/]")

    def analyze_file(self, content: str, file_path: str) -> List[Finding]:
        findings: List[Finding] = []
        for idx, line in enumerate(content.splitlines(), start=1):
            if self.PATTERN.search(line):
                findings.append(
                    self.create_finding(
                        file_path=file_path,
                        line_number=idx,
                        code_snippet=line,
                        remediation="Use standard POSIX shm_open() without hardcoding the filesystem path, or reference '/dev/shmem' on QNX.",
                        remediation_code="// Portable POSIX shared memory:\n#include <sys/mman.h>\nint fd = shm_open(\"/telemetry_buf\", O_CREAT | O_RDWR, 0660);",
                    )
                )
        return findings


class LinuxSysfsRule(BaseRule):
    rule_id = "QNX-022-SYSFS"
    category = FindingCategory.FILESYSTEM_PROCFS
    severity = Severity.CRITICAL
    title = "Linux sysfs (/sys/...) Path Dependency"
    description = (
        "Linux sysfs (/sys/class, /sys/devices) does not exist on QNX Neutrino RTOS."
    )
    documentation_url = DOC_LINKS["porting_guide"]
    rationale = (
        "Hardware devices on QNX are managed by user-space Resource Managers under /dev/ (e.g. /dev/io-net, /dev/spi, /dev/i2c, /dev/ser1)."
    )

    PATTERN = re.compile(r"\"/sys/(class|devices|bus|module|kernel)[/\"]")

    def analyze_file(self, content: str, file_path: str) -> List[Finding]:
        findings: List[Finding] = []
        for idx, line in enumerate(content.splitlines(), start=1):
            m = self.PATTERN.search(line)
            if m:
                findings.append(
                    self.create_finding(
                        file_path=file_path,
                        line_number=idx,
                        code_snippet=line,
                        remediation="Access device drivers through their QNX resource manager nodes under /dev/ using standard open()/devctl() calls.",
                        remediation_code="// Example QNX device control via devctl():\n#include <devctl.h>\nint fd = open(\"/dev/spi0\", O_RDWR);\n// devctl(fd, DCMD_..., &data, sizeof(data), NULL);",
                        custom_desc=f"Detected Linux sysfs path '{m.group(0)}'.",
                    )
                )
        return findings
