"""
QNX Sentinel - Linux-Specific Syscall Portability Rules
Detects Linux epoll, timerfd, eventfd, signalfd, and inotify APIs,
providing verified QNX 8.0 equivalents (ionotify, POSIX timers + pulses, pipes).
"""

import re
from typing import List
from qnx_sentinel.analyzer.rules.base_rule import BaseRule
from qnx_sentinel.core.models import Finding, FindingCategory, Severity
from qnx_sentinel.core.config import DOC_LINKS


class EpollUsageRule(BaseRule):
    rule_id = "QNX-001-EPOLL"
    category = FindingCategory.LINUX_SPECIFIC_SYSCALL
    severity = Severity.CRITICAL
    title = "Non-Portable Linux epoll API Usage"
    description = (
        "Linux epoll APIs (epoll_create, epoll_ctl, epoll_wait) are not supported on QNX Neutrino RTOS. "
        "Code using epoll will fail at link or compile time on QNX SDP 8.0."
    )
    documentation_url = DOC_LINKS["porting_guide"]
    rationale = (
        "QNX Neutrino is a microkernel operating system that multiplexes events using "
        "ionotify(), standard POSIX poll()/select(), or native Neutrino Pulses/Channels."
    )

    PATTERNS = [
        re.compile(r"\b(epoll_create|epoll_create1)\b"),
        re.compile(r"\bepoll_ctl\b"),
        re.compile(r"\bepoll_wait\b"),
        re.compile(r"#\s*include\s*<sys/epoll\.h>"),
    ]

    def analyze_file(self, content: str, file_path: str) -> List[Finding]:
        findings: List[Finding] = []
        lines = content.splitlines()

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("/*"):
                continue

            for pat in self.PATTERNS:
                m = pat.search(line)
                if m:
                    match_str = m.group(0)
                    remediation = (
                        "Replace epoll with standard POSIX poll() or select() for socket loops. "
                        "For high-performance native events, use QNX ionotify() with a sigevent pulse, "
                        "allowing the event loop to block on MsgReceive()."
                    )
                    sample_code = (
                        "// QNX 8.0 Porting: Standard POSIX poll() fallback\n"
                        "#include <poll.h>\n"
                        "struct pollfd fds[2];\n"
                        "fds[0].fd = socket_fd;\n"
                        "fds[0].events = POLLIN | POLLERR;\n"
                        "int ready = poll(fds, 1, timeout_ms);\n"
                        "if (ready > 0 && (fds[0].revents & POLLIN)) { /* process */ }"
                    )
                    findings.append(
                        self.create_finding(
                            file_path=file_path,
                            line_number=idx,
                            code_snippet=line,
                            remediation=remediation,
                            remediation_code=sample_code,
                            custom_desc=f"Detected '{match_str}' which is unsupported on QNX SDP 8.0.",
                        )
                    )
                    break
        return findings


class TimerfdUsageRule(BaseRule):
    rule_id = "QNX-002-TIMERFD"
    category = FindingCategory.LINUX_SPECIFIC_SYSCALL
    severity = Severity.CRITICAL
    title = "Non-Portable Linux timerfd API Usage"
    description = (
        "Linux timerfd APIs (timerfd_create, timerfd_settime) are Linux kernel abstractions "
        "and do not exist in the QNX SDP 8.0 C library."
    )
    documentation_url = DOC_LINKS["pulses_timers"]
    rationale = (
        "QNX Neutrino timing architecture delivers real-time notifications via standard POSIX timers "
        "(timer_create) coupled to QNX Pulses (SIGEV_PULSE) directly into an IPC Channel."
    )

    PATTERNS = [
        re.compile(r"\b(timerfd_create|timerfd_settime|timerfd_gettime)\b"),
        re.compile(r"#\s*include\s*<sys/timerfd\.h>"),
    ]

    def analyze_file(self, content: str, file_path: str) -> List[Finding]:
        findings: List[Finding] = []
        lines = content.splitlines()

        for idx, line in enumerate(lines, start=1):
            for pat in self.PATTERNS:
                m = pat.search(line)
                if m:
                    match_str = m.group(0)
                    remediation = (
                        "Use standard POSIX timer_create() with SIGEV_PULSE delivered to a QNX channel. "
                        "If a file descriptor is strictly required by third-party abstractions, "
                        "couple a POSIX timer to a pipe() or socketpair()."
                    )
                    sample_code = (
                        "// QNX 8.0: High-performance POSIX timer with Pulse\n"
                        "#include <sys/netmgr.h>\n"
                        "#include <sys/neutrino.h>\n"
                        "#include <time.h>\n\n"
                        "struct sigevent event;\n"
                        "SIGEV_PULSE_INIT(&event, coid, priority, CODE_TIMER, 0);\n"
                        "timer_t timer_id;\n"
                        "timer_create(CLOCK_MONOTONIC, &event, &timer_id);\n"
                        "struct itimerspec itime = {{1, 0}, {1, 0}}; // 1s periodic\n"
                        "timer_settime(timer_id, 0, &itime, NULL);"
                    )
                    findings.append(
                        self.create_finding(
                            file_path=file_path,
                            line_number=idx,
                            code_snippet=line,
                            remediation=remediation,
                            remediation_code=sample_code,
                            custom_desc=f"Detected Linux '{match_str}'. Use POSIX timer_create() with SIGEV_PULSE.",
                        )
                    )
                    break
        return findings


class EventfdUsageRule(BaseRule):
    rule_id = "QNX-003-EVENTFD"
    category = FindingCategory.LINUX_SPECIFIC_SYSCALL
    severity = Severity.CRITICAL
    title = "Non-Portable Linux eventfd API Usage"
    description = (
        "Linux eventfd is a kernel counter mapped to a file descriptor. "
        "It is not supported on QNX SDP 8.0."
    )
    documentation_url = DOC_LINKS["microkernel_ipc"]
    rationale = (
        "QNX Neutrino provides lightweight non-blocking 8-byte Pulses (MsgSendPulse) for inter-thread "
        "and inter-process event signaling, with zero kernel memory allocation overhead."
    )

    PATTERNS = [
        re.compile(r"\b(eventfd|eventfd_read|eventfd_write)\b"),
        re.compile(r"#\s*include\s*<sys/eventfd\.h>"),
    ]

    def analyze_file(self, content: str, file_path: str) -> List[Finding]:
        findings: List[Finding] = []
        lines = content.splitlines()

        for idx, line in enumerate(lines, start=1):
            for pat in self.PATTERNS:
                m = pat.search(line)
                if m:
                    match_str = m.group(0)
                    remediation = (
                        "Replace eventfd with a standard POSIX pipe() or socketpair() if an event fd is needed. "
                        "For native QNX services, send a Neutrino Pulse via MsgSendPulse()."
                    )
                    sample_code = (
                        "// POSIX pipe drop-in for inter-thread wakeup on QNX:\n"
                        "int wake_fds[2];\n"
                        "pipe(wake_fds);\n"
                        "// Writer: write(wake_fds[1], \"w\", 1);\n"
                        "// Reader: poll() on wake_fds[0] and read() to drain."
                    )
                    findings.append(
                        self.create_finding(
                            file_path=file_path,
                            line_number=idx,
                            code_snippet=line,
                            remediation=remediation,
                            remediation_code=sample_code,
                            custom_desc=f"Detected Linux '{match_str}'. Use POSIX pipe() or QNX Pulses.",
                        )
                    )
                    break
        return findings


class SignalfdInotifyRule(BaseRule):
    rule_id = "QNX-004-SIGNALFD-INOTIFY"
    category = FindingCategory.LINUX_SPECIFIC_SYSCALL
    severity = Severity.CRITICAL
    title = "Non-Portable signalfd or inotify API Usage"
    description = (
        "signalfd and inotify are Linux-specific kernel interfaces and do not exist on QNX."
    )
    documentation_url = DOC_LINKS["porting_guide"]
    rationale = (
        "QNX provides standard POSIX sigwaitinfo() / sigtimedwait() for synchronous signal handling, "
        "and dircache / filesystem polling for file changes."
    )

    PATTERNS = [
        re.compile(r"\b(signalfd|signalfd4)\b"),
        re.compile(r"\b(inotify_init|inotify_init1|inotify_add_watch)\b"),
        re.compile(r"#\s*include\s*<sys/(signalfd|inotify)\.h>"),
    ]

    def analyze_file(self, content: str, file_path: str) -> List[Finding]:
        findings: List[Finding] = []
        lines = content.splitlines()

        for idx, line in enumerate(lines, start=1):
            for pat in self.PATTERNS:
                m = pat.search(line)
                if m:
                    findings.append(
                        self.create_finding(
                            file_path=file_path,
                            line_number=idx,
                            code_snippet=line,
                            remediation="Replace signalfd with sigwaitinfo(). Replace inotify with directory monitoring or polling.",
                            remediation_code="// POSIX sigwaitinfo:\nsiginfo_t info;\nsigset_t set;\nsigemptyset(&set);\nsigaddset(&set, SIGTERM);\nsigwaitinfo(&set, &info);",
                            custom_desc=f"Detected Linux-specific '{m.group(0)}'.",
                        )
                    )
                    break
        return findings
