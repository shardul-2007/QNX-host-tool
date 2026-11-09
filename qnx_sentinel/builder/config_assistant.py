"""
QNX Sentinel - Build Configuration Assistant
Inspects CMakeLists.txt and Makefiles, explains QNX 8.0 toolchain requirements,
generates verified toolchain and preset files, and computes unified diffs
for safe, user-confirmed application.
"""

import difflib
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from qnx_sentinel.core.models import ProjectStructure
from qnx_sentinel.core.config import (
    DEFAULT_TOOLCHAIN_FILENAME,
    DEFAULT_PRESETS_FILENAME,
    DEFAULT_COMMON_MK_FILENAME,
)


class ConfigAssistant:
    """Assists developers with QNX SDP 8.0 build configurations and templates."""

    def __init__(self, project_dir: str | Path) -> None:
        self.project_dir = Path(project_dir).resolve()
        self.templates_dir = Path(__file__).resolve().parent.parent / "templates"

    def generate_toolchain_content(self, default_arch: str = "aarch64") -> str:
        """Returns the official QNX SDP 8.0 CMake toolchain file content."""
        tpl_path = self.templates_dir / "qnx.toolchain.cmake"
        if tpl_path.is_file():
            content = tpl_path.read_text(encoding="utf-8")
        else:
            content = (
                "# QNX SDP 8.0 CMake Toolchain\n"
                "cmake_minimum_required(VERSION 3.25)\n"
                "set(CMAKE_SYSTEM_NAME QNX)\n"
                f"set(CMAKE_SYSTEM_PROCESSOR {default_arch})\n"
                "set(CMAKE_C_COMPILER $ENV{QNX_HOST}/usr/bin/qcc)\n"
                "set(CMAKE_CXX_COMPILER $ENV{QNX_HOST}/usr/bin/q++)\n"
            )
        return content

    def generate_presets_content(self) -> str:
        """Returns the CMakePresets.json content for QNX 8.0."""
        tpl_path = self.templates_dir / "CMakePresets.json"
        if tpl_path.is_file():
            return tpl_path.read_text(encoding="utf-8")
        return "{}"

    def generate_common_mk_content(self, app_name: Optional[str] = None) -> str:
        """Returns standard QNX recursive make common.mk content."""
        tpl_path = self.templates_dir / "common.mk"
        if tpl_path.is_file():
            content = tpl_path.read_text(encoding="utf-8")
            if app_name:
                content = content.replace("NAME=app", f"NAME={app_name}")
            return content
        return "include $(MKFILES_ROOT)/qtargets.mk\n"

    def suggest_cmakelists_patches(self, original_content: str) -> Optional[str]:
        """
        Suggests clean QNX 8.0 adaptations for an existing CMakeLists.txt:
        - Replaces hardcoded -lpthread, -ldl, -lrt with platform conditions.
        - Removes deprecated -lang-c++ flags.
        """
        patched = original_content

        # Remove -lang-c++
        patched = re.sub(r"\s*-lang-c\+\+", "", patched)

        # Remove hardcoded -march=native
        patched = re.sub(r"\s*-march=native", "", patched)

        # Guard target_link_libraries for pthread / dl / rt if present
        # Replace simple 'target_link_libraries(target pthread dl)' with QNX check
        lines = patched.splitlines()
        new_lines: List[str] = []
        modified = False

        for line in lines:
            if re.search(r"target_link_libraries\s*\(.*?\b(pthread|dl|rt)\b", line):
                modified = True
                new_lines.append("# QNX Sentinel: On QNX, pthread, dl, and rt are built into libc.so")
                new_lines.append("if(NOT CMAKE_SYSTEM_NAME STREQUAL \"QNX\")")
                new_lines.append(f"  {line.strip()}")
                clean_line = re.sub(r"\b(pthread|dl|rt)\b", "", line).strip()
                # Clean up any trailing paren or spaces
                clean_line = re.sub(r"\s+\)", ")", clean_line)
                new_lines.append("else()")
                new_lines.append(f"  {clean_line}")
                new_lines.append("endif()")
            else:
                new_lines.append(line)

        patched = "\n".join(new_lines) + ("\n" if original_content.endswith("\n") else "")
        return patched if patched != original_content else None

    def plan_changes(self, structure: ProjectStructure) -> Dict[str, Dict[str, str]]:
        """
        Calculates all proposed file changes, returning a dict of:
        {
          "filename": {
             "action": "CREATE" or "MODIFY",
             "path": full_path,
             "proposed_content": content,
             "diff": unified_diff_str,
             "reason": explanation
          }
        }
        """
        plans: Dict[str, Dict[str, str]] = {}
        has_cmake = "CMake" in structure.build_systems
        has_qnx_make = "QNX_Recursive_Make" in structure.build_systems
        has_gnu_make = "GNU_Make" in structure.build_systems

        # 1. Propose qnx.toolchain.cmake if missing for CMake projects
        toolchain_path = self.project_dir / DEFAULT_TOOLCHAIN_FILENAME
        if has_cmake and not toolchain_path.exists():
            content = self.generate_toolchain_content()
            plans[DEFAULT_TOOLCHAIN_FILENAME] = {
                "action": "CREATE",
                "path": str(toolchain_path),
                "proposed_content": content,
                "diff": self._compute_diff("", content, DEFAULT_TOOLCHAIN_FILENAME),
                "reason": "Provides official QNX SDP 8.0 cross-compilation settings for CMake (qcc/q++, AArch64/x86_64, sysroot).",
            }

        # 2. Propose CMakePresets.json if missing for CMake projects
        presets_path = self.project_dir / DEFAULT_PRESETS_FILENAME
        if has_cmake and not presets_path.exists():
            content = self.generate_presets_content()
            plans[DEFAULT_PRESETS_FILENAME] = {
                "action": "CREATE",
                "path": str(presets_path),
                "proposed_content": content,
                "diff": self._compute_diff("", content, DEFAULT_PRESETS_FILENAME),
                "reason": "Standardizes reproducible QNX build profiles for Debug/Release on AArch64 and x86_64.",
            }

        # 3. Propose common.mk if using makefile without QNX recursive system
        common_mk_path = self.project_dir / DEFAULT_COMMON_MK_FILENAME
        if has_gnu_make and not common_mk_path.exists():
            content = self.generate_common_mk_content(structure.project_name)
            plans[DEFAULT_COMMON_MK_FILENAME] = {
                "action": "CREATE",
                "path": str(common_mk_path),
                "proposed_content": content,
                "diff": self._compute_diff("", content, DEFAULT_COMMON_MK_FILENAME),
                "reason": "Integrates project into standard QNX recursive make architecture.",
            }

        # 4. Check existing CMakeLists.txt for modifications
        cmakelists_path = self.project_dir / "CMakeLists.txt"
        if cmakelists_path.is_file():
            try:
                orig_content = cmakelists_path.read_text(encoding="utf-8")
                patched = self.suggest_cmakelists_patches(orig_content)
                if patched:
                    plans["CMakeLists.txt"] = {
                        "action": "MODIFY",
                        "path": str(cmakelists_path),
                        "proposed_content": patched,
                        "diff": self._compute_diff(orig_content, patched, "CMakeLists.txt"),
                        "reason": "Removes deprecated -lang-c++ / -march=native and makes Linux libraries (pthread, dl, rt) conditional for QNX libc.",
                    }
            except Exception:
                pass

        return plans

    def apply_plan(self, plans: Dict[str, Dict[str, str]], confirmed: bool = False) -> List[str]:
        """
        Applies proposed changes to disk ONLY if confirmed is True.
        Returns a list of messages describing applied actions.
        """
        if not confirmed:
            raise PermissionError(
                "Execution aborted: User confirmation is strictly required to apply configuration changes."
            )

        applied: List[str] = []
        for name, item in plans.items():
            dest = Path(item["path"])
            dest.write_text(item["proposed_content"], encoding="utf-8")
            applied.append(f"{item['action']}: {dest.name} -> {item['reason']}")

        return applied

    def _compute_diff(self, original: str, modified: str, filename: str) -> str:
        orig_lines = original.splitlines(keepends=True)
        mod_lines = modified.splitlines(keepends=True)
        diff = difflib.unified_diff(
            orig_lines,
            mod_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
            n=3,
        )
        return "".join(diff)
