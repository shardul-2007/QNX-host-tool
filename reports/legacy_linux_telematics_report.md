# QNX Sentinel — Analysis Report: `legacy_linux_telematics`

> **Analysis Timestamp:** `2026-11-09T16:35:10.217732+00:00`  
> **Project Root:** `C:\Users\shard\Downloads\QNX host tool\samples\legacy_linux_telematics`  
> **QNX 8.0 Readiness Index:** **`0.0/100`** (Grade: **`F`**)

## 1. Executive Summary

| Metric | Value |
|---|---|
| **Overall Readiness Score** | **0.0/100 (F)** |
| **Total Source Files** | 6 (2 C, 2 C++, 1 Headers) |
| **Lines of Code** | 136 LOC |
| **Detected Build Systems** | CMake |
| **Critical Compatibility Blockers** | **16** |
| **Portability Warnings** | 11 |
| **Microkernel Best Practice Tips** | 0 |
| **Informational Notes** | 3 |

## 2. Host QNX SDP 8.0 Environment

- **SDP Detected:** `NO`
- **Status:** Running in Host-Static Analysis & Simulation Mode
- **Activation Command:** `call C:\qnx800\qnxsdp-env.bat`
- **QEMU Emulator:** `NOT DETECTED`
- **mkqnximage Utility:** `NOT DETECTED`

## 3. Build Configuration Status

The following standard QNX 8.0 build files are missing from the project:

- [ ] **Missing qnx.toolchain.cmake (Required for cross-compiling with QNX SDP 8.0 qcc)**
- [ ] **Missing CMakePresets.json (Recommended for reproducible QNX 8.0 AArch64/x86_64 build profiles)**

> Use `qnx-sentinel build-assist` to automatically generate verified `qnx.toolchain.cmake` and `CMakePresets.json` templates.

## 4. Portability & Compatibility Findings

| # | Severity | Rule ID | Title | Location |
|---|---|---|---|---|
| 1 | **`CRITICAL`** | `QNX-030-PRCTL` | Linux prctl() Interface Usage | `src\daemon.cpp:10` |
| 2 | **`CRITICAL`** | `QNX-030-PRCTL` | Linux prctl() Interface Usage | `src\daemon.cpp:14` |
| 3 | **`CRITICAL`** | `QNX-001-EPOLL` | Non-Portable Linux epoll API Usage | `src\event_loop.c:9` |
| 4 | **`CRITICAL`** | `QNX-002-TIMERFD` | Non-Portable Linux timerfd API Usage | `src\event_loop.c:10` |
| 5 | **`CRITICAL`** | `QNX-001-EPOLL` | Non-Portable Linux epoll API Usage | `src\event_loop.c:17` |
| 6 | **`CRITICAL`** | `QNX-001-EPOLL` | Non-Portable Linux epoll API Usage | `src\event_loop.c:19` |
| 7 | **`CRITICAL`** | `QNX-002-TIMERFD` | Non-Portable Linux timerfd API Usage | `src\event_loop.c:24` |
| 8 | **`CRITICAL`** | `QNX-002-TIMERFD` | Non-Portable Linux timerfd API Usage | `src\event_loop.c:35` |
| 9 | **`CRITICAL`** | `QNX-001-EPOLL` | Non-Portable Linux epoll API Usage | `src\event_loop.c:40` |
| 10 | **`CRITICAL`** | `QNX-001-EPOLL` | Non-Portable Linux epoll API Usage | `src\event_loop.c:43` |
| 11 | **`CRITICAL`** | `QNX-003-EVENTFD` | Non-Portable Linux eventfd API Usage | `src\ipc_channel.c:3` |
| 12 | **`CRITICAL`** | `QNX-003-EVENTFD` | Non-Portable Linux eventfd API Usage | `src\ipc_channel.c:9` |
| 13 | **`CRITICAL`** | `QNX-003-EVENTFD` | Non-Portable Linux eventfd API Usage | `src\ipc_channel.c:14` |
| 14 | **`CRITICAL`** | `QNX-003-EVENTFD` | Non-Portable Linux eventfd API Usage | `src\ipc_channel.c:15` |
| 15 | **`CRITICAL`** | `QNX-003-EVENTFD` | Non-Portable Linux eventfd API Usage | `src\ipc_channel.c:17` |
| 16 | **`CRITICAL`** | `QNX-022-SYSFS` | Linux sysfs (/sys/...) Path Dependency | `src\telemetry.cpp:20` |
| 17 | **`WARNING`** | `QNX-050-LANG-CPP` | Deprecated Compiler Flag '-lang-c++' in QNX 8.0 | `CMakeLists.txt:7` |
| 18 | **`WARNING`** | `QNX-011-GET-CURRENT-DIR-NAME` | Non-Standard GNU get_current_dir_name() Call | `src\daemon.cpp:17` |
| 19 | **`WARNING`** | `QNX-020-PROC-SELF-EXE` | Linux /proc/self/exe Symlink Dependency | `src\daemon.cpp:25` |
| 20 | **`WARNING`** | `QNX-040-SYSV-IPC` | Legacy System V IPC Usage (shmget / semget / msgget) | `src\ipc_channel.c:10` |
| 21 | **`WARNING`** | `QNX-040-SYSV-IPC` | Legacy System V IPC Usage (shmget / semget / msgget) | `src\ipc_channel.c:11` |
| 22 | **`WARNING`** | `QNX-040-SYSV-IPC` | Legacy System V IPC Usage (shmget / semget / msgget) | `src\ipc_channel.c:26` |
| 23 | **`WARNING`** | `QNX-040-SYSV-IPC` | Legacy System V IPC Usage (shmget / semget / msgget) | `src\ipc_channel.c:28` |
| 24 | **`WARNING`** | `QNX-012-STRNDUPA` | Unsafe GNU strndupa() / strdupa() Macro | `src\telemetry.cpp:3` |
| 25 | **`WARNING`** | `QNX-012-STRNDUPA` | Unsafe GNU strndupa() / strdupa() Macro | `src\telemetry.cpp:14` |
| 26 | **`WARNING`** | `QNX-012-STRNDUPA` | Unsafe GNU strndupa() / strdupa() Macro | `src\telemetry.cpp:16` |
| 27 | **`WARNING`** | `QNX-010-PTHREAD-YIELD` | Non-Standard GNU pthread_yield() Call | `src\telemetry.cpp:28` |
| 28 | **`INFO`** | `QNX-051-HOST-LIBRARIES` | Redundant Host Library Linking (-lpthread, -ldl, -lrt) | `CMakeLists.txt:19` |
| 29 | **`INFO`** | `QNX-051-HOST-LIBRARIES` | Redundant Host Library Linking (-lpthread, -ldl, -lrt) | `CMakeLists.txt:19` |
| 30 | **`INFO`** | `QNX-051-HOST-LIBRARIES` | Redundant Host Library Linking (-lpthread, -ldl, -lrt) | `CMakeLists.txt:19` |

### Detailed Issue Analysis & Remediation

#### Finding #1: [CRITICAL] Linux prctl() Interface Usage (`QNX-030-PRCTL`)

- **File:** `src\daemon.cpp` (Line 10)
- **Category:** `THREADING_SCHEDULING`
- **Description:** Detected Linux '#include <sys/prctl.h>'.
- **Rationale:** Thread naming on QNX is performed via pthread_setname_np(). Process attributes and security capabilities are configured via ThreadCtl() or procmgr_* APIs.
- **Offending Code:**
  ```c
  #include <sys/prctl.h>
  ```
- **Remediation:** For thread naming, use pthread_setname_np(pthread_self(), "name"). For process control, use QNX ThreadCtl().
- **Recommended QNX 8.0 Implementation:**
  ```c
// Portable thread naming for QNX SDP 8.0:
#include <pthread.h>
pthread_setname_np(pthread_self(), "WorkerThread");
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/threads.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/threads.html)

#### Finding #2: [CRITICAL] Linux prctl() Interface Usage (`QNX-030-PRCTL`)

- **File:** `src\daemon.cpp` (Line 14)
- **Category:** `THREADING_SCHEDULING`
- **Description:** Detected Linux 'prctl('.
- **Rationale:** Thread naming on QNX is performed via pthread_setname_np(). Process attributes and security capabilities are configured via ThreadCtl() or procmgr_* APIs.
- **Offending Code:**
  ```c
  prctl(PR_SET_NAME, "TelemetryDaemon", 0, 0, 0);
  ```
- **Remediation:** For thread naming, use pthread_setname_np(pthread_self(), "name"). For process control, use QNX ThreadCtl().
- **Recommended QNX 8.0 Implementation:**
  ```c
// Portable thread naming for QNX SDP 8.0:
#include <pthread.h>
pthread_setname_np(pthread_self(), "WorkerThread");
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/threads.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/threads.html)

#### Finding #3: [CRITICAL] Non-Portable Linux epoll API Usage (`QNX-001-EPOLL`)

- **File:** `src\event_loop.c` (Line 9)
- **Category:** `LINUX_SPECIFIC_SYSCALL`
- **Description:** Detected '#include <sys/epoll.h>' which is unsupported on QNX SDP 8.0.
- **Rationale:** QNX Neutrino is a microkernel operating system that multiplexes events using ionotify(), standard POSIX poll()/select(), or native Neutrino Pulses/Channels.
- **Offending Code:**
  ```c
  #include <sys/epoll.h>
  ```
- **Remediation:** Replace epoll with standard POSIX poll() or select() for socket loops. For high-performance native events, use QNX ionotify() with a sigevent pulse, allowing the event loop to block on MsgReceive().
- **Recommended QNX 8.0 Implementation:**
  ```c
// QNX 8.0 Porting: Standard POSIX poll() fallback
#include <poll.h>
struct pollfd fds[2];
fds[0].fd = socket_fd;
fds[0].events = POLLIN | POLLERR;
int ready = poll(fds, 1, timeout_ms);
if (ready > 0 && (fds[0].revents & POLLIN)) { /* process */ }
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html)

#### Finding #4: [CRITICAL] Non-Portable Linux timerfd API Usage (`QNX-002-TIMERFD`)

- **File:** `src\event_loop.c` (Line 10)
- **Category:** `LINUX_SPECIFIC_SYSCALL`
- **Description:** Detected Linux '#include <sys/timerfd.h>'. Use POSIX timer_create() with SIGEV_PULSE.
- **Rationale:** QNX Neutrino timing architecture delivers real-time notifications via standard POSIX timers (timer_create) coupled to QNX Pulses (SIGEV_PULSE) directly into an IPC Channel.
- **Offending Code:**
  ```c
  #include <sys/timerfd.h>
  ```
- **Remediation:** Use standard POSIX timer_create() with SIGEV_PULSE delivered to a QNX channel. If a file descriptor is strictly required by third-party abstractions, couple a POSIX timer to a pipe() or socketpair().
- **Recommended QNX 8.0 Implementation:**
  ```c
// QNX 8.0: High-performance POSIX timer with Pulse
#include <sys/netmgr.h>
#include <sys/neutrino.h>
#include <time.h>

struct sigevent event;
SIGEV_PULSE_INIT(&event, coid, priority, CODE_TIMER, 0);
timer_t timer_id;
timer_create(CLOCK_MONOTONIC, &event, &timer_id);
struct itimerspec itime = {{1, 0}, {1, 0}}; // 1s periodic
timer_settime(timer_id, 0, &itime, NULL);
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/timer_pulses.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/timer_pulses.html)

#### Finding #5: [CRITICAL] Non-Portable Linux epoll API Usage (`QNX-001-EPOLL`)

- **File:** `src\event_loop.c` (Line 17)
- **Category:** `LINUX_SPECIFIC_SYSCALL`
- **Description:** Detected 'epoll_create1' which is unsupported on QNX SDP 8.0.
- **Rationale:** QNX Neutrino is a microkernel operating system that multiplexes events using ionotify(), standard POSIX poll()/select(), or native Neutrino Pulses/Channels.
- **Offending Code:**
  ```c
  int epoll_fd = epoll_create1(0);
  ```
- **Remediation:** Replace epoll with standard POSIX poll() or select() for socket loops. For high-performance native events, use QNX ionotify() with a sigevent pulse, allowing the event loop to block on MsgReceive().
- **Recommended QNX 8.0 Implementation:**
  ```c
// QNX 8.0 Porting: Standard POSIX poll() fallback
#include <poll.h>
struct pollfd fds[2];
fds[0].fd = socket_fd;
fds[0].events = POLLIN | POLLERR;
int ready = poll(fds, 1, timeout_ms);
if (ready > 0 && (fds[0].revents & POLLIN)) { /* process */ }
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html)

#### Finding #6: [CRITICAL] Non-Portable Linux epoll API Usage (`QNX-001-EPOLL`)

- **File:** `src\event_loop.c` (Line 19)
- **Category:** `LINUX_SPECIFIC_SYSCALL`
- **Description:** Detected 'epoll_create1' which is unsupported on QNX SDP 8.0.
- **Rationale:** QNX Neutrino is a microkernel operating system that multiplexes events using ionotify(), standard POSIX poll()/select(), or native Neutrino Pulses/Channels.
- **Offending Code:**
  ```c
  perror("epoll_create1");
  ```
- **Remediation:** Replace epoll with standard POSIX poll() or select() for socket loops. For high-performance native events, use QNX ionotify() with a sigevent pulse, allowing the event loop to block on MsgReceive().
- **Recommended QNX 8.0 Implementation:**
  ```c
// QNX 8.0 Porting: Standard POSIX poll() fallback
#include <poll.h>
struct pollfd fds[2];
fds[0].fd = socket_fd;
fds[0].events = POLLIN | POLLERR;
int ready = poll(fds, 1, timeout_ms);
if (ready > 0 && (fds[0].revents & POLLIN)) { /* process */ }
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html)

#### Finding #7: [CRITICAL] Non-Portable Linux timerfd API Usage (`QNX-002-TIMERFD`)

- **File:** `src\event_loop.c` (Line 24)
- **Category:** `LINUX_SPECIFIC_SYSCALL`
- **Description:** Detected Linux 'timerfd_create'. Use POSIX timer_create() with SIGEV_PULSE.
- **Rationale:** QNX Neutrino timing architecture delivers real-time notifications via standard POSIX timers (timer_create) coupled to QNX Pulses (SIGEV_PULSE) directly into an IPC Channel.
- **Offending Code:**
  ```c
  int tfd = timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK);
  ```
- **Remediation:** Use standard POSIX timer_create() with SIGEV_PULSE delivered to a QNX channel. If a file descriptor is strictly required by third-party abstractions, couple a POSIX timer to a pipe() or socketpair().
- **Recommended QNX 8.0 Implementation:**
  ```c
// QNX 8.0: High-performance POSIX timer with Pulse
#include <sys/netmgr.h>
#include <sys/neutrino.h>
#include <time.h>

struct sigevent event;
SIGEV_PULSE_INIT(&event, coid, priority, CODE_TIMER, 0);
timer_t timer_id;
timer_create(CLOCK_MONOTONIC, &event, &timer_id);
struct itimerspec itime = {{1, 0}, {1, 0}}; // 1s periodic
timer_settime(timer_id, 0, &itime, NULL);
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/timer_pulses.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/timer_pulses.html)

#### Finding #8: [CRITICAL] Non-Portable Linux timerfd API Usage (`QNX-002-TIMERFD`)

- **File:** `src\event_loop.c` (Line 35)
- **Category:** `LINUX_SPECIFIC_SYSCALL`
- **Description:** Detected Linux 'timerfd_settime'. Use POSIX timer_create() with SIGEV_PULSE.
- **Rationale:** QNX Neutrino timing architecture delivers real-time notifications via standard POSIX timers (timer_create) coupled to QNX Pulses (SIGEV_PULSE) directly into an IPC Channel.
- **Offending Code:**
  ```c
  timerfd_settime(tfd, 0, &new_value, NULL);
  ```
- **Remediation:** Use standard POSIX timer_create() with SIGEV_PULSE delivered to a QNX channel. If a file descriptor is strictly required by third-party abstractions, couple a POSIX timer to a pipe() or socketpair().
- **Recommended QNX 8.0 Implementation:**
  ```c
// QNX 8.0: High-performance POSIX timer with Pulse
#include <sys/netmgr.h>
#include <sys/neutrino.h>
#include <time.h>

struct sigevent event;
SIGEV_PULSE_INIT(&event, coid, priority, CODE_TIMER, 0);
timer_t timer_id;
timer_create(CLOCK_MONOTONIC, &event, &timer_id);
struct itimerspec itime = {{1, 0}, {1, 0}}; // 1s periodic
timer_settime(timer_id, 0, &itime, NULL);
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/timer_pulses.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/timer_pulses.html)

#### Finding #9: [CRITICAL] Non-Portable Linux epoll API Usage (`QNX-001-EPOLL`)

- **File:** `src\event_loop.c` (Line 40)
- **Category:** `LINUX_SPECIFIC_SYSCALL`
- **Description:** Detected 'epoll_ctl' which is unsupported on QNX SDP 8.0.
- **Rationale:** QNX Neutrino is a microkernel operating system that multiplexes events using ionotify(), standard POSIX poll()/select(), or native Neutrino Pulses/Channels.
- **Offending Code:**
  ```c
  epoll_ctl(epoll_fd, EPOLL_CTL_ADD, tfd, &ev);
  ```
- **Remediation:** Replace epoll with standard POSIX poll() or select() for socket loops. For high-performance native events, use QNX ionotify() with a sigevent pulse, allowing the event loop to block on MsgReceive().
- **Recommended QNX 8.0 Implementation:**
  ```c
// QNX 8.0 Porting: Standard POSIX poll() fallback
#include <poll.h>
struct pollfd fds[2];
fds[0].fd = socket_fd;
fds[0].events = POLLIN | POLLERR;
int ready = poll(fds, 1, timeout_ms);
if (ready > 0 && (fds[0].revents & POLLIN)) { /* process */ }
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html)

#### Finding #10: [CRITICAL] Non-Portable Linux epoll API Usage (`QNX-001-EPOLL`)

- **File:** `src\event_loop.c` (Line 43)
- **Category:** `LINUX_SPECIFIC_SYSCALL`
- **Description:** Detected 'epoll_wait' which is unsupported on QNX SDP 8.0.
- **Rationale:** QNX Neutrino is a microkernel operating system that multiplexes events using ionotify(), standard POSIX poll()/select(), or native Neutrino Pulses/Channels.
- **Offending Code:**
  ```c
  int nfds = epoll_wait(epoll_fd, events, MAX_EVENTS, 500);
  ```
- **Remediation:** Replace epoll with standard POSIX poll() or select() for socket loops. For high-performance native events, use QNX ionotify() with a sigevent pulse, allowing the event loop to block on MsgReceive().
- **Recommended QNX 8.0 Implementation:**
  ```c
// QNX 8.0 Porting: Standard POSIX poll() fallback
#include <poll.h>
struct pollfd fds[2];
fds[0].fd = socket_fd;
fds[0].events = POLLIN | POLLERR;
int ready = poll(fds, 1, timeout_ms);
if (ready > 0 && (fds[0].revents & POLLIN)) { /* process */ }
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html)

#### Finding #11: [CRITICAL] Non-Portable Linux eventfd API Usage (`QNX-003-EVENTFD`)

- **File:** `src\ipc_channel.c` (Line 3)
- **Category:** `LINUX_SPECIFIC_SYSCALL`
- **Description:** Detected Linux 'eventfd'. Use POSIX pipe() or QNX Pulses.
- **Rationale:** QNX Neutrino provides lightweight non-blocking 8-byte Pulses (MsgSendPulse) for inter-thread and inter-process event signaling, with zero kernel memory allocation overhead.
- **Offending Code:**
  ```c
  * Uses Linux eventfd and System V shared memory (Non-portable to QNX 8.0).
  ```
- **Remediation:** Replace eventfd with a standard POSIX pipe() or socketpair() if an event fd is needed. For native QNX services, send a Neutrino Pulse via MsgSendPulse().
- **Recommended QNX 8.0 Implementation:**
  ```c
// POSIX pipe drop-in for inter-thread wakeup on QNX:
int wake_fds[2];
pipe(wake_fds);
// Writer: write(wake_fds[1], "w", 1);
// Reader: poll() on wake_fds[0] and read() to drain.
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/ipc.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/ipc.html)

#### Finding #12: [CRITICAL] Non-Portable Linux eventfd API Usage (`QNX-003-EVENTFD`)

- **File:** `src\ipc_channel.c` (Line 9)
- **Category:** `LINUX_SPECIFIC_SYSCALL`
- **Description:** Detected Linux 'eventfd'. Use POSIX pipe() or QNX Pulses.
- **Rationale:** QNX Neutrino provides lightweight non-blocking 8-byte Pulses (MsgSendPulse) for inter-thread and inter-process event signaling, with zero kernel memory allocation overhead.
- **Offending Code:**
  ```c
  #include <sys/eventfd.h>
  ```
- **Remediation:** Replace eventfd with a standard POSIX pipe() or socketpair() if an event fd is needed. For native QNX services, send a Neutrino Pulse via MsgSendPulse().
- **Recommended QNX 8.0 Implementation:**
  ```c
// POSIX pipe drop-in for inter-thread wakeup on QNX:
int wake_fds[2];
pipe(wake_fds);
// Writer: write(wake_fds[1], "w", 1);
// Reader: poll() on wake_fds[0] and read() to drain.
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/ipc.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/ipc.html)

#### Finding #13: [CRITICAL] Non-Portable Linux eventfd API Usage (`QNX-003-EVENTFD`)

- **File:** `src\ipc_channel.c` (Line 14)
- **Category:** `LINUX_SPECIFIC_SYSCALL`
- **Description:** Detected Linux 'eventfd'. Use POSIX pipe() or QNX Pulses.
- **Rationale:** QNX Neutrino provides lightweight non-blocking 8-byte Pulses (MsgSendPulse) for inter-thread and inter-process event signaling, with zero kernel memory allocation overhead.
- **Offending Code:**
  ```c
  // Non-portable Linux eventfd
  ```
- **Remediation:** Replace eventfd with a standard POSIX pipe() or socketpair() if an event fd is needed. For native QNX services, send a Neutrino Pulse via MsgSendPulse().
- **Recommended QNX 8.0 Implementation:**
  ```c
// POSIX pipe drop-in for inter-thread wakeup on QNX:
int wake_fds[2];
pipe(wake_fds);
// Writer: write(wake_fds[1], "w", 1);
// Reader: poll() on wake_fds[0] and read() to drain.
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/ipc.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/ipc.html)

#### Finding #14: [CRITICAL] Non-Portable Linux eventfd API Usage (`QNX-003-EVENTFD`)

- **File:** `src\ipc_channel.c` (Line 15)
- **Category:** `LINUX_SPECIFIC_SYSCALL`
- **Description:** Detected Linux 'eventfd'. Use POSIX pipe() or QNX Pulses.
- **Rationale:** QNX Neutrino provides lightweight non-blocking 8-byte Pulses (MsgSendPulse) for inter-thread and inter-process event signaling, with zero kernel memory allocation overhead.
- **Offending Code:**
  ```c
  int efd = eventfd(0, EFD_NONBLOCK);
  ```
- **Remediation:** Replace eventfd with a standard POSIX pipe() or socketpair() if an event fd is needed. For native QNX services, send a Neutrino Pulse via MsgSendPulse().
- **Recommended QNX 8.0 Implementation:**
  ```c
// POSIX pipe drop-in for inter-thread wakeup on QNX:
int wake_fds[2];
pipe(wake_fds);
// Writer: write(wake_fds[1], "w", 1);
// Reader: poll() on wake_fds[0] and read() to drain.
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/ipc.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/ipc.html)

#### Finding #15: [CRITICAL] Non-Portable Linux eventfd API Usage (`QNX-003-EVENTFD`)

- **File:** `src\ipc_channel.c` (Line 17)
- **Category:** `LINUX_SPECIFIC_SYSCALL`
- **Description:** Detected Linux 'eventfd'. Use POSIX pipe() or QNX Pulses.
- **Rationale:** QNX Neutrino provides lightweight non-blocking 8-byte Pulses (MsgSendPulse) for inter-thread and inter-process event signaling, with zero kernel memory allocation overhead.
- **Offending Code:**
  ```c
  perror("eventfd");
  ```
- **Remediation:** Replace eventfd with a standard POSIX pipe() or socketpair() if an event fd is needed. For native QNX services, send a Neutrino Pulse via MsgSendPulse().
- **Recommended QNX 8.0 Implementation:**
  ```c
// POSIX pipe drop-in for inter-thread wakeup on QNX:
int wake_fds[2];
pipe(wake_fds);
// Writer: write(wake_fds[1], "w", 1);
// Reader: poll() on wake_fds[0] and read() to drain.
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/ipc.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/ipc.html)

#### Finding #16: [CRITICAL] Linux sysfs (/sys/...) Path Dependency (`QNX-022-SYSFS`)

- **File:** `src\telemetry.cpp` (Line 20)
- **Category:** `FILESYSTEM_PROCFS`
- **Description:** Detected Linux sysfs path '"/sys/class/'.
- **Rationale:** Hardware devices on QNX are managed by user-space Resource Managers under /dev/ (e.g. /dev/io-net, /dev/spi, /dev/i2c, /dev/ser1).
- **Offending Code:**
  ```c
  std::ifstream iface_file("/sys/class/net/eth0/address");
  ```
- **Remediation:** Access device drivers through their QNX resource manager nodes under /dev/ using standard open()/devctl() calls.
- **Recommended QNX 8.0 Implementation:**
  ```c
// Example QNX device control via devctl():
#include <devctl.h>
int fd = open("/dev/spi0", O_RDWR);
// devctl(fd, DCMD_..., &data, sizeof(data), NULL);
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html)

#### Finding #17: [WARNING] Deprecated Compiler Flag '-lang-c++' in QNX 8.0 (`QNX-050-LANG-CPP`)

- **File:** `CMakeLists.txt` (Line 7)
- **Category:** `COMPILER_TOOLCHAIN`
- **Description:** The '-lang-c++' flag was used in legacy QNX toolchains to force C++ compilation with qcc. In QNX SDP 8.0 with GCC 12.2 and modern Clang, this flag is deprecated and triggers warnings or errors.
- **Rationale:** Modern CMake and QNX 8.0 use 'q++' directly or standard language flags (-x c++).
- **Offending Code:**
  ```c
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -lang-c++ -march=native -Wall")
  ```
- **Remediation:** Remove '-lang-c++'. Set CMAKE_CXX_COMPILER to 'q++' in your QNX toolchain file.
- **Recommended QNX 8.0 Implementation:**
  ```c
# In qnx.toolchain.cmake:
set(CMAKE_CXX_COMPILER ${QNX_HOST}/usr/bin/q++)
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/q/qcc_options.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/q/qcc_options.html)

#### Finding #18: [WARNING] Non-Standard GNU get_current_dir_name() Call (`QNX-011-GET-CURRENT-DIR-NAME`)

- **File:** `src\daemon.cpp` (Line 17)
- **Category:** `GNU_EXTENSION`
- **Description:** get_current_dir_name() is a GNU libc extension not present in QNX SDP 8.0.
- **Rationale:** Standard POSIX getcwd(buf, size) is fully supported across all POSIX compliant operating systems.
- **Offending Code:**
  ```c
  char* cwd = get_current_dir_name();
  ```
- **Remediation:** Replace 'get_current_dir_name()' with POSIX 'getcwd(buf, sizeof(buf))'.
- **Recommended QNX 8.0 Implementation:**
  ```c
#include <unistd.h>
#include <limits.h>
char cwd[PATH_MAX];
if (getcwd(cwd, sizeof(cwd)) != NULL) { /* use cwd */ }
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html)

#### Finding #19: [WARNING] Linux /proc/self/exe Symlink Dependency (`QNX-020-PROC-SELF-EXE`)

- **File:** `src\daemon.cpp` (Line 25)
- **Category:** `FILESYSTEM_PROCFS`
- **Description:** Linux exposes the running binary path via the '/proc/self/exe' symlink. QNX procfs does not provide this symlink.
- **Rationale:** On QNX, procnto provides process memory mappings via '/proc/<pid>/as'. The executable path is commonly obtained through argv[0], the global '_cmdname' variable, or by querying dtv_entry structures.
- **Offending Code:**
  ```c
  ssize_t len = readlink("/proc/self/exe", exe_path, sizeof(exe_path) - 1);
  ```
- **Remediation:** Use QNX global '_cmdname' or pass argv[0] to realpath() instead of reading /proc/self/exe.
- **Recommended QNX 8.0 Implementation:**
  ```c
// In QNX, _cmdname points to the program invocation binary name:
extern char *_cmdname;
printf("Running binary: %s\n", _cmdname);
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html)

#### Finding #20: [WARNING] Legacy System V IPC Usage (shmget / semget / msgget) (`QNX-040-SYSV-IPC`)

- **File:** `src\ipc_channel.c` (Line 10)
- **Category:** `IPC_SYNCHRONIZATION`
- **Description:** Detected System V IPC call '#include <sys/ipc.h>'.
- **Rationale:** QNX Neutrino RTOS is optimized for synchronous message passing (MsgSend/MsgReceive), asynchronous Pulses, and POSIX memory objects (shm_open, sem_open).
- **Offending Code:**
  ```c
  #include <sys/ipc.h>
  ```
- **Remediation:** Migrate from System V IPC to POSIX IPC (shm_open, sem_open) or QNX native Channels.
- **Recommended QNX 8.0 Implementation:**
  ```c
// POSIX shared memory:
#include <sys/mman.h>
#include <fcntl.h>
int fd = shm_open("/my_shared_mem", O_RDWR | O_CREAT, 0660);
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/ipc.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/ipc.html)

#### Finding #21: [WARNING] Legacy System V IPC Usage (shmget / semget / msgget) (`QNX-040-SYSV-IPC`)

- **File:** `src\ipc_channel.c` (Line 11)
- **Category:** `IPC_SYNCHRONIZATION`
- **Description:** Detected System V IPC call '#include <sys/shm.h>'.
- **Rationale:** QNX Neutrino RTOS is optimized for synchronous message passing (MsgSend/MsgReceive), asynchronous Pulses, and POSIX memory objects (shm_open, sem_open).
- **Offending Code:**
  ```c
  #include <sys/shm.h>
  ```
- **Remediation:** Migrate from System V IPC to POSIX IPC (shm_open, sem_open) or QNX native Channels.
- **Recommended QNX 8.0 Implementation:**
  ```c
// POSIX shared memory:
#include <sys/mman.h>
#include <fcntl.h>
int fd = shm_open("/my_shared_mem", O_RDWR | O_CREAT, 0660);
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/ipc.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/ipc.html)

#### Finding #22: [WARNING] Legacy System V IPC Usage (shmget / semget / msgget) (`QNX-040-SYSV-IPC`)

- **File:** `src\ipc_channel.c` (Line 26)
- **Category:** `IPC_SYNCHRONIZATION`
- **Description:** Detected System V IPC call 'shmget'.
- **Rationale:** QNX Neutrino RTOS is optimized for synchronous message passing (MsgSend/MsgReceive), asynchronous Pulses, and POSIX memory objects (shm_open, sem_open).
- **Offending Code:**
  ```c
  int shmid = shmget(key, 1024, 0666 | IPC_CREAT);
  ```
- **Remediation:** Migrate from System V IPC to POSIX IPC (shm_open, sem_open) or QNX native Channels.
- **Recommended QNX 8.0 Implementation:**
  ```c
// POSIX shared memory:
#include <sys/mman.h>
#include <fcntl.h>
int fd = shm_open("/my_shared_mem", O_RDWR | O_CREAT, 0660);
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/ipc.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/ipc.html)

#### Finding #23: [WARNING] Legacy System V IPC Usage (shmget / semget / msgget) (`QNX-040-SYSV-IPC`)

- **File:** `src\ipc_channel.c` (Line 28)
- **Category:** `IPC_SYNCHRONIZATION`
- **Description:** Detected System V IPC call 'shmctl'.
- **Rationale:** QNX Neutrino RTOS is optimized for synchronous message passing (MsgSend/MsgReceive), asynchronous Pulses, and POSIX memory objects (shm_open, sem_open).
- **Offending Code:**
  ```c
  shmctl(shmid, IPC_RMID, NULL);
  ```
- **Remediation:** Migrate from System V IPC to POSIX IPC (shm_open, sem_open) or QNX native Channels.
- **Recommended QNX 8.0 Implementation:**
  ```c
// POSIX shared memory:
#include <sys/mman.h>
#include <fcntl.h>
int fd = shm_open("/my_shared_mem", O_RDWR | O_CREAT, 0660);
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/ipc.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/ipc.html)

#### Finding #24: [WARNING] Unsafe GNU strndupa() / strdupa() Macro (`QNX-012-STRNDUPA`)

- **File:** `src\telemetry.cpp` (Line 3)
- **Category:** `GNU_EXTENSION`
- **Description:** Detected GNU extension 'strndupa'.
- **Rationale:** QNX real-time threads typically operate with bounded stack sizes (e.g. 32KB to 256KB). Unbounded alloca() risks silent stack overflow.
- **Offending Code:**
  ```c
  * Uses GNU pthread_yield, strndupa, and Linux sysfs /sys/class.
  ```
- **Remediation:** Replace with POSIX strndup() and explicit free(), or use a bounded fixed-size stack buffer.
- **Recommended QNX 8.0 Implementation:**
  ```c
char *safe_str = strndup(src, max_len);
// ... use safe_str ...
free(safe_str);
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html)

#### Finding #25: [WARNING] Unsafe GNU strndupa() / strdupa() Macro (`QNX-012-STRNDUPA`)

- **File:** `src\telemetry.cpp` (Line 14)
- **Category:** `GNU_EXTENSION`
- **Description:** Detected GNU extension 'strndupa'.
- **Rationale:** QNX real-time threads typically operate with bounded stack sizes (e.g. 32KB to 256KB). Unbounded alloca() risks silent stack overflow.
- **Offending Code:**
  ```c
  // Non-portable GNU strndupa stack allocation
  ```
- **Remediation:** Replace with POSIX strndup() and explicit free(), or use a bounded fixed-size stack buffer.
- **Recommended QNX 8.0 Implementation:**
  ```c
char *safe_str = strndup(src, max_len);
// ... use safe_str ...
free(safe_str);
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html)

#### Finding #26: [WARNING] Unsafe GNU strndupa() / strdupa() Macro (`QNX-012-STRNDUPA`)

- **File:** `src\telemetry.cpp` (Line 16)
- **Category:** `GNU_EXTENSION`
- **Description:** Detected GNU extension 'strndupa'.
- **Rationale:** QNX real-time threads typically operate with bounded stack sizes (e.g. 32KB to 256KB). Unbounded alloca() risks silent stack overflow.
- **Offending Code:**
  ```c
  char* tag_copy = strndupa(raw_tag, 10);
  ```
- **Remediation:** Replace with POSIX strndup() and explicit free(), or use a bounded fixed-size stack buffer.
- **Recommended QNX 8.0 Implementation:**
  ```c
char *safe_str = strndup(src, max_len);
// ... use safe_str ...
free(safe_str);
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html)

#### Finding #27: [WARNING] Non-Standard GNU pthread_yield() Call (`QNX-010-PTHREAD-YIELD`)

- **File:** `src\telemetry.cpp` (Line 28)
- **Category:** `GNU_EXTENSION`
- **Description:** pthread_yield() is a deprecated GNU extension not defined in standard POSIX or QNX libc. Will cause 'implicit declaration of function' or linker error.
- **Rationale:** POSIX specifies sched_yield() defined in <sched.h>.
- **Offending Code:**
  ```c
  pthread_yield();
  ```
- **Remediation:** Replace 'pthread_yield()' with standard POSIX 'sched_yield()' and include <sched.h>.
- **Recommended QNX 8.0 Implementation:**
  ```c
#include <sched.h>
sched_yield();
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html)

#### Finding #28: [INFO] Redundant Host Library Linking (-lpthread, -ldl, -lrt) (`QNX-051-HOST-LIBRARIES`)

- **File:** `CMakeLists.txt` (Line 19)
- **Category:** `COMPILER_TOOLCHAIN`
- **Description:** Found explicit 'pthread / -lpthread'. Threads and dlopen are built into QNX libc.so.
- **Rationale:** Explicitly specifying -lpthread or -ldl is unnecessary on QNX and can lead to linker warnings or missing library errors if stub libraries are absent.
- **Offending Code:**
  ```c
  target_link_libraries(telematics_daemon PRIVATE pthread dl rt)
  ```
- **Remediation:** Wrap 'pthread / -lpthread' in platform checks or remove it when CMAKE_SYSTEM_NAME STREQUAL 'QNX'.
- **Recommended QNX 8.0 Implementation:**
  ```c
if(NOT CMAKE_SYSTEM_NAME STREQUAL "QNX")
  target_link_libraries(my_target PRIVATE pthread dl)
endif()
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/q/qcc.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/q/qcc.html)

#### Finding #29: [INFO] Redundant Host Library Linking (-lpthread, -ldl, -lrt) (`QNX-051-HOST-LIBRARIES`)

- **File:** `CMakeLists.txt` (Line 19)
- **Category:** `COMPILER_TOOLCHAIN`
- **Description:** Found explicit 'dl / -ldl'. Threads and dlopen are built into QNX libc.so.
- **Rationale:** Explicitly specifying -lpthread or -ldl is unnecessary on QNX and can lead to linker warnings or missing library errors if stub libraries are absent.
- **Offending Code:**
  ```c
  target_link_libraries(telematics_daemon PRIVATE pthread dl rt)
  ```
- **Remediation:** Wrap 'dl / -ldl' in platform checks or remove it when CMAKE_SYSTEM_NAME STREQUAL 'QNX'.
- **Recommended QNX 8.0 Implementation:**
  ```c
if(NOT CMAKE_SYSTEM_NAME STREQUAL "QNX")
  target_link_libraries(my_target PRIVATE pthread dl)
endif()
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/q/qcc.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/q/qcc.html)

#### Finding #30: [INFO] Redundant Host Library Linking (-lpthread, -ldl, -lrt) (`QNX-051-HOST-LIBRARIES`)

- **File:** `CMakeLists.txt` (Line 19)
- **Category:** `COMPILER_TOOLCHAIN`
- **Description:** Found explicit 'rt / -lrt'. Threads and dlopen are built into QNX libc.so.
- **Rationale:** Explicitly specifying -lpthread or -ldl is unnecessary on QNX and can lead to linker warnings or missing library errors if stub libraries are absent.
- **Offending Code:**
  ```c
  target_link_libraries(telematics_daemon PRIVATE pthread dl rt)
  ```
- **Remediation:** Wrap 'rt / -lrt' in platform checks or remove it when CMAKE_SYSTEM_NAME STREQUAL 'QNX'.
- **Recommended QNX 8.0 Implementation:**
  ```c
if(NOT CMAKE_SYSTEM_NAME STREQUAL "QNX")
  target_link_libraries(my_target PRIVATE pthread dl)
endif()
  ```
- **Official Documentation:** [https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/q/qcc.html](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/q/qcc.html)

## 5. Architectural Recommendations

1. Refactor epoll loops to standard POSIX poll() or leverage QNX ionotify() with pulses for event notification.
2. Convert Linux timerfd usage to POSIX timer_create() coupled with QNX SIGEV_PULSE delivered to a Neutrino channel.
3. Replace eventfd inter-thread signaling with POSIX pipes or lightweight non-blocking QNX Pulses.
4. Replace non-standard pthread_yield() calls with standard POSIX sched_yield() from <sched.h>.
5. Replace /proc/self/exe resolution with the QNX _cmdname global pointer or argv[0] path resolution.
6. Replace Linux prctl() calls with standard pthread_setname_np() for thread names and QNX ThreadCtl() for process controls.
7. Remove deprecated '-lang-c++' flags from build files; configure CMAKE_CXX_COMPILER to point to 'q++'.
8. Remove explicit '-lpthread', '-ldl', and '-lrt' from linker flags; these are integrated into QNX libc.so.

---
*Generated by QNX Sentinel — Intelligent QNX Build, Test & Compatibility Analyzer*