"""
QNX Sentinel - Diagnostic Knowledge Base
Houses verified diagnostic patterns, root-cause explanations, and remediation
recipes mapped to official QNX SDP 8.0 documentation.
"""

from typing import Dict, List
from qnx_sentinel.core.config import DOC_LINKS

KNOWLEDGE_BASE: List[Dict] = [
    {
        "id": "KB-EPOLL-MISSING",
        "pattern": r"(?:sys/epoll\.h: No such file or directory|undefined reference to `?epoll_create)",
        "category": "LINUX_SPECIFIC_SYSCALL",
        "title": "Linux epoll API Missing on QNX",
        "explanation": (
            "QNX Neutrino RTOS is a microkernel operating system and does not implement the Linux-specific "
            "epoll kernel event subsystem. Attempting to include <sys/epoll.h> or call epoll_create/epoll_ctl/epoll_wait "
            "will fail at compile or link time."
        ),
        "remediation_steps": [
            "For standard TCP/UDP socket or pipe multiplexing, replace epoll with standard POSIX poll() or select().",
            "For event-driven microkernel servers, use QNX ionotify() coupled to a Neutrino Pulse, and process events in a MsgReceive() loop.",
            "If using third-party asynchronous libraries (e.g. libuv, boost.asio), configure the build to select the POSIX poll backend.",
        ],
        "suggested_diff": (
            "--- a/event_loop.c\n"
            "+++ b/event_loop.c\n"
            "-#include <sys/epoll.h>\n"
            "+#include <poll.h>\n"
            "-\n"
            "-int epfd = epoll_create1(0);\n"
            "-epoll_ctl(epfd, EPOLL_CTL_ADD, sock, &ev);\n"
            "-epoll_wait(epfd, events, 10, -1);\n"
            "+\n"
            "+struct pollfd fds[1];\n"
            "+fds[0].fd = sock;\n"
            "+fds[0].events = POLLIN;\n"
            "+int ret = poll(fds, 1, -1);\n"
        ),
        "doc_link": DOC_LINKS["porting_guide"],
    },
    {
        "id": "KB-TIMERFD-MISSING",
        "pattern": r"(?:sys/timerfd\.h: No such file or directory|undefined reference to `?timerfd_create)",
        "category": "LINUX_SPECIFIC_SYSCALL",
        "title": "Linux timerfd API Missing on QNX",
        "explanation": (
            "Linux timerfd presents timer expirations as readable file descriptors. "
            "QNX SDP 8.0 does not provide timerfd in its standard C library."
        ),
        "remediation_steps": [
            "Use standard POSIX timer_create() with CLOCK_MONOTONIC.",
            "Configure the sigevent structure to deliver a QNX Pulse (SIGEV_PULSE_INIT) directly to your server channel.",
            "If a file descriptor is strictly required by an event loop, connect the timer to a pipe() or socketpair().",
        ],
        "suggested_diff": (
            "--- a/timer.c\n"
            "+++ b/timer.c\n"
            "-#include <sys/timerfd.h>\n"
            "+#include <time.h>\n"
            "+#include <sys/neutrino.h>\n"
            "+\n"
            "-int tfd = timerfd_create(CLOCK_MONOTONIC, 0);\n"
            "+struct sigevent event;\n"
            "+SIGEV_PULSE_INIT(&event, coid, SIGEV_PULSE_PRIO_INHERIT, CODE_TIMER, 0);\n"
            "+timer_t timer_id;\n"
            "+timer_create(CLOCK_MONOTONIC, &event, &timer_id);\n"
        ),
        "doc_link": DOC_LINKS["pulses_timers"],
    },
    {
        "id": "KB-PRCTL-MISSING",
        "pattern": r"(?:sys/prctl\.h: No such file or directory|undefined reference to `?prctl)",
        "category": "LINUX_SPECIFIC_SYSCALL",
        "title": "Linux prctl Interface Missing on QNX",
        "explanation": (
            "<sys/prctl.h> is a Linux-only header for kernel process control operations. "
            "It is not part of POSIX or QNX Neutrino RTOS."
        ),
        "remediation_steps": [
            "For setting thread names (PR_SET_NAME), use pthread_setname_np(pthread_self(), name).",
            "For process security or core dump controls, use QNX ThreadCtl() or procmgr_ability().",
        ],
        "suggested_diff": (
            "--- a/process.c\n"
            "+++ b/process.c\n"
            "-#include <sys/prctl.h>\n"
            "-prctl(PR_SET_NAME, \"Worker\", 0, 0, 0);\n"
            "+#include <pthread.h>\n"
            "+pthread_setname_np(pthread_self(), \"Worker\");\n"
        ),
        "doc_link": DOC_LINKS["thread_scheduling"],
    },
    {
        "id": "KB-LIBPTHREAD-LINK",
        "pattern": r"(?:cannot find -lpthread|ld: error: unable to find library -lpthread)",
        "category": "COMPILER_TOOLCHAIN",
        "title": "Redundant -lpthread Flag on QNX",
        "explanation": (
            "On QNX SDP 8.0, all POSIX thread functionality (pthread_create, pthread_mutex_*, etc.) "
            "is implemented directly inside the core C library (libc.so). A separate libpthread.so does not exist."
        ),
        "remediation_steps": [
            "Remove -lpthread from target_link_libraries() or LDFLAGS when building for QNX.",
            "In CMake, guard thread linking with: if(NOT CMAKE_SYSTEM_NAME STREQUAL \"QNX\")",
            "QNX libc.so automatically provides all standard POSIX threading primitives without separate flags.",
        ],
        "suggested_diff": (
            "--- a/CMakeLists.txt\n"
            "+++ b/CMakeLists.txt\n"
            "-target_link_libraries(my_app PRIVATE pthread)\n"
            "+if(NOT CMAKE_SYSTEM_NAME STREQUAL \"QNX\")\n"
            "+  target_link_libraries(my_app PRIVATE pthread)\n"
            "+endif()\n"
        ),
        "doc_link": DOC_LINKS["compiler_qcc"],
    },
    {
        "id": "KB-LANG-CPP-DEPRECATED",
        "pattern": r"(?:warning:.*-lang-c\+\+ is deprecated|error: unrecognized command-line option '-lang-c\+\+')",
        "category": "COMPILER_TOOLCHAIN",
        "title": "Deprecated -lang-c++ Compiler Option in QNX 8.0",
        "explanation": (
            "The flag '-lang-c++' was used in older QNX SDP releases to instruct qcc to treat C files as C++. "
            "In QNX SDP 8.0 with GCC 12 and Clang, this flag is deprecated and should not be passed to qcc."
        ),
        "remediation_steps": [
            "Invoke 'q++' instead of 'qcc' when compiling C++ code.",
            "In CMake toolchain files, set CMAKE_CXX_COMPILER to '${QNX_HOST}/usr/bin/q++'.",
        ],
        "suggested_diff": (
            "--- a/CMakeLists.txt\n"
            "+++ b/CMakeLists.txt\n"
            "-set(CMAKE_CXX_FLAGS \"${CMAKE_CXX_FLAGS} -lang-c++\")\n"
        ),
        "doc_link": DOC_LINKS["compiler_options"],
    },
    {
        "id": "KB-PTHREAD-YIELD",
        "pattern": r"(?:'pthread_yield' was not declared in this scope|implicit declaration of function `?pthread_yield)",
        "category": "GNU_EXTENSION",
        "title": "Non-Standard GNU pthread_yield() Call",
        "explanation": (
            "pthread_yield() is a legacy GNU non-standard function. Standard POSIX defines sched_yield() "
            "in <sched.h>, which QNX strictly follows."
        ),
        "remediation_steps": [
            "Include <sched.h>.",
            "Replace pthread_yield() with sched_yield().",
        ],
        "suggested_diff": (
            "--- a/worker.c\n"
            "+++ b/worker.c\n"
            "-#include <pthread.h>\n"
            "-pthread_yield();\n"
            "+#include <sched.h>\n"
            "+sched_yield();\n"
        ),
        "doc_link": DOC_LINKS["porting_guide"],
    },
]
