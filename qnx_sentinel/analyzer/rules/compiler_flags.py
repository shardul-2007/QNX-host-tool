"""
QNX Sentinel - Compiler & Toolchain Flags Rules
Scans CMakeLists.txt and Makefiles for deprecated flags (-lang-c++),
redundant host libraries (-lpthread, -ldl, -lrt), and architecture hardcoding.
"""

import re
from typing import List
from qnx_sentinel.analyzer.rules.base_rule import BaseRule
from qnx_sentinel.core.models import Finding, FindingCategory, Severity
from qnx_sentinel.core.config import DOC_LINKS


class DeprecatedLangCppRule(BaseRule):
    rule_id = "QNX-050-LANG-CPP"
    category = FindingCategory.COMPILER_TOOLCHAIN
    severity = Severity.WARNING
    title = "Deprecated Compiler Flag '-lang-c++' in QNX 8.0"
    description = (
        "The '-lang-c++' flag was used in legacy QNX toolchains to force C++ compilation with qcc. "
        "In QNX SDP 8.0 with GCC 12.2 and modern Clang, this flag is deprecated and triggers warnings or errors."
    )
    documentation_url = DOC_LINKS["compiler_options"]
    rationale = "Modern CMake and QNX 8.0 use 'q++' directly or standard language flags (-x c++)."

    PATTERN = re.compile(r"-lang-c\+\+")

    def analyze_file(self, content: str, file_path: str) -> List[Finding]:
        findings: List[Finding] = []
        for idx, line in enumerate(content.splitlines(), start=1):
            if self.PATTERN.search(line):
                findings.append(
                    self.create_finding(
                        file_path=file_path,
                        line_number=idx,
                        code_snippet=line,
                        remediation="Remove '-lang-c++'. Set CMAKE_CXX_COMPILER to 'q++' in your QNX toolchain file.",
                        remediation_code="# In qnx.toolchain.cmake:\nset(CMAKE_CXX_COMPILER ${QNX_HOST}/usr/bin/q++)",
                    )
                )
        return findings


class RedundantHostLibrariesRule(BaseRule):
    rule_id = "QNX-051-HOST-LIBRARIES"
    category = FindingCategory.COMPILER_TOOLCHAIN
    severity = Severity.INFO
    title = "Redundant Host Library Linking (-lpthread, -ldl, -lrt)"
    description = (
        "On Linux, libpthread, libdl, and librt are separate libraries. "
        "On QNX Neutrino RTOS, all threading, dynamic loading, and realtime timing routines "
        "are integrated directly into the standard C library (libc.so)."
    )
    documentation_url = DOC_LINKS["compiler_qcc"]
    rationale = (
        "Explicitly specifying -lpthread or -ldl is unnecessary on QNX and can lead to linker warnings "
        "or missing library errors if stub libraries are absent."
    )

    PATTERNS = [
        (re.compile(r"(?:-lpthread\b|\btarget_link_libraries\s*\(.*?\bpthread\b)"), "pthread / -lpthread"),
        (re.compile(r"(?:-ldl\b|\btarget_link_libraries\s*\(.*?\bdl\b)"), "dl / -ldl"),
        (re.compile(r"(?:-lrt\b|\btarget_link_libraries\s*\(.*?\brt\b)"), "rt / -lrt"),
    ]

    def analyze_file(self, content: str, file_path: str) -> List[Finding]:
        findings: List[Finding] = []
        for idx, line in enumerate(content.splitlines(), start=1):
            for pat, name in self.PATTERNS:
                if pat.search(line):
                    findings.append(
                        self.create_finding(
                            file_path=file_path,
                            line_number=idx,
                            code_snippet=line,
                            remediation=f"Wrap '{name}' in platform checks or remove it when CMAKE_SYSTEM_NAME STREQUAL 'QNX'.",
                            remediation_code="if(NOT CMAKE_SYSTEM_NAME STREQUAL \"QNX\")\n  target_link_libraries(my_target PRIVATE pthread dl)\nendif()",
                            custom_desc=f"Found explicit '{name}'. Threads and dlopen are built into QNX libc.so.",
                        )
                    )
        return findings
