from .base_rule import BaseRule
from .linux_syscalls import (
    EpollUsageRule,
    TimerfdUsageRule,
    EventfdUsageRule,
    SignalfdInotifyRule,
)
from .gnu_extensions import (
    PthreadYieldRule,
    GetCurrentDirNameRule,
    StrndupaRule,
    LinuxCpuAffinityRule,
)
from .filesystem_proc import (
    ProcSelfExeRule,
    DevShmPathRule,
    LinuxSysfsRule,
)
from .process_threads import (
    PrctlRule,
    MultithreadedForkRule,
    LinuxNicePriorityRule,
)
from .ipc_primitives import SysVIPCRule
from .compiler_flags import (
    DeprecatedLangCppRule,
    RedundantHostLibrariesRule,
)
from .qnx_idioms import Slog2AdoptionRule

DEFAULT_RULES = [
    # Linux Syscalls
    EpollUsageRule(),
    TimerfdUsageRule(),
    EventfdUsageRule(),
    SignalfdInotifyRule(),
    # GNU Extensions
    PthreadYieldRule(),
    GetCurrentDirNameRule(),
    StrndupaRule(),
    LinuxCpuAffinityRule(),
    # Filesystem & Procfs
    ProcSelfExeRule(),
    DevShmPathRule(),
    LinuxSysfsRule(),
    # Process & Threads
    PrctlRule(),
    MultithreadedForkRule(),
    LinuxNicePriorityRule(),
    # IPC
    SysVIPCRule(),
    # Compiler Flags
    DeprecatedLangCppRule(),
    RedundantHostLibrariesRule(),
    # QNX Idioms
    Slog2AdoptionRule(),
]

__all__ = [
    "BaseRule",
    "DEFAULT_RULES",
    "EpollUsageRule",
    "TimerfdUsageRule",
    "EventfdUsageRule",
    "SignalfdInotifyRule",
    "PthreadYieldRule",
    "GetCurrentDirNameRule",
    "StrndupaRule",
    "LinuxCpuAffinityRule",
    "ProcSelfExeRule",
    "DevShmPathRule",
    "LinuxSysfsRule",
    "PrctlRule",
    "MultithreadedForkRule",
    "LinuxNicePriorityRule",
    "SysVIPCRule",
    "DeprecatedLangCppRule",
    "RedundantHostLibrariesRule",
    "Slog2AdoptionRule",
]
