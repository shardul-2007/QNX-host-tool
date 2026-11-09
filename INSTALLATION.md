# Installation & Setup Guide — QNX Sentinel

This guide provides instructions for deploying and running **QNX Sentinel** on Windows, Linux, and macOS host workstations.

---

## 1. System Requirements

### Supported Host Operating Systems
- **Windows:** Windows 10 / 11 (64-bit)
- **Linux:** Ubuntu 20.04 / 22.04 / 24.04 LTS, Red Hat Enterprise Linux 8/9, Fedora (x86_64 or AArch64)
- **macOS:** macOS 12 Monterey, macOS 13 Ventura, macOS 14 Sonoma, macOS 15 Sequoia (Apple Silicon & Intel)

### Host Dependencies
- **Python:** 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14+
- **Git:** 2.20+
- **CMake:** 3.25+ (optional, only needed for actual host build invocation)
- **QNX SDP 8.0:** (Optional for static analysis and simulated runs; required for actual `qcc` binary cross-compilation)

---

## 2. Installation Steps

### Step 1: Clone the Repository
```bash
git clone https://github.com/qnx-sentinel/qnx-sentinel.git
cd "QNX host tool"
```

### Step 2: Install QNX Sentinel
You can install QNX Sentinel into your active Python environment in editable mode:

```bash
# Optional: create a clean virtual environment
python -m venv .venv

# On Linux/macOS:
source .venv/bin/activate

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Install in editable mode
pip install -e .
```

*Note: If you prefer not to install via pip, you can run all commands directly using `python -m qnx_sentinel.cli` from the project root directory!*

---

## 3. Configuring QNX SDP 8.0 (Optional)

If you have a licensed installation of QNX Software Development Platform 8.0 installed on your host machine:

### On Windows
Open Command Prompt or PowerShell and initialize the QNX environment:
```cmd
call C:\qnx800\qnxsdp-env.bat
```

Verify that the environment variables are active:
```cmd
echo %QNX_HOST%
echo %QNX_TARGET%
qcc -V
```

### On Linux / macOS
Open your terminal and source the environment script:
```bash
source ~/qnx800/qnxsdp-env.sh
```

Verify in terminal:
```bash
echo $QNX_HOST
echo $QNX_TARGET
qcc -V
```

### Without QNX SDP 8.0 (Host Simulation Mode)
If QNX SDP 8.0 is not installed on your current workstation, **QNX Sentinel runs automatically in Host-Static Analysis and Simulation Mode**:
- Full static analysis across all C/C++ files.
- QNX 8.0 Readiness Index calculation.
- Generation of verified `qnx.toolchain.cmake` and `CMakePresets.json`.
- Accurate compiler error diagnosis and remediation advice.
- Interactive Web Dashboard on `http://127.0.0.1:8080`.

---

## 4. Verifying the Installation

Run the automated self-test suite to verify all 24 unit and integration tests:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Expected output:
```text
Ran 24 tests in 0.902s
OK
```

Verify CLI responsiveness:
```bash
python -m qnx_sentinel.cli --version
python -m qnx_sentinel.cli audit
```
