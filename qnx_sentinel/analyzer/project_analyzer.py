"""
QNX Sentinel - Project Structure & Build Configuration Analyzer
Inspects source trees, identifies C/C++ source and header files, detects build systems
(CMake, QNX Recursive Make, GNU Make), identifies missing QNX configuration files,
and flags incompatible dependencies and suspicious platform assumptions.
"""

import os
import re
from pathlib import Path
from typing import List, Set, Tuple

from qnx_sentinel.core.models import ProjectStructure, ProjectMetrics
from qnx_sentinel.core.config import (
    C_EXTENSIONS,
    CPP_EXTENSIONS,
    HEADER_EXTENSIONS,
    BUILD_FILENAMES,
    DEFAULT_EXCLUDE_DIRS,
    DEFAULT_TOOLCHAIN_FILENAME,
    DEFAULT_PRESETS_FILENAME,
    DEFAULT_COMMON_MK_FILENAME,
)
from qnx_sentinel.core.exceptions import InvalidProjectError


class ProjectAnalyzer:
    """Inspects project layout, build configs, dependencies, and platform assumptions."""

    def __init__(self, root_dir: str | Path) -> None:
        self.root_path = Path(root_dir).resolve()
        if not self.root_path.exists() or not self.root_path.is_dir():
            raise InvalidProjectError(f"Directory not found: {self.root_path}")

    def analyze(self) -> ProjectStructure:
        """Runs full structural analysis on the project directory."""
        proj_name = self.root_path.name
        structure = ProjectStructure(
            root_path=str(self.root_path),
            project_name=proj_name,
        )

        source_files: List[str] = []
        header_files: List[str] = []
        build_files: List[str] = []
        c_count = 0
        cpp_count = 0
        header_count = 0
        total_loc = 0

        # Traverse directory
        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDE_DIRS and not d.startswith(".")]
            rel_root = Path(root).relative_to(self.root_path)

            for file in files:
                rel_path = str(rel_root / file) if str(rel_root) != "." else file
                full_path = Path(root) / file
                suffix = full_path.suffix.lower()

                if suffix in C_EXTENSIONS:
                    source_files.append(rel_path)
                    c_count += 1
                    total_loc += self._count_lines(full_path)
                elif suffix in CPP_EXTENSIONS:
                    source_files.append(rel_path)
                    cpp_count += 1
                    total_loc += self._count_lines(full_path)
                elif suffix in HEADER_EXTENSIONS:
                    header_files.append(rel_path)
                    header_count += 1
                    total_loc += self._count_lines(full_path)
                elif file in BUILD_FILENAMES or suffix == ".cmake" or file.endswith(".mk"):
                    build_files.append(rel_path)

        structure.source_files = sorted(source_files)
        structure.header_files = sorted(header_files)
        structure.build_files = sorted(build_files)
        structure.metrics = ProjectMetrics(
            total_files=len(source_files) + len(header_files) + len(build_files),
            c_files=c_count,
            cpp_files=cpp_count,
            header_files=header_count,
            build_files=len(build_files),
            lines_of_code=total_loc,
        )

        # Detect build systems
        self._detect_build_systems(structure)

        # Detect missing configurations
        self._detect_missing_configs(structure)

        # Inspect build files for incompatible dependencies & assumptions
        self._inspect_build_dependencies(structure)

        # Inspect source files for platform assumptions
        self._inspect_platform_assumptions(structure)

        return structure

    def _count_lines(self, path: Path) -> int:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return sum(1 for line in f if line.strip())
        except Exception:
            return 0

    def _detect_build_systems(self, structure: ProjectStructure) -> None:
        """Identifies active build systems in the repository."""
        systems: List[str] = []
        has_cmake = any("CMakeLists.txt" in f for f in structure.build_files)
        has_common_mk = any("common.mk" in f for f in structure.build_files)
        has_makefile = any("Makefile" in f or "makefile" in f for f in structure.build_files)

        if has_cmake:
            systems.append("CMake")
        if has_common_mk:
            systems.append("QNX_Recursive_Make")
        elif has_makefile:
            systems.append("GNU_Make")

        if not systems:
            systems.append("Custom/Generic")

        structure.build_systems = systems

    def _detect_missing_configs(self, structure: ProjectStructure) -> None:
        """Checks for standard QNX 8.0 configuration files."""
        has_cmake = "CMake" in structure.build_systems
        has_qnx_make = "QNX_Recursive_Make" in structure.build_systems

        has_toolchain = any(
            DEFAULT_TOOLCHAIN_FILENAME in f or "qnx" in f.lower() and f.endswith(".cmake")
            for f in structure.build_files
        )
        has_presets = any(DEFAULT_PRESETS_FILENAME in f for f in structure.build_files)

        if has_cmake:
            if has_toolchain:
                structure.detected_configs.append(f"Toolchain file: {DEFAULT_TOOLCHAIN_FILENAME}")
            else:
                structure.missing_configs.append(
                    f"Missing {DEFAULT_TOOLCHAIN_FILENAME} (Required for cross-compiling with QNX SDP 8.0 qcc)"
                )

            if has_presets:
                structure.detected_configs.append(f"CMake presets: {DEFAULT_PRESETS_FILENAME}")
            else:
                structure.missing_configs.append(
                    f"Missing {DEFAULT_PRESETS_FILENAME} (Recommended for reproducible QNX 8.0 AArch64/x86_64 build profiles)"
                )

        if has_qnx_make:
            structure.detected_configs.append("QNX recursive make architecture (common.mk)")
        elif "GNU_Make" in structure.build_systems:
            structure.missing_configs.append(
                f"Missing {DEFAULT_COMMON_MK_FILENAME} (Standard QNX recursive make system definition)"
            )

    def _inspect_build_dependencies(self, structure: ProjectStructure) -> None:
        """Scans CMakeLists.txt and Makefiles for problematic libraries & flags."""
        incompatible: List[str] = []

        patterns = [
            (r"-lpthread\b", "Explicit '-lpthread' library flag (POSIX threads are built into QNX libc; linking libpthread fails or is redundant)"),
            (r"-ldl\b", "Explicit '-ldl' library flag (Dynamic linking dlopen/dlsym are built into QNX libc; libdl does not exist on QNX)"),
            (r"-lrt\b", "Explicit '-lrt' library flag (POSIX realtime timers and clock functions are built into QNX libc; librt does not exist on QNX)"),
            (r"-lang-c\+\+", "Deprecated compiler flag '-lang-c++' (Deprecated in QNX 8.0 GCC 12/Clang; use 'q++' or '-x c++')"),
            (r"-march=native\b", "Host-specific flag '-march=native' (Incompatible with cross-compilation targeting QNX AArch64/x86_64)"),
            (r"-m64\b", "Hardcoded host flag '-m64' (Use QNX target variant '-Vgcc_ntox86_64' or '-Vgcc_ntoaarch64le' instead)"),
        ]

        for bfile in structure.build_files:
            full_path = self.root_path / bfile
            try:
                content = full_path.read_text(encoding="utf-8", errors="ignore")
                for pat, msg in patterns:
                    if re.search(pat, content):
                        incompatible.append(f"[{bfile}] {msg}")
            except Exception:
                continue

        structure.incompatible_dependencies = incompatible

    def _inspect_platform_assumptions(self, structure: ProjectStructure) -> None:
        """Inspects source files for hardcoded Linux/Windows platform assumptions."""
        assumptions: List[str] = []

        # Look for #ifdef __linux__ without QNX handling
        linux_guard_pat = re.compile(r"#\s*(?:ifdef|if\s+defined)\s*\(__linux__\)")
        qnx_guard_pat = re.compile(r"__QNX__|__QNXNTO__")

        for sfile in structure.source_files[:50]:  # sample representative files
            full_path = self.root_path / sfile
            try:
                content = full_path.read_text(encoding="utf-8", errors="ignore")
                if linux_guard_pat.search(content) and not qnx_guard_pat.search(content):
                    assumptions.append(
                        f"[{sfile}] Contains '#ifdef __linux__' blocks with no '__QNX__' or '__QNXNTO__' branch"
                    )
                if "/proc/self/exe" in content:
                    assumptions.append(
                        f"[{sfile}] Assumes Linux procfs '/proc/self/exe' (QNX requires _cmdname or /proc/<pid>/as)"
                    )
                if "/sys/class" in content or "/sys/devices" in content:
                    assumptions.append(
                        f"[{sfile}] Assumes Linux sysfs path '/sys/...' (Not available on QNX Neutrino RTOS)"
                    )
            except Exception:
                continue

        structure.suspicious_platform_assumptions = assumptions
