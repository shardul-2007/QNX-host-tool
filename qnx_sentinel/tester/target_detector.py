"""
QNX Sentinel - Target Environment Detector
Identifies reachable QNX hardware devices, running QEMU virtual targets,
or determines when host-simulation / SDK sandbox mode must be used.
"""

import os
import shutil
import socket
import subprocess
from typing import List, Optional

from qnx_sentinel.core.models import TargetEnvironment, SDKEnvironment
from qnx_sentinel.audit.sdk_auditor import SDKAuditor


class TargetDetector:
    """Discovers and validates QNX 8.0 execution targets."""

    def __init__(self, sdk: Optional[SDKEnvironment] = None) -> None:
        self.sdk = sdk if sdk is not None else SDKAuditor().audit()

    def detect_targets(self) -> List[TargetEnvironment]:
        """Scans for available execution targets (Hardware, QEMU, Simulation)."""
        targets: List[TargetEnvironment] = []

        # 1. Check for configured hardware target from environment (e.g. QNX_TARGET_IP)
        env_ip = os.environ.get("QNX_TARGET_IP")
        if env_ip:
            port = int(os.environ.get("QNX_TARGET_SSH_PORT", "22"))
            is_reachable = self._ping_port(env_ip, port)
            targets.append(
                TargetEnvironment(
                    target_type="HARDWARE",
                    architecture=os.environ.get("QNX_TARGET_ARCH", "aarch64le"),
                    hostname_or_ip=env_ip,
                    ssh_port=port,
                    is_simulated=False,
                    status="REACHABLE" if is_reachable else "UNREACHABLE",
                )
            )

        # 2. Check for running QEMU target (default port 2222 or mkqnximage)
        if self.sdk.qemu_available or self.sdk.mkqnximage_available:
            qemu_port = int(os.environ.get("QNX_QEMU_PORT", "2222"))
            qemu_up = self._ping_port("127.0.0.1", qemu_port)
            targets.append(
                TargetEnvironment(
                    target_type="QEMU",
                    architecture="aarch64le",
                    hostname_or_ip="127.0.0.1",
                    ssh_port=qemu_port,
                    is_simulated=False,
                    qemu_command="mkqnximage --run" if self.sdk.mkqnximage_available else "qemu-system-aarch64 ...",
                    status="ACTIVE" if qemu_up else "READY_TO_LAUNCH",
                )
            )

        # 3. Always provide the verified Simulated Target Runner
        targets.append(
            TargetEnvironment(
                target_type="SIMULATED",
                architecture="aarch64le",
                hostname_or_ip="localhost",
                ssh_port=0,
                is_simulated=True,
                status="ALWAYS_AVAILABLE",
            )
        )

        return targets

    def _ping_port(self, host: str, port: int, timeout_sec: float = 0.5) -> bool:
        """Non-blocking TCP probe to see if target SSH port is open."""
        try:
            with socket.create_connection((host, port), timeout=timeout_sec):
                return True
        except Exception:
            return False
