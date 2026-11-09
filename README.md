# QNX Sentinel — Intelligent QNX 8.0 Build, Test & Compatibility Analyzer

> **QNX Global Hackathon 2026** | **Category:** Developer Tooling & Host Tools  
> **Target OS Support:** Host tools run on **Windows, Linux, macOS** targeting **QNX SDP 8.0 (AArch64 & x86_64)**.  
> **Live Cloud Dashboard:** [https://qnx-sentinel.vercel.app](https://qnx-sentinel.vercel.app)  
> **GitHub Repository:** [https://github.com/shardul-2007/QNX-host-tool](https://github.com/shardul-2007/QNX-host-tool)

---

## 🚀 Executive Summary

**QNX Sentinel** is a developer host tool designed to accelerate, validate, and demystify software development for **QNX SDP 8.0** (Neutrino RTOS).

Transitioning code from standard Linux (glibc, systemd, epoll) or Windows to the deterministic microkernel architecture of QNX 8.0 presents unique engineering friction:
- **Non-portable Linux syscalls** (`epoll`, `timerfd`, `eventfd`, `signalfd`, `prctl`) that do not exist on QNX Neutrino.
- **Subtle glibc assumptions** (`pthread_yield`, `get_current_dir_name`, `strndupa`, `cpu_set_t`).
- **Filesystem discrepancies** (Linux `/proc/self/exe` vs QNX `_cmdname`; `/dev/shm` vs `/dev/shmem`; absent `/sys/class`).
- **Toolchain and build configuration evolution** in QNX 8.0 (GCC 12.2 baseline, LLVM `libc++` default, deprecation of `-lang-c++`, integrated threading in `libc.so`).

**QNX Sentinel eliminates this friction** by providing static code analysis, automated build configuration adaptation, diagnostic intelligence that explains compiler failures, target execution assistance (Hardware, QEMU via `mkqnximage`, and simulated runners), and an interactive local developer dashboard.

---

## 🌟 Key Capabilities

| Capability | Description |
|---|---|
| **1. Official SDK Audit** | Detects active QNX SDP 8.0 environment variables (`QNX_HOST`, `QNX_TARGET`, `QNX_CONFIGURATION`), verifies `qcc` driver availability, checks for QEMU and `mkqnximage`, and provides one-click activation scripts. |
| **2. Structure & Dependency Inspection** | Inspects C/C++ layouts, identifies build systems (CMake, QNX Recursive Make, GNU Make), flags missing QNX configuration files, and identifies non-portable linker flags (`-lpthread`, `-ldl`, `-lrt`, `-march=native`). |
| **3. Static Compatibility Engine** | Rule-based code inspection detecting non-portable APIs with exact file/line coordinates, severity ratings (`CRITICAL`, `WARNING`, `BEST_PRACTICE`, `INFO`), and verified QNX 8.0 remediation code snippets. |
| **4. Build Configuration Assistant** | Generates verified `qnx.toolchain.cmake`, `CMakePresets.json`, and QNX `common.mk` files. Previews changes via unified diffs and strictly adheres to a safe dry-run policy. |
| **5. Build & Verification Runner** | Compiles with `qcc` when the toolchain is present, or executes a simulated verification pass when SDK is absent, accurately reproducing expected compiler diagnostics. |
| **6. Target Test Assistant** | Detects physical hardware, QEMU virtual targets (`mkqnximage --run`), or executes host simulation test harnesses with clear attribution banners. |
| **7. Diagnostic Intelligence Engine** | Ingests raw compiler/linker logs, isolates root causes, explains microkernel rationale, and links directly to official QNX 8.0 documentation anchors. |
| **8. Interactive Web Dashboard** | Zero-dependency local web dashboard (`http://127.0.0.1:8080`) featuring real-time compliance grading (A–F), interactive search, copyable code fixes, and test runners. |

---

## ⚡ Quick Start

### Installation

QNX Sentinel is written in standard Python 3.8+ with **zero mandatory external pip dependencies**:

```bash
# Clone repository
git clone https://github.com/qnx-sentinel/qnx-sentinel.git
cd "QNX host tool"

# Install as editable CLI tool (optional, or run directly via python -m qnx_sentinel.cli)
pip install -e .
```

### 1. Audit Host Environment
Inspect whether QNX SDP 8.0 and QEMU are configured in the current shell:
```bash
python -m qnx_sentinel.cli audit
```

### 2. Analyze a Project
Analyze a C/C++ codebase and compute the **QNX 8.0 Readiness Index** (0–100):
```bash
python -m qnx_sentinel.cli analyze samples/legacy_linux_telematics
```

### 3. Preview & Apply QNX Build Configurations
Inspect missing build configs and generate verified QNX 8.0 CMake toolchain files:
```bash
# Dry-run preview
python -m qnx_sentinel.cli build-assist samples/legacy_linux_telematics

# Apply changes with user confirmation
python -m qnx_sentinel.cli build-assist samples/legacy_linux_telematics --apply
```

### 4. Run Build Verification
Execute a cross-compilation or simulated build targeting 64-bit ARM (`aarch64le`) or x86 (`x86_64`):
```bash
python -m qnx_sentinel.cli build samples/qnx8_sensor_service --arch aarch64le
```

### 5. Diagnose Build Errors
Feed compiler error logs to obtain instant root-cause analysis and code diffs:
```bash
python -m qnx_sentinel.cli diagnose "fatal error: sys/epoll.h: No such file or directory"
```

### 6. Launch the Interactive Web Dashboard
Explore findings visually, filter by severity, and run builds and tests from your browser:
```bash
python -m qnx_sentinel.cli serve samples/legacy_linux_telematics
# Opens http://127.0.0.1:8080
```

---

## 📁 Repository Layout

```text
├── qnx_sentinel/              # Core application package
│   ├── audit/                 # QNX SDP 8.0 environment auditor
│   ├── analyzer/              # Project structure and static rules engine
│   │   └── rules/             # Modular compatibility rules (epoll, prctl, etc.)
│   ├── builder/               # Toolchain generator, presets, and build runner
│   ├── tester/                # Target detector and test assistant
│   ├── diagnostics/           # Compiler error parser and QNX knowledge base
│   ├── reporter/              # Terminal, JSON, Markdown, and Web reporters
│   ├── templates/             # Verified qnx.toolchain.cmake, CMakePresets, Web UI
│   └── cli.py                 # Unified command-line interface
├── samples/                   # Representative test cases
│   ├── qnx8_sensor_service/   # Valid QNX 8.0 sample (Score: 100/100, Grade A)
│   └── legacy_linux_telematics/# Portability challenge sample (Score: 0/100, Grade F)
├── tests/                     # 24 automated unit and integration tests
├── scripts/                   # Automated demo and report generation scripts
├── reports/                   # Sample generated JSON & Markdown reports
├── README.md                  # Project overview and quick start
├── ARCHITECTURE.md            # Modular architecture and data flow
├── QNX_COMPATIBILITY.md       # Verified QNX 8.0 API & toolchain specification
├── INSTALLATION.md            # Host OS setup guide (Windows, Linux, macOS)
├── TESTING.md                 # Test harness and verification results
├── SECURITY.md                # Security and safety guarantees
├── DEMO_SCRIPT.md             # Step-by-step video demonstration script
└── HACKATHON_SUBMISSION.md    # Official hackathon submission entry
```

---

## 🏆 Hackathon Verification Summary

- **Test Suite:** 24/24 unit & integration tests passing (`Ran 24 tests in 0.902s - OK`).
- **Clean Sample Project (`samples/qnx8_sensor_service`):** Verified 100/100 [Grade A] score, 0 errors, full POSIX/QNX Neutrino microkernel idioms.
- **Porting Challenge Sample (`samples/legacy_linux_telematics`):** Correctly flags 16 Critical blockers and 11 Portability warnings, providing exact line references and verified remediation code.
- **Host Independence:** Functions cleanly on Windows, Linux, and macOS host environments without requiring physical target hardware.
