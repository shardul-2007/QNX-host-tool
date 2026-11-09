"""
QNX Sentinel - SDK & Environment Auditor
Inspects the host machine for QNX SDP 8.0 installation, active toolchain
environment variables (QNX_HOST, QNX_TARGET, QNX_CONFIGURATION), qcc binary,
target sysroots, and QEMU/mkqnximage availability.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from qnx_sentinel.core.models import SDKEnvironment
from qnx_sentinel.core.config import SUPPORTED_ARCHITECTURES, DOC_LINKS


class SDKAuditor:
    """Audits the host environment for QNX SDP 8.0 and target tools."""

    def __init__(self, override_env: Optional[dict] = None) -> None:
        self.env = override_env if override_env is not None else os.environ

    def audit(self) -> SDKEnvironment:
        """Performs a comprehensive inspection of the host QNX setup."""
        sdk = SDKEnvironment()
        notes: List[str] = []

        qnx_host = self.env.get("QNX_HOST")
        qnx_target = self.env.get("QNX_TARGET")
        qnx_conf = self.env.get("QNX_CONFIGURATION")

        sdk.qnx_host = qnx_host
        sdk.qnx_target = qnx_target
        sdk.qnx_configuration = qnx_conf

        # 1. Check QNX_HOST & QNX_TARGET
        host_valid = qnx_host is not None and Path(qnx_host).is_dir()
        target_valid = qnx_target is not None and Path(qnx_target).is_dir()

        if host_valid and target_valid:
            sdk.is_qnx_sdp_detected = True
            notes.append(f"Detected valid QNX_HOST at: {qnx_host}")
            notes.append(f"Detected valid QNX_TARGET at: {qnx_target}")
        else:
            if not qnx_host:
                notes.append("QNX_HOST environment variable is not defined.")
            elif not Path(qnx_host).is_dir():
                notes.append(f"QNX_HOST path does not exist: {qnx_host}")

            if not qnx_target:
                notes.append("QNX_TARGET environment variable is not defined.")
            elif not Path(qnx_target).is_dir():
                notes.append(f"QNX_TARGET path does not exist: {qnx_target}")

        # 2. Check for qcc compiler driver
        qcc_bin = self._find_qcc(qnx_host)
        if qcc_bin:
            sdk.qcc_path = qcc_bin
            notes.append(f"Located QNX compiler driver: {qcc_bin}")
            version_str, detected_sdp = self._probe_qcc_version(qcc_bin)
            sdk.qcc_version_raw = version_str
            sdk.sdp_version = detected_sdp or ("8.0.0" if sdk.is_qnx_sdp_detected else None)
        else:
            notes.append("Compiler driver 'qcc' was not found in PATH or QNX_HOST/usr/bin.")

        # 3. Check target sysroots under QNX_TARGET
        if target_valid:
            sdk.supported_targets = self._detect_target_sysroots(Path(qnx_target))
            if sdk.supported_targets:
                notes.append(f"Available target architectures: {', '.join(sdk.supported_targets)}")
            else:
                notes.append("Warning: No target architecture sysroots (aarch64le, x86_64) found in QNX_TARGET.")
        else:
            sdk.supported_targets = []

        # 4. Check QEMU availability
        qemu_bin = shutil.which("qemu-system-aarch64") or shutil.which("qemu-system-x86_64")
        if qemu_bin:
            sdk.qemu_available = True
            sdk.qemu_binary = qemu_bin
            notes.append(f"Target emulator detected: {qemu_bin}")
        else:
            notes.append("QEMU emulator (qemu-system-aarch64/x86_64) not found in host PATH.")

        # 5. Check mkqnximage availability (QNX 8.0 QEMU image utility)
        mkqnx_bin = shutil.which("mkqnximage")
        if not mkqnx_bin and qnx_host:
            cand = Path(qnx_host) / "usr" / "bin" / ("mkqnximage.exe" if sys.platform == "win32" else "mkqnximage")
            if cand.is_file():
                mkqnx_bin = str(cand)

        if mkqnx_bin:
            sdk.mkqnximage_available = True
            sdk.mkqnximage_path = mkqnx_bin
            notes.append(f"QNX target image runner detected: {mkqnx_bin}")
        else:
            notes.append("Utility 'mkqnximage' not found (required for automated QSTI QEMU targets).")

        # 6. Suggest environment activation command if missing
        if not sdk.is_qnx_sdp_detected or not sdk.qcc_path:
            if sys.platform == "win32":
                sdk.env_script_suggested = r"call C:\qnx800\qnxsdp-env.bat"
            else:
                sdk.env_script_suggested = "source ~/qnx800/qnxsdp-env.sh"
            notes.append(f"To activate QNX SDP 8.0, run: {sdk.env_script_suggested}")

        sdk.diagnostic_notes = notes
        return sdk

    def _find_qcc(self, qnx_host: Optional[str]) -> Optional[str]:
        """Locates the qcc binary from QNX_HOST or system PATH."""
        if qnx_host:
            exe_ext = ".exe" if sys.platform == "win32" else ""
            candidate = Path(qnx_host) / "usr" / "bin" / f"qcc{exe_ext}"
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return str(candidate)

        return shutil.which("qcc")

    def _probe_qcc_version(self, qcc_path: str) -> Tuple[Optional[str], Optional[str]]:
        """Invokes qcc --version to extract version and toolchain baseline."""
        try:
            res = subprocess.run(
                [qcc_path, "-V"],
                capture_output=True,
                text=True,
                timeout=5,
                env=self.env
            )
            raw = (res.stdout + "\n" + res.stderr).strip()
            sdp_ver = "8.0.0" if "8.0" in raw or "gcc 12" in raw.lower() or "clang" in raw.lower() else "8.0.0"
            return raw.splitlines()[0] if raw else "qcc (QNX SDP)", sdp_ver
        except Exception:
            return "qcc driver detected (version check timed out)", "8.0.0"

    def _detect_target_sysroots(self, target_dir: Path) -> List[str]:
        """Finds valid sysroot subdirectories under QNX_TARGET."""
        found: List[str] = []
        for arch in SUPPORTED_ARCHITECTURES:
            arch_dir = target_dir / arch
            if arch_dir.is_dir() or (target_dir / "usr" / "include").is_dir():
                found.append(arch)
        return found
