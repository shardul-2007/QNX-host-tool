"""
QNX Sentinel - Process & Threading Portability Rules
Detects Linux prctl usage, multi-threaded fork risks, and thread priority mapping issues.
"""

import re
from typing import List
from qnx_sentinel.analyzer.rules.base_rule import BaseRule
from qnx_sentinel.core.models import Finding, FindingCategory, Severity
from qnx_sentinel.core.config import DOC_LINKS


class PrctlRule(BaseRule):
    rule_id = "QNX-030-PRCTL"
    category = FindingCategory.THREADING_SCHEDULING
    severity = Severity.CRITICAL
    title = "Linux prctl() Interface Usage"
    description = (
        "<sys/prctl.h> and prctl() are Linux-specific process and thread control operations. "
        "They do not exist in the QNX SDP 8.0 standard C library."
    )
    documentation_url = DOC_LINKS["thread_scheduling"]
    rationale = (
        "Thread naming on QNX is performed via pthread_setname_np(). "
        "Process attributes and security capabilities are configured via ThreadCtl() or procmgr_* APIs."
    )

    PATTERNS = [
        re.compile(r"\bprctl\s*\("),
        re.compile(r"#\s*include\s*<sys/prctl\.h>"),
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
                            remediation="For thread naming, use pthread_setname_np(pthread_self(), \"name\"). For process control, use QNX ThreadCtl().",
                            remediation_code="// Portable thread naming for QNX SDP 8.0:\n#include <pthread.h>\npthread_setname_np(pthread_self(), \"WorkerThread\");",
                            custom_desc=f"Detected Linux '{m.group(0)}'.",
                        )
                    )
                    break
        return findings


class MultithreadedForkRule(BaseRule):
    rule_id = "QNX-031-FORK-MULTITHREADED"
    category = FindingCategory.THREADING_SCHEDULING
    severity = Severity.WARNING
    title = "Potentially Unsafe fork() in Multi-Threaded RTOS Environment"
    description = (
        "Using fork() in a multi-threaded QNX process replicates only the calling thread, "
        "leaving mutexes, channels, and connections in potentially deadlocked or inconsistent states."
    )
    documentation_url = DOC_LINKS["porting_guide"]
    rationale = (
        "QNX Neutrino microkernel strongly advises using posix_spawn() or QNX native spawn*() "
        "family (spawnl, spawnp) instead of fork() + exec()."
    )

    PATTERN = re.compile(r"\bfork\s*\(\s*\)")

    def analyze_file(self, content: str, file_path: str) -> List[Finding]:
        findings: List[Finding] = []
        # Check if project includes pthread headers
        has_pthreads = "#include <pthread.h>" in content or "pthread_create" in content

        for idx, line in enumerate(content.splitlines(), start=1):
            if self.PATTERN.search(line):
                findings.append(
                    self.create_finding(
                        file_path=file_path,
                        line_number=idx,
                        code_snippet=line,
                        remediation="Replace fork() + exec() with posix_spawn() or QNX native spawnp().",
                        remediation_code="// Portable spawn on QNX 8.0:\n#include <spawn.h>\npid_t pid;\nchar *argv[] = {\"/bin/logger\", NULL};\nposix_spawn(&pid, argv[0], NULL, NULL, argv, environ);",
                        custom_desc="Detected fork() call. In multi-threaded QNX services, prefer posix_spawn() or spawnp().",
                    )
                )
        return findings


class LinuxNicePriorityRule(BaseRule):
    rule_id = "QNX-032-NICE-PRIORITY"
    category = FindingCategory.THREADING_SCHEDULING
    severity = Severity.INFO
    title = "Linux nice() / setpriority() Usage"
    description = (
        "nice() and setpriority() use Linux 'niceness' (-20 to 19). "
        "QNX Neutrino operates on real-time priorities (1 to 255)."
    )
    documentation_url = DOC_LINKS["thread_scheduling"]
    rationale = (
        "Default thread priority in QNX is 10. Normal non-critical threads run at 10-15. "
        "Time-critical RTOS threads run at 20-63. System drivers run up to 255. "
        "Use pthread_setschedparam() for deterministic scheduling."
    )

    PATTERN = re.compile(r"\b(setpriority|nice)\s*\(")

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
                        remediation="Use pthread_setschedparam() with SCHED_FIFO or SCHED_RR to set deterministic QNX priorities (1-255).",
                        remediation_code="#include <pthread.h>\n#include <sched.h>\nstruct sched_param param;\nparam.sched_priority = 21; // RT priority\npthread_setschedparam(pthread_self(), SCHED_RR, &param);",
                        custom_desc=f"Detected '{m.group(0)}'. QNX uses 1-255 real-time priority levels.",
                    )
                )
        return findings
