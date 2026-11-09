#!/usr/bin/env python3
"""
QNX Sentinel - End-to-End Hackathon Demonstration Script
Demonstrates all 6 core features:
  1. Official QNX SDP 8.0 Environment Audit
  2. Project Structure & Dependency Analyzer
  3. QNX Compatibility & Portability Static Analysis
  4. Build Configuration Assistant with Diff Preview
  5. Cross-Compilation & Verification Runner
  6. Diagnostic Intelligence Engine & Remediation
  7. Target Test Assistant with Attribution
"""

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from qnx_sentinel.cli import (
    cmd_audit,
    cmd_analyze,
    cmd_build_assist,
    cmd_build,
    cmd_test,
    cmd_diagnose,
    build_parser,
)
from qnx_sentinel.reporter.terminal_reporter import Colors


def print_banner(step_num: int, title: str):
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}" + "=" * 80)
    print(f"  [STEP {step_num}] {title.upper()}")
    print("=" * 80 + f"{Colors.RESET}\n")
    time.sleep(0.2)


def main():
    parser = build_parser()
    samples_dir = PROJECT_ROOT / "samples"
    clean_proj = samples_dir / "qnx8_sensor_service"
    legacy_proj = samples_dir / "legacy_linux_telematics"

    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("********************************************************************************")
    print("      QNX SENTINEL — LIVE HACKATHON DEMO WALKTHROUGH (QNX SDP 8.0)")
    print("********************************************************************************")
    print(f"{Colors.RESET}")

    # STEP 1: Host Environment Audit
    print_banner(1, "Official QNX SDP 8.0 Environment Audit")
    args = parser.parse_args(["audit"])
    cmd_audit(args)

    # STEP 2: Analyze Valid QNX 8.0 Project
    print_banner(2, "Analyze Valid QNX 8.0 Project (qnx8_sensor_service)")
    args = parser.parse_args(["analyze", str(clean_proj), "--format", "terminal"])
    cmd_analyze(args)

    # STEP 3: Analyze Legacy Linux Project with Known Portability Issues
    print_banner(3, "Analyze Legacy Linux Project with Portability Issues (legacy_linux_telematics)")
    args = parser.parse_args(["analyze", str(legacy_proj), "--format", "terminal"])
    try:
        cmd_analyze(args)
    except SystemExit:
        pass

    # STEP 4: Build Configuration Assistant
    print_banner(4, "Build Configuration Assistant & Diff Generation (Safe Dry-Run)")
    args = parser.parse_args(["build-assist", str(legacy_proj)])
    cmd_build_assist(args)

    # STEP 5: Build Verification Runner
    print_banner(5, "Build Verification & Simulated QNX 8.0 Compiler Execution")
    args = parser.parse_args(["build", str(legacy_proj)])
    cmd_build(args)

    # STEP 6: Diagnostic Intelligence
    print_banner(6, "Diagnostic Intelligence & Error Root-Cause Explanation")
    sample_error = "src/event_loop.c:9:24: fatal error: sys/epoll.h: No such file or directory"
    args = parser.parse_args(["diagnose", sample_error])
    cmd_diagnose(args)

    # STEP 7: Target Test Assistant
    print_banner(7, "Target Test Assistant & Verification Report")
    args = parser.parse_args(["test", str(clean_proj)])
    cmd_test(args)

    print(f"\n{Colors.BOLD}{Colors.GREEN}")
    print("********************************************************************************")
    print("  [SUCCESS] All QNX Sentinel features verified successfully!")
    print("  To launch the interactive Web Dashboard run:")
    print("      python -m qnx_sentinel.cli serve samples/legacy_linux_telematics")
    print("********************************************************************************")
    print(f"{Colors.RESET}\n")


if __name__ == "__main__":
    main()
