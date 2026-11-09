# QNX Sentinel — Hackathon Video Demonstration Script

> **Title:** QNX Sentinel — Intelligent QNX 8.0 Build, Test & Compatibility Analyzer  
> **Category:** Developer Tooling & Host Tools  
> **Duration:** ~5–6 Minutes  
> **Target Audience:** Hackathon Judges, Embedded Software Architects, Linux/Windows-to-QNX Migrators

---

## 🎬 Video Overview & Timeline

| Timestamp | Scene | Key Feature Demonstrated |
|---|---|---|
| `0:00 - 0:40` | **Scene 1: Introduction & The Problem** | Linux-to-QNX friction: epoll, timerfd, glibc vs microkernel. |
| `0:40 - 1:15` | **Scene 2: Environment Audit** | `qnx-sentinel audit` detecting host QNX SDP 8.0 & QEMU. |
| `1:15 - 2:20` | **Scene 3: Static Analysis on Legacy Code** | `qnx-sentinel analyze samples/legacy_linux_telematics`. Score: 0/100 [F]. |
| `2:20 - 3:10` | **Scene 4: Build Configuration Assistant** | `qnx-sentinel build-assist` generating toolchains with diff preview. |
| `3:10 - 4:00` | **Scene 5: Build Verification & Diagnostics** | `qnx-sentinel build` & `diagnose` explaining root causes with docs. |
| `4:00 - 4:45` | **Scene 6: Valid QNX 8.0 Project & Tests** | `qnx8_sensor_service` scoring 100/100 [A] & target test runner. |
| `4:45 - 5:30` | **Scene 7: Interactive Local Web Dashboard** | `qnx-sentinel serve` live in browser with dark UI. |
| `5:30 - 6:00` | **Scene 8: Conclusion** | Summary, architecture, and hackathon impact. |

---

## 🎙️ Step-by-Step Narration & Execution Guide

### Scene 1: Introduction (0:00 - 0:40)
**Visual:** Title slide and split-screen comparison: Monolithic Linux Kernel vs QNX Neutrino Microkernel.  
**Speaker:**
> *"Welcome to the demonstration of **QNX Sentinel**, an intelligent host-side developer tool built for the **QNX Global Hackathon** in the Developer Tooling category.*
>
> *Moving software from Linux to QNX SDP 8.0 is a critical journey for automotive, aerospace, and robotics developers. But developers quickly encounter breaking roadblocks: Linux-specific syscalls like `epoll` and `timerfd` don't exist on QNX; glibc extensions like `pthread_yield` fail to compile; and subtle build configurations in QNX 8.0—like the new GCC 12 baseline, default LLVM `libc++`, and integrated `libc.so` threads—cause confusing linker failures.*
>
> *QNX Sentinel was built to solve this: an intelligent analyzer that audits your environment, inspects your source code, adapts your build system, diagnoses errors, and verifies target execution—on Windows, Linux, and macOS."*

---

### Scene 2: Host Environment Audit (0:40 - 1:15)
**Visual:** Terminal command execution.  
**Action:**
```bash
python -m qnx_sentinel.cli audit
```
**Speaker:**
> *"Let's begin by auditing our host development environment. Running `qnx-sentinel audit` inspects the host workstation for QNX SDP 8.0 environment variables: `QNX_HOST`, `QNX_TARGET`, compiler driver `qcc`, and target emulators like QEMU and `mkqnximage`.*
>
> *Notice that if the SDP is not yet sourced in our shell, Sentinel doesn't crash or fail—it explains exactly how to activate the official toolchain with `call C:\qnx800\qnxsdp-env.bat` (or `source ~/qnx800/qnxsdp-env.sh`), and seamlessly transitions into Host-Static Analysis and Verification Mode."*

---

### Scene 3: Static Analysis on Legacy Linux Project (1:15 - 2:20)
**Visual:** Analyzing `samples/legacy_linux_telematics`.  
**Action:**
```bash
python -m qnx_sentinel.cli analyze samples/legacy_linux_telematics
```
**Speaker:**
> *"Now let's analyze an existing telematics service originally written for Linux. In a single command, QNX Sentinel scans every source file, header, and build configuration.*
>
> *Sentinel immediately flags 16 Critical blockers and 11 Portability warnings, rating the project at a **0.0/100 Readiness Score (Grade F)**.*
>
> *Look at the granularity of the findings: It flags `sys/epoll.h` at line 9 and `epoll_create1` at line 17, explaining that QNX Neutrino RTOS does not implement epoll. Even better, it provides a verified QNX 8.0 drop-in code fix using POSIX `poll()` or `ionotify()` with pulses.*
>
> *It detects `timerfd`, `eventfd`, `prctl()`, non-standard `pthread_yield()`, stack-unsafe `strndupa()`, `/proc/self/exe`, and deprecated `-lang-c++` compiler flags. Every finding includes the exact line number, code snippet, remediation steps, and direct links to the official QNX 8.0 documentation."*

---

### Scene 4: Build Configuration Assistant (2:20 - 3:10)
**Visual:** Proposing build configurations.  
**Action:**
```bash
python -m qnx_sentinel.cli build-assist samples/legacy_linux_telematics
```
**Speaker:**
> *"Next, how does a developer actually configure this project to build with QNX SDP 8.0? That's where our **Build Configuration Assistant** comes in.*
>
> *Adhering to our strict security principle—never overwrite user files without confirmation—Sentinel runs in dry-run mode first.*
>
> *It proposes three clean changes: creating an official `qnx.toolchain.cmake` configured for `qcc` and AArch64/x86_64, creating standard `CMakePresets.json` for Debug and Release builds, and generating a unified diff for `CMakeLists.txt` that eliminates deprecated flags and wraps Linux threading libraries in QNX platform checks."*

---

### Scene 5: Cross-Compilation Verification & Diagnostics (3:10 - 4:00)
**Visual:** Running build and diagnostic engine.  
**Action:**
```bash
python -m qnx_sentinel.cli build samples/legacy_linux_telematics
python -m qnx_sentinel.cli diagnose "fatal error: sys/epoll.h: No such file or directory"
```
**Speaker:**
> *"When we trigger a build with `qnx-sentinel build`, Sentinel compiles with `qcc` if installed, or simulates the exact QNX 8.0 compiler output if running on a standard host. Notice the clear attribution tag: `SDK_SIMULATED_VERIFICATION`.*
>
> *When a developer encounters an unfamiliar compiler error, they can invoke our **Diagnostic Intelligence Engine**: `qnx-sentinel diagnose`.*
>
> *Sentinel parses the error, identifies the root cause in the QNX microkernel context, and produces an actionable patch and documentation reference in milliseconds."*

---

### Scene 6: Valid QNX 8.0 Sample Project & Target Testing (4:00 - 4:45)
**Visual:** Analyzing clean project and running tests.  
**Action:**
```bash
python -m qnx_sentinel.cli analyze samples/qnx8_sensor_service
python -m qnx_sentinel.cli test samples/qnx8_sensor_service
```
**Speaker:**
> *"Now let's examine `qnx8_sensor_service`, a project written natively for QNX SDP 8.0 using `ChannelCreate`, `ConnectAttach`, POSIX timers with `SIGEV_PULSE`, and `slog2` system logging.*
>
> *Sentinel awards it a perfect **100/100 Readiness Score (Grade A)** with 0 violations!*
>
> *Running `qnx-sentinel test` invokes our **Target Test Assistant**. It automatically discovers available targets—physical hardware, QEMU virtual targets via `mkqnximage`, or the host-simulated test harness. It runs our tests and generates a structured report with prominent simulation attribution banners."*

---

### Scene 7: Interactive Local Web Dashboard (4:45 - 5:30)
**Visual:** Opening browser to `http://127.0.0.1:8080`.  
**Action:**
```bash
python -m qnx_sentinel.cli serve samples/legacy_linux_telematics
```
**Speaker:**
> *"Finally, developers who prefer visual workflows can launch the **QNX Sentinel Interactive Web Dashboard**.*
>
> *Running on an embedded, zero-dependency local HTTP server, this dashboard gives developers a real-time HUD of their project's QNX 8.0 health: compliance gauges, interactive severity filters, expandable issue cards with 1-click copyable code fixes, and real-time build and test execution buttons."*

---

### Scene 8: Conclusion (5:30 - 6:00)
**Visual:** Final summary slide with test results and GitHub link.  
**Speaker:**
> *"In summary, QNX Sentinel delivers:
> - Full offline host-tool support across Windows, Linux, and macOS.
> - Deep QNX SDP 8.0 integration and verified microkernel rules.
> - Safe build configuration automation with diff previews.
> - Transparent target testing and diagnostic intelligence.
> - 24 passing automated tests and zero external dependencies.
>
> QNX Sentinel empowers developers everywhere to build safe, deterministic, high-performance software for QNX 8.0 with total confidence. Thank you!"*
