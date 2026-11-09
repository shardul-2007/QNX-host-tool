"""
QNX Sentinel - Core Configuration & Official Knowledge References
Houses verified QNX SDP 8.0 parameters, standard documentation links,
target profiles, and analysis settings.
"""

from typing import Dict, List, Set

# Official QNX 8.0 Documentation Anchors
QNX_DOC_BASE = "https://www.qnx.com/developers/docs/8.0"
DOC_LINKS = {
    "quickstart": f"{QNX_DOC_BASE}/com.qnx.doc.neutrino.getting_started/topic/overview.html",
    "compiler_qcc": f"{QNX_DOC_BASE}/com.qnx.doc.neutrino.utilities/topic/q/qcc.html",
    "compiler_options": f"{QNX_DOC_BASE}/com.qnx.doc.neutrino.utilities/topic/q/qcc_options.html",
    "cmake_integration": f"{QNX_DOC_BASE}/com.qnx.doc.neutrino.prog/topic/cmake_support.html",
    "porting_guide": f"{QNX_DOC_BASE}/com.qnx.doc.neutrino.prog/topic/porting_linux.html",
    "microkernel_ipc": f"{QNX_DOC_BASE}/com.qnx.doc.neutrino.prog/topic/ipc.html",
    "pulses_timers": f"{QNX_DOC_BASE}/com.qnx.doc.neutrino.prog/topic/timer_pulses.html",
    "slog2_logging": f"{QNX_DOC_BASE}/com.qnx.doc.neutrino.lib_ref/topic/s/slog2.html",
    "qemu_qsti": f"{QNX_DOC_BASE}/com.qnx.doc.neutrino.getting_started/topic/qemu_target.html",
    "thread_scheduling": f"{QNX_DOC_BASE}/com.qnx.doc.neutrino.prog/topic/threads.html",
}

# Verified QNX 8.0 Supported Architectures
SUPPORTED_ARCHITECTURES: List[str] = [
    "aarch64le",  # ARMv8 64-bit Little Endian (Primary embedded/automotive)
    "x86_64",     # x86 64-bit Little Endian (Host simulation, HPC, hypervisors)
]

# Verified QNX 8.0 Compiler Variants for qcc -V
SUPPORTED_VARIANTS: Dict[str, str] = {
    "gcc_ntoaarch64le": "GCC 12.2.0 for QNX Neutrino AArch64 Little-Endian",
    "gcc_ntox86_64": "GCC 12.2.0 for QNX Neutrino x86_64",
    "llvm_ntoaarch64le": "LLVM/Clang for QNX Neutrino AArch64 Little-Endian",
    "llvm_ntox86_64": "LLVM/Clang for QNX Neutrino x86_64",
}

# Standard Source & Header Extensions
C_EXTENSIONS: Set[str] = {".c"}
CPP_EXTENSIONS: Set[str] = {".cpp", ".cc", ".cxx", ".C"}
HEADER_EXTENSIONS: Set[str] = {".h", ".hpp", ".hxx", ".hh"}
BUILD_FILENAMES: Set[str] = {
    "CMakeLists.txt",
    "Makefile",
    "makefile",
    "common.mk",
    "CMakePresets.json",
    "CMakeUserPresets.json",
    ".qnx-project.json",
}

# Ignored directory names during scanning
DEFAULT_EXCLUDE_DIRS: Set[str] = {
    ".git",
    ".svn",
    ".hg",
    "build",
    "build_qnx",
    "cmake-build-debug",
    "cmake-build-release",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".vscode",
    ".idea",
}

# Default Toolchain Filenames
DEFAULT_TOOLCHAIN_FILENAME = "qnx.toolchain.cmake"
DEFAULT_PRESETS_FILENAME = "CMakePresets.json"
DEFAULT_COMMON_MK_FILENAME = "common.mk"
