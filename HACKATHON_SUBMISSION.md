# QNX Global Hackathon 2026 — Official Submission Entry

## 📌 Project Overview

- **Project Title:** QNX Sentinel — Intelligent QNX Build, Test & Compatibility Analyzer
- **Category:** Developer Tooling & Host Tools
- **Target Host Environments:** Windows 10/11 (x64), Linux (Ubuntu/RHEL x64/AArch64), macOS (Intel/Apple Silicon)
- **Target QNX Environment:** QNX Software Development Platform (SDP) 8.0 (Neutrino RTOS) targeting 64-bit ARM (`aarch64le`) and x86 (`x86_64`)
- **Repository Path:** `c:\Users\shard\Downloads\QNX host tool`

---

## 🎯 Executive Pitch

**QNX Sentinel** is an open, host-side developer tool that dramatically simplifies building, testing, and migrating C/C++ software for **QNX SDP 8.0**. 

By combining **deep static analysis** of Linux/glibc vs. QNX microkernel portability, **automated CMake/Makefile build configuration adaptation**, **compiler error diagnostic intelligence**, and **transparent target test execution** across physical boards, QEMU, and simulated environments, QNX Sentinel empowers both embedded veterans and Linux engineers transitioning to QNX to build deterministic, safe, real-time software faster and with complete confidence.

---

## 🔍 Official Documentation Audit & Grounding

QNX Sentinel is strictly built upon verified documentation and specifications for **QNX SDP 8.0**:

1. **Microkernel Architecture & Primitives:**
   - Real-time priority model (1 to 255; default non-critical priority 10).
   - Core IPC primitives: Channels, Connections, Messages (`MsgSend`, `MsgReceive`, `MsgReply`), and non-blocking 8-byte Pulses (`SIGEV_PULSE_INIT`, `MsgSendPulse`).
   - Logging via QNX System Logger 2 (`slog2_register`, `slog2c`, `SLOG2_INFO`, `SLOG2_ERROR`).
2. **Compiler Toolchain (SDP 8.0 Updates):**
   - Frontline compiler drivers: `qcc` (C) and `q++` (C++).
   - Compiler baselines: **GCC 12.2.0** and **LLVM / Clang**.
   - Target variant profiles via `-V`: `-Vgcc_ntoaarch64le`, `-Vgcc_ntox86_64`.
   - Default C++ Standard Library: **LLVM `libc++`** (`-stdlib=libc++`).
   - Deprecated flags in SDP 8.0: `-lang-c++` is deprecated; use `q++` or `-x c++`.
   - Integrated libraries: Threading (`pthread`), dynamic loading (`dlopen`), and real-time clocks are integrated directly into standard `libc.so` (no separate `-lpthread`, `-ldl`, `-lrt`).
3. **Target & Emulation Framework:**
   - Quick Start Target Image (QSTI) management via official QNX 8.0 command `mkqnximage` (`--type=qemu`, `--run`, `--getip`).
   - QEMU target integration (`qemu-system-aarch64`, `qemu-system-x86_64`).

---

## 💡 Implemented Core Features

### 1. Project Analyzer (`qnx_sentinel.analyzer.project_analyzer`)
- Inspects repository structure, enumerating C, C++, and header files, and lines of code.
- Identifies build systems: CMake, QNX Recursive Make (`common.mk`), and GNU Make.
- Detects missing QNX 8.0 configuration files (`qnx.toolchain.cmake`, `CMakePresets.json`).
- Flags incompatible dependencies and host-specific flags (`-lpthread`, `-ldl`, `-lrt`, `-march=native`, `-m64`).
- Reports suspicious platform-specific assumptions (`#ifdef __linux__` without `__QNX__`, `/proc/self/exe`, `/sys/class`).

### 2. QNX Compatibility Analyzer (`qnx_sentinel.analyzer.compatibility_engine`)
- Static analysis engine running 15+ modular rules across 8 categories:
  - **Linux Syscalls:** `epoll` (`epoll_create1`, `epoll_ctl`, `epoll_wait`), `timerfd`, `eventfd`, `signalfd`, `inotify`.
  - **GNU Extensions:** `pthread_yield()`, `get_current_dir_name()`, `strndupa()`, `cpu_set_t`.
  - **Filesystem Assumptions:** `/proc/self/exe`, `/dev/shm` vs `/dev/shmem`, `/sys/class`.
  - **Process/Thread Control:** `prctl()`, multi-threaded `fork()`, nice priorities.
  - **IPC Primitives:** Legacy System V IPC (`shmget`, `semget`, `msgget`).
  - **Compiler Flags:** Deprecated `-lang-c++`, host-specific flags.
  - **QNX Idioms:** Encouraging `slog2` over raw stdout/stderr in embedded services.
- Assigns severity ratings (`CRITICAL`, `WARNING`, `BEST_PRACTICE`, `INFO`).
- Computes the **QNX 8.0 Readiness Index (0–100)** and letter grade (A–F).
- Outputs exact line numbers, offending code snippets, and verified QNX 8.0 drop-in code fixes.

### 3. Build Configuration Assistant (`qnx_sentinel.builder.config_assistant`)
- Generates official `qnx.toolchain.cmake` configured for CMake 3.25+ and QNX SDP 8.0.
- Generates `CMakePresets.json` standardizing Debug/Release configurations for AArch64 and x86_64.
- Generates standard QNX recursive `common.mk` files.
- Generates unified diffs for existing `CMakeLists.txt` files to make Linux libraries conditional for QNX.
- **Safety Policy:** Operates in dry-run mode by default; never modifies files without explicit `--apply` confirmation.

### 4. Build & Verification Runner (`qnx_sentinel.builder.build_runner`)
- Supports dual execution modes:
  - **Actual Toolchain Mode:** Invokes `cmake` and `qcc` when QNX SDP 8.0 is present.
  - **SDK Simulated Verification Mode:** Accurately reproduces expected QNX 8.0 compiler/linker output on standard workstations.
- Every run is clearly tagged with its execution mode.

### 5. Target Test Assistant (`qnx_sentinel.tester.test_runner`)
- Probes for available targets: physical hardware over SSH, QEMU virtual targets via `mkqnximage`, or host simulated test harnesses.
- Executes tests and parses results (Passed, Failed, Skipped, Duration).
- Prominently tags simulated runs with explicit notice banners to prevent any confusion with actual hardware execution.

### 6. Diagnostic Intelligence Engine (`qnx_sentinel.diagnostics.error_explainer`)
- Parses raw compiler error outputs from `qcc`, GCC 12, Clang, and `ld`.
- Matches error signatures against a verified QNX 8.0 knowledge base.
- Explains the architectural microkernel reason for the failure.
- Provides unified diff code patches and direct hyperlinks to official QNX 8.0 documentation anchors.

### 7. Developer Dashboard & Reporters (`qnx_sentinel.reporter`)
- **Terminal Reporter:** Rich colorized output with ASCII badges and score meters.
- **JSON Reporter:** Standardized format for CI/CD pipeline automation (`--format json`).
- **Markdown Reporter:** GitHub Flavored Markdown summary (`--format markdown`).
- **Web Dashboard:** Embedded, zero-dependency local web server (`qnx-sentinel serve`) at `http://127.0.0.1:8080` with dark developer UI, live search, and interactive controls.

---

## 📊 Verification & Test Results

### 1. Automated Test Suite
- **Location:** `tests/`
- **Total Tests:** 24 unit and integration tests across 8 test suites.
- **Result:** **24/24 PASSED in 0.902 seconds** (`Ran 24 tests in 0.902s - OK`).

### 2. Sample Project Verification
- **Test Case 1: Clean QNX 8.0 Project (`samples/qnx8_sensor_service`)**
  - **Score:** `100.0/100 [Grade A]`
  - **Violations:** 0 Critical, 0 Warnings
  - **Build & Tests:** Verified passing.
- **Test Case 2: Portability Challenge (`samples/legacy_linux_telematics`)**
  - **Score:** `0.0/100 [Grade F]`
  - **Violations Detected:** 16 Critical blockers, 11 Portability warnings, 3 Info notices.
  - **Remediation:** Accurate code patches generated for all violations.

---

## 🔒 Security & Reliability Guarantees

- **No Arbitrary Code Execution:** Commands are strictly parameterized; `shell=True` is prohibited.
- **User Confirmation Required:** Modifying or generating build files requires explicit `--apply` confirmation.
- **Path Traversal Protection:** All file paths are sanitized and resolved through `pathlib.Path.resolve()`.
- **Zero Cloud Dependencies:** Operates 100% locally and offline without data exfiltration or external telemetry.

---

## ⚙️ Exact Setup & Execution Commands

```bash
# 1. Environment Audit
python -m qnx_sentinel.cli audit

# 2. Analyze Valid QNX 8.0 Project
python -m qnx_sentinel.cli analyze samples/qnx8_sensor_service

# 3. Analyze Legacy Linux Project
python -m qnx_sentinel.cli analyze samples/legacy_linux_telematics

# 4. Preview Build Configuration Changes (Dry-Run)
python -m qnx_sentinel.cli build-assist samples/legacy_linux_telematics

# 5. Apply Build Configuration Changes with Confirmation
python -m qnx_sentinel.cli build-assist samples/legacy_linux_telematics --apply

# 6. Execute Build Verification
python -m qnx_sentinel.cli build samples/qnx8_sensor_service --arch aarch64le

# 7. Execute Target Tests
python -m qnx_sentinel.cli test samples/qnx8_sensor_service

# 8. Run Diagnostic Intelligence Engine on Error Log
python -m qnx_sentinel.cli diagnose "fatal error: sys/epoll.h: No such file or directory"

# 9. Launch Interactive Local Web Dashboard
python -m qnx_sentinel.cli serve samples/legacy_linux_telematics --port 8080

# 10. Run End-to-End Automated Demo
python scripts/run_demo.py

# 11. Run Full Automated Test Suite
python -m unittest discover -s tests -p "test_*.py"
```

---

## 🛠️ Limitations & Future Roadmap

- **Clang AST Integration:** Future releases can incorporate Clang libclang python bindings for AST-level macro expansions when LLVM is present on host.
- **Momentics IDE Plugin:** Packaging QNX Sentinel's diagnostic engine as an Eclipse CDT / Momentics IDE extension or VS Code Language Server Protocol (LSP) extension.
- **Automated Sigevent Shims:** Automatic generation of C compatibility wrappers (`sys/epoll.h` drop-in wrapper over `poll()`) for large third-party open-source libraries.
