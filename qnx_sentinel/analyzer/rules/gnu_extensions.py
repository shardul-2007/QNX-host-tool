"""
QNX Sentinel - GNU Extension & Portability Rules
Detects non-standard GNU C/C++ extensions that trigger compilation errors
or undefined behavior when moving from glibc/Linux to QNX SDP 8.0 libc.
"""

import re
from typing import List
from qnx_sentinel.analyzer.rules.base_rule import BaseRule
from qnx_sentinel.core.models import Finding, FindingCategory, Severity
from qnx_sentinel.core.config import DOC_LINKS


class PthreadYieldRule(BaseRule):
    rule_id = "QNX-010-PTHREAD-YIELD"
    category = FindingCategory.GNU_EXTENSION
    severity = Severity.WARNING
    title = "Non-Standard GNU pthread_yield() Call"
    description = (
        "pthread_yield() is a deprecated GNU extension not defined in standard POSIX or QNX libc. "
        "Will cause 'implicit declaration of function' or linker error."
    )
    documentation_url = DOC_LINKS["porting_guide"]
    rationale = "POSIX specifies sched_yield() defined in <sched.h>."

    PATTERN = re.compile(r"\bpthread_yield\s*\(\s*\)")

    def analyze_file(self, content: str, file_path: str) -> List[Finding]:
        findings: List[Finding] = []
        for idx, line in enumerate(content.splitlines(), start=1):
            if self.PATTERN.search(line):
                findings.append(
                    self.create_finding(
                        file_path=file_path,
                        line_number=idx,
                        code_snippet=line,
                        remediation="Replace 'pthread_yield()' with standard POSIX 'sched_yield()' and include <sched.h>.",
                        remediation_code="#include <sched.h>\nsched_yield();",
                    )
                )
        return findings


class GetCurrentDirNameRule(BaseRule):
    rule_id = "QNX-011-GET-CURRENT-DIR-NAME"
    category = FindingCategory.GNU_EXTENSION
    severity = Severity.WARNING
    title = "Non-Standard GNU get_current_dir_name() Call"
    description = (
        "get_current_dir_name() is a GNU libc extension not present in QNX SDP 8.0."
    )
    documentation_url = DOC_LINKS["porting_guide"]
    rationale = "Standard POSIX getcwd(buf, size) is fully supported across all POSIX compliant operating systems."

    PATTERN = re.compile(r"\bget_current_dir_name\s*\(\s*\)")

    def analyze_file(self, content: str, file_path: str) -> List[Finding]:
        findings: List[Finding] = []
        for idx, line in enumerate(content.splitlines(), start=1):
            if self.PATTERN.search(line):
                findings.append(
                    self.create_finding(
                        file_path=file_path,
                        line_number=idx,
                        code_snippet=line,
                        remediation="Replace 'get_current_dir_name()' with POSIX 'getcwd(buf, sizeof(buf))'.",
                        remediation_code="#include <unistd.h>\n#include <limits.h>\nchar cwd[PATH_MAX];\nif (getcwd(cwd, sizeof(cwd)) != NULL) { /* use cwd */ }",
                    )
                )
        return findings


class StrndupaRule(BaseRule):
    rule_id = "QNX-012-STRNDUPA"
    category = FindingCategory.GNU_EXTENSION
    severity = Severity.WARNING
    title = "Unsafe GNU strndupa() / strdupa() Macro"
    description = (
        "strndupa() and strdupa() are GNU extensions that use alloca() stack allocations. "
        "They are non-standard and risk stack exhaustion in embedded/RTOS thread environments."
    )
    documentation_url = DOC_LINKS["porting_guide"]
    rationale = (
        "QNX real-time threads typically operate with bounded stack sizes (e.g. 32KB to 256KB). "
        "Unbounded alloca() risks silent stack overflow."
    )

    PATTERN = re.compile(r"\b(strndupa|strdupa)\b")

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
                        remediation="Replace with POSIX strndup() and explicit free(), or use a bounded fixed-size stack buffer.",
                        remediation_code="char *safe_str = strndup(src, max_len);\n// ... use safe_str ...\nfree(safe_str);",
                        custom_desc=f"Detected GNU extension '{m.group(0)}'.",
                    )
                )
        return findings


class LinuxCpuAffinityRule(BaseRule):
    rule_id = "QNX-013-CPU-AFFINITY"
    category = FindingCategory.GNU_EXTENSION
    severity = Severity.WARNING
    title = "Linux CPU Affinity (cpu_set_t / pthread_setaffinity_np)"
    description = (
        "Linux uses cpu_set_t and pthread_setaffinity_np() for CPU core pinning. "
        "QNX Neutrino RTOS manages CPU core affinity using ThreadCtl() or ThreadCtlExt()."
    )
    documentation_url = DOC_LINKS["thread_scheduling"]
    rationale = (
        "QNX Neutrino supports multi-core SMP scaling with ThreadCtl(_NTO_TCTL_RUNMASK, ...) "
        "and multi-cluster runmasks with _NTO_TCTL_RUNMASK_EXT."
    )

    PATTERNS = [
        re.compile(r"\b(pthread_setaffinity_np|pthread_getaffinity_np)\b"),
        re.compile(r"\b(cpu_set_t|CPU_SET|CPU_ZERO)\b"),
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
                            remediation="Use QNX ThreadCtl(_NTO_TCTL_RUNMASK, (void*)(uintptr_t)mask) to pin threads to SMP cores.",
                            remediation_code="#include <sys/neutrino.h>\n// Pin calling thread to CPU core 0 and 1:\nuint32_t runmask = (1 << 0) | (1 << 1);\nThreadCtl(_NTO_TCTL_RUNMASK, (void*)(uintptr_t)runmask);",
                            custom_desc=f"Detected Linux CPU affinity interface '{m.group(0)}'.",
                        )
                    )
                    break
        return findings
