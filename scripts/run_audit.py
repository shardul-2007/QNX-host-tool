#!/usr/bin/env python3
"""
QNX Sentinel - Host Toolchain Audit Runner
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from qnx_sentinel.cli import main

if __name__ == "__main__":
    sys.argv = ["qnx-sentinel", "audit"]
    sys.exit(main())
