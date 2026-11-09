# Security & Reliability Policy — QNX Sentinel

Security and engineering reliability are core tenets of **QNX Sentinel**. This document outlines the security controls, execution boundaries, and reliability guarantees built into the tool.

---

## 1. Safe Automation & Confirmation Boundaries

### Rule: Never Overwrite Without Confirmation
- QNX Sentinel strictly implements a **dry-run by default** policy for all configuration and file modification actions.
- Proposing build configurations (`qnx-sentinel build-assist <path>`) computes and displays unified diffs without modifying disk contents.
- Files are **only** written to disk when the user explicitly provides the `--apply` flag on the command line or confirms via the interactive Web Dashboard modal.
- If `--apply` is omitted, the tool terminates with an informative notice and leaves all project files untouched.

---

## 2. Command Execution & Untrusted Projects

### Arbitrary Code Execution Prevention
- QNX Sentinel **never** executes arbitrary scripts, shell hooks, or unverified commands found inside inspected repositories.
- Build and test operations strictly invoke verified system binaries (`cmake`, `qcc`, `qemu-system-*`, `mkqnximage`) using parameterized argument lists (`subprocess.run(list_of_args)`).
- Shell execution (`shell=True`) is completely disallowed across all subprocess calls to prevent command injection vulnerabilities.

---

## 3. Filesystem Sandboxing & Path Traversal Guards

- All file lookups, project directory walks, and output write operations resolve paths through `pathlib.Path.resolve()`.
- Access is restricted to the target project directory and designated report directories.
- Symlinks pointing outside the project tree during static analysis are handled safely without infinite loops or unauthorized disk writes.

---

## 4. Environment & Credential Protection

- QNX Sentinel inspects only official toolchain environment variables (`QNX_HOST`, `QNX_TARGET`, `QNX_CONFIGURATION`, `PATH`).
- Build logs, reports, and JSON exports are scrubbed to ensure that authorization tokens, private keys, and host credentials are never logged or exposed.

---

## 5. Offline Local Operation & Privacy

- QNX Sentinel operates **100% locally on the host workstation**.
- The embedded Web Dashboard binds strictly to `127.0.0.1` (localhost).
- There are **no cloud telemetry dependencies**, no remote analytics beacons, and no network exfiltration of developer code.
- All dependencies are either from the standard Python library or pinned locally.

---

## 6. Audit Trail & Diagnostic Context

Every generated report (JSON, Markdown, or Terminal) permanently records:
- Exact tool version (`qnx-sentinel 1.0.0`).
- UTC ISO 8601 timestamp.
- Host environment status (detected QNX SDP version, target sysroots).
- Execution mode (`ACTUAL_QNX_SDP_8_0` vs `SDK_SIMULATED_VERIFICATION`).
- Unambiguous tagging on all test results, preventing simulation data from being mistaken for real target runs.
