# Testing & Verification Specification — QNX Sentinel

This document details the test strategy, representative test cases, edge case handling, and automated test execution results for **QNX Sentinel**.

---

## 1. Test Architecture & Coverage

The QNX Sentinel test suite validates all core modules across 8 test suites containing 24 automated unit and integration tests:

| Test Suite | Module Under Test | Validated Behaviors |
|---|---|---|
| `test_sdk_auditor.py` | `qnx_sentinel.audit` | Host environment inspection, missing `QNX_HOST`/`QNX_TARGET`, sysroot detection, toolchain fallback. |
| `test_project_analyzer.py` | `qnx_sentinel.analyzer` | File taxonomy, C/C++ classification, build system detection (CMake, Make), missing config detection, invalid path error handling. |
| `test_compatibility_engine.py` | `qnx_sentinel.analyzer.rules` | Static analysis across all 8 rule categories (`epoll`, `timerfd`, `eventfd`, `prctl`, `pthread_yield`, `sysfs`, `shm`, `-lang-c++`, `-lpthread`). |
| `test_config_assistant.py` | `qnx_sentinel.builder` | Safe dry-run planning, unified diff computation, permission guards preventing file modification without confirmation (`--apply`). |
| `test_error_explainer.py` | `qnx_sentinel.diagnostics` | Compiler log parsing, knowledge base pattern matching, root-cause categorization, and remediation diff generation. |
| `test_test_runner.py` | `qnx_sentinel.tester` | Target detection (Hardware, QEMU, Simulated), unambiguous attribution banners, simulation test execution. |
| `test_reporters.py` | `qnx_sentinel.reporter` | JSON serialization, Markdown generation, colorized terminal rendering. |
| `test_cli.py` | `qnx_sentinel.cli` | Subcommands (`audit`, `analyze`, `build-assist`, `build`, `test`, `diagnose`), `--fail-under` CI threshold exit codes. |

---

## 2. Representative Test Cases

### Test Case 1: Valid QNX 8.0 Project (`samples/qnx8_sensor_service`)
- **Objective:** Verify that a clean, well-architected QNX 8.0 project passes static analysis with zero false positives.
- **Project Structure:**
  - `CMakeLists.txt` configured with conditional threading (`if(NOT CMAKE_SYSTEM_NAME STREQUAL "QNX")`).
  - `qnx.toolchain.cmake` present targeting `aarch64le` with `qcc` and `q++`.
  - `CMakePresets.json` present.
  - Source files use QNX Neutrino microkernel IPC (`ChannelCreate`, `ConnectAttach`, `MsgReceive`, `MsgReply`), POSIX timers with `SIGEV_PULSE`, and system logging via `slog2`.
- **Expected Result:**
  - **Readiness Score:** `100.0/100 [Grade A]`
  - **Compatibility Findings:** `0 Critical, 0 Warnings, 0 Info`
  - **Build Status:** `SUCCESS`
  - **Test Results:** `3 Passed, 0 Failed`

### Test Case 2: Portability & Incompatibility Sample (`samples/legacy_linux_telematics`)
- **Objective:** Verify that common Linux-specific and glibc assumptions are correctly detected with exact file/line coordinates and remediation code.
- **Portability Flaws Introduced:**
  1. `<sys/epoll.h>`: `epoll_create1`, `epoll_ctl`, `epoll_wait` (CRITICAL)
  2. `<sys/timerfd.h>`: `timerfd_create`, `timerfd_settime` (CRITICAL)
  3. `<sys/eventfd.h>`: `eventfd` (CRITICAL)
  4. `<sys/prctl.h>`: `prctl(PR_SET_NAME, ...)` (CRITICAL)
  5. Linux sysfs: `/sys/class/net/...` (CRITICAL)
  6. Non-standard GNU extension: `pthread_yield()` (WARNING)
  7. Non-standard GNU extension: `get_current_dir_name()` (WARNING)
  8. Non-standard GNU extension: `strndupa()` (WARNING)
  9. Linux symlink: `/proc/self/exe` (WARNING)
  10. System V IPC: `shmget`, `shmctl` (WARNING)
  11. Deprecated compiler flag: `-lang-c++` in `CMakeLists.txt` (WARNING)
  12. Host-specific flag: `-march=native` in `CMakeLists.txt`
  13. Explicit host libraries: `-lpthread`, `-ldl`, `-lrt` (INFO)
  14. Missing `qnx.toolchain.cmake` and `CMakePresets.json` (CONFIG)
- **Expected Result:**
  - **Readiness Score:** `0.0/100 [Grade F]`
  - **Findings Detected:** 16 Critical, 11 Warnings, 3 Info (Total: 30)
  - **Remediation Code:** Provided for every single issue.

---

## 3. Edge Cases & Resilience

| Edge Case | Sentinel Behavior | Verified |
|---|---|---|
| **Missing QNX SDK** | Gracefully notes absence, suggests activation command, and executes in simulated verification mode. | YES |
| **Missing Compiler (`qcc`)** | Does not crash; provides clear diagnostic notice and checks PATH. | YES |
| **Malformed Build Files** | Fails safely with `InvalidProjectError` or reports parse issues without raising unhandled exceptions. | YES |
| **Non-Existent Directory** | Exits with error code 1 and actionable message: `Error: Project directory not found`. | YES |
| **Unavailable QEMU Target** | Reports QEMU emulator missing; routes testing to verified simulated target runner. | YES |
| **CI/CD Threshold Failure** | When `--fail-under 80` is specified and project scores below 80, exits with exit code `2`. | YES |

---

## 4. Test Execution & Verified Results

Execute the complete test suite:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

### Actual Execution Log:
```text
Ran 24 tests in 0.902s

OK
```
All 24 automated unit and integration tests execute in under 1 second with 100% pass rate.
