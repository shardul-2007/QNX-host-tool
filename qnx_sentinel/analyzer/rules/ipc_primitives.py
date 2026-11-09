"""
QNX Sentinel - IPC & Synchronization Rules
Detects legacy System V IPC, recommends POSIX or QNX Neutrino message passing.
"""

import re
from typing import List
from qnx_sentinel.analyzer.rules.base_rule import BaseRule
from qnx_sentinel.core.models import Finding, FindingCategory, Severity
from qnx_sentinel.core.config import DOC_LINKS


class SysVIPCRule(BaseRule):
    rule_id = "QNX-040-SYSV-IPC"
    category = FindingCategory.IPC_SYNCHRONIZATION
    severity = Severity.WARNING
    title = "Legacy System V IPC Usage (shmget / semget / msgget)"
    description = (
        "Legacy System V IPC primitives are sub-optimal on microkernels and may not be configured "
        "by default on minimal QNX embedded runtime targets."
    )
    documentation_url = DOC_LINKS["microkernel_ipc"]
    rationale = (
        "QNX Neutrino RTOS is optimized for synchronous message passing (MsgSend/MsgReceive), "
        "asynchronous Pulses, and POSIX memory objects (shm_open, sem_open)."
    )

    PATTERNS = [
        re.compile(r"\b(shmget|shmat|shmdt|shmctl)\b"),
        re.compile(r"\b(semget|semop|semctl)\b"),
        re.compile(r"\b(msgget|msgsnd|msgrcv|msgctl)\b"),
        re.compile(r"#\s*include\s*<sys/(ipc|shm|sem|msg)\.h>"),
    ]

    def analyze_file(self, content: str, file_path: str) -> List[Finding]:
        findings: List[Finding] = []
        for idx, line in enumerate(content.splitlines(), start=1):
            for pat in self.PATTERNS:
                m = pat.search(line)
                if m:
                    findings.append(
                        self.create_finding(
                            file_path=file_path,
                            line_number=idx,
                            code_snippet=line,
                            remediation="Migrate from System V IPC to POSIX IPC (shm_open, sem_open) or QNX native Channels.",
                            remediation_code="// POSIX shared memory:\n#include <sys/mman.h>\n#include <fcntl.h>\nint fd = shm_open(\"/my_shared_mem\", O_RDWR | O_CREAT, 0660);",
                            custom_desc=f"Detected System V IPC call '{m.group(0)}'.",
                        )
                    )
                    break
        return findings
