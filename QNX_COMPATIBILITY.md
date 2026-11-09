# QNX SDP 8.0 Compatibility & Portability Reference Guide

This document provides a comprehensive technical reference for software engineers porting C/C++ applications from Linux or Windows to **QNX Software Development Platform (SDP) 8.0** (Neutrino RTOS).

---

## 1. QNX SDP 8.0 Architecture Overview

QNX Neutrino is a true microkernel operating system. Unlike monolithic kernels (Linux, Windows) where networking, filesystems, and device drivers execute in privileged supervisor space:
- **Only core services** (threads, message passing, signals, timers, memory management) execute within `procnto` / `procnto-smp`.
- **Filesystems, drivers, and network stacks** run as user-space **Resource Managers** communicating via high-performance synchronous message passing.
- POSIX 1003.1 is the primary user-space programming model, augmented by QNX Neutrino microkernel primitives.

---

## 2. Verified Compiler & Toolchain Changes in QNX 8.0

| Feature | QNX SDP 7.1 / Legacy | QNX SDP 8.0 (Current) | Porting Note |
|---|---|---|---|
| **Baseline Compiler** | GCC 8.3 / GCC 5.4 | **GCC 12.2.0** and **LLVM / Clang** | Modern C++17/C++20 baseline supported natively. |
| **Compiler Driver** | `qcc` (C & C++) | **`qcc` (C)** and **`q++` (C++)** | Legacy `-lang-c++` flag is deprecated; use `q++` or `-x c++`. |
| **C++ Standard Library** | Dinkumware / GNU `libstdc++` | **LLVM `libc++`** (Default) | Defaults to `-stdlib=libc++`. GNU `libstdc++` available via `-stdlib=libstdc++`. |
| **Target Architectures** | ARMv7, AArch64, x86, x86_64 | **AArch64 (`aarch64le`)**, **x86_64** | Focus on 64-bit multi-core SMP and HPC SoCs. |
| **Threading (`libpthread`)** | Linked via `libc` | Built into **`libc.so`** | Do NOT pass `-lpthread`. Linker will emit warning or fail if stub missing. |
| **Dynamic Loading (`libdl`)** | Separate or alias | Built into **`libc.so`** | Functions `dlopen`, `dlsym`, `dlclose` are in standard `libc.so`. |
| **Realtime Clocks (`librt`)** | Separate or alias | Built into **`libc.so`** | POSIX `timer_*` and `clock_*` functions are in standard `libc.so`. |

---

## 3. Detailed Linux-to-QNX Portability Matrix

### 3.1 Event Multiplexing: `epoll` vs QNX Primitives

- **Linux Model:** `epoll_create1()`, `epoll_ctl()`, `epoll_wait()`. Relies on kernel-managed readiness states.
- **QNX Status:** **Unsupported.** `<sys/epoll.h>` does not exist.
- **Porting Strategy:**
  1. **Standard POSIX:** For socket or pipe file descriptors, replace with standard POSIX `poll()` or `select()`. QNX optimizes `poll()` through its internal `ionotify()` subsystem.
  2. **Native Microkernel Performance:** Use `ionotify()` with a `sigevent` configured to deliver a **Neutrino Pulse** (`SIGEV_PULSE_INIT`). Multiplex all pulses and messages into a single blocking `MsgReceive()` loop.

```c
// QNX 8.0 Native Event Loop using POSIX poll():
#include <poll.h>

struct pollfd fds[2];
fds[0].fd = sock_fd;
fds[0].events = POLLIN | POLLERR;
fds[1].fd = pipe_fd;
fds[1].events = POLLIN;

int ready = poll(fds, 2, 1000); // 1000ms timeout
if (ready > 0) {
    if (fds[0].revents & POLLIN) { /* Read socket */ }
    if (fds[1].revents & POLLIN) { /* Read pipe */ }
}
```

---

### 3.2 Timers: `timerfd` vs QNX POSIX Timers & Pulses

- **Linux Model:** `timerfd_create()`, `timerfd_settime()`. Exposes timers as file descriptors to feed into `epoll`.
- **QNX Status:** **Unsupported.** `<sys/timerfd.h>` does not exist.
- **QNX Native Equivalent:** Use standard POSIX `timer_create(CLOCK_MONOTONIC, &event, &timer_id)` coupled to a `SIGEV_PULSE`.

```c
// QNX 8.0 High-Performance Periodic Timer with Pulse:
#include <sys/neutrino.h>
#include <sys/netmgr.h>
#include <time.h>

#define PULSE_CODE_TICK _PULSE_CODE_MINAVAIL

int chid = ChannelCreate(0);
int coid = ConnectAttach(ND_LOCAL_NODE, 0, chid, _NTO_SIDE_CHANNEL, 0);

struct sigevent event;
SIGEV_PULSE_INIT(&event, coid, SIGEV_PULSE_PRIO_INHERIT, PULSE_CODE_TICK, 0);

timer_t timer_id;
timer_create(CLOCK_MONOTONIC, &event, &timer_id);

struct itimerspec itime;
itime.it_value.tv_sec = 0;
itime.it_value.tv_nsec = 50000000; // 50ms initial
itime.it_interval = itime.it_value; // 50ms periodic
timer_settime(timer_id, 0, &itime, NULL);

// In event loop:
struct _pulse pulse;
MsgReceive(chid, &pulse, sizeof(pulse), NULL);
if (pulse.code == PULSE_CODE_TICK) {
    // 50ms tick executed deterministically!
}
```

---

### 3.3 Inter-Thread Signaling: `eventfd` vs QNX Pulses

- **Linux Model:** `eventfd(0, EFD_NONBLOCK)`. Uses a kernel counter mapped to a file descriptor.
- **QNX Status:** **Unsupported.** `<sys/eventfd.h>` does not exist.
- **QNX Equivalents:**
  1. **Drop-in replacement:** POSIX standard `pipe(wake_fds)` or `socketpair()`. Writing 1 byte wakes the reader waiting in `poll()`.
  2. **Microkernel native:** `MsgSendPulse(coid, priority, code, value)`. Delivers an 8-byte payload with zero dynamic memory allocation and immediate priority inheritance.

---

### 3.4 Process Control: `prctl()` vs QNX `ThreadCtl()` & `pthread_setname_np()`

- **Linux Model:** `prctl(PR_SET_NAME, ...)` or setting process security bits.
- **QNX Status:** **Unsupported.** `<sys/prctl.h>` does not exist.
- **QNX Equivalents:**
  - **Thread Naming:** `pthread_setname_np(pthread_self(), "WorkerThread")`.
  - **Thread Control / Affinity:** `ThreadCtl(_NTO_TCTL_RUNMASK, (void*)(uintptr_t)mask)`.
  - **Process Abilities:** `procmgr_ability()`.

---

### 3.5 GNU C Extensions vs POSIX Compliance

| GNU C Extension | Standard POSIX / QNX 8.0 Replacement | Header Required |
|---|---|---|
| `pthread_yield()` | `sched_yield()` | `<sched.h>` |
| `get_current_dir_name()` | `getcwd(buf, sizeof(buf))` | `<unistd.h>` |
| `strndupa(s, n)` | `strndup(s, n)` followed by `free()` | `<string.h>`, `<stdlib.h>` |
| `cpu_set_t` / `CPU_SET` | `ThreadCtl(_NTO_TCTL_RUNMASK, ...)` | `<sys/neutrino.h>` |

---

### 3.6 Filesystem & Paths

- **Binary Self Path:**
  - *Linux:* Reading `/proc/self/exe`.
  - *QNX:* The global pointer `extern char *_cmdname;` points to the program invocation name. Alternatively, inspect `argv[0]` or query `/proc/<pid>/as`.
- **Shared Memory:**
  - *Linux:* Creates objects in `/dev/shm`.
  - *QNX:* POSIX shared memory resides under `/dev/shmem`. Always use `shm_open("/name", O_RDWR | O_CREAT, 0660)` rather than hardcoding filesystem paths.
- **Hardware/Device Access:**
  - *Linux:* Navigating `/sys/class/...` or `/sys/devices/...`.
  - *QNX:* Sysfs does not exist. Hardware interfaces register as Resource Managers under `/dev/` (e.g. `/dev/ser1`, `/dev/spi0`, `/dev/i2c0`). Access devices using `open()` and `devctl()`.

---

### 3.7 Real-Time Thread Scheduling & Priorities

- **Linux Model:** Nice values ranging from `-20` (highest) to `+19` (lowest).
- **QNX Neutrino Model:** Real-time deterministic priorities ranging from `1` (lowest) to `255` (highest).
  - Priority `10`: Default non-critical application thread.
  - Priority `11-20`: Normal priority tasks.
  - Priority `21-63`: Time-critical embedded control loops.
  - Priority `64-255`: Interrupt handlers and system drivers.
- **Configuration API:**
  ```c
  #include <pthread.h>
  #include <sched.h>

  struct sched_param param;
  param.sched_priority = 25; // Real-time priority
  pthread_setschedparam(pthread_self(), SCHED_RR, &param);
  ```

---

### 3.8 Logging: `printf` vs QNX `slog2`

- Standard `printf` or `fprintf(stderr, ...)` causes blocking I/O on headless systems and is unsuitable for safety-critical daemons.
- QNX SDP 8.0 provides `slog2` (System Logger 2): lock-free, zero-allocation ring buffers with configurable verbosity levels (`SLOG2_DEBUG1`, `SLOG2_INFO`, `SLOG2_WARNING`, `SLOG2_ERROR`).
- Logs are inspected in real time using the host or target utility `slog2info`.

---

## 4. Official QNX Documentation References

- **QNX SDP 8.0 Overview:** [QNX Neutrino RTOS Documentation](https://www.qnx.com/developers/docs/8.0/)
- **Compiler Driver (`qcc`):** [qcc Utilities Reference](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/q/qcc.html)
- **CMake Integration Guide:** [CMake Support for QNX](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/cmake_support.html)
- **Porting from Linux:** [Porting Linux Applications Guide](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/porting_linux.html)
- **Inter-Process Communication:** [QNX IPC Architecture](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.prog/topic/ipc.html)
- **slog2 Logging Subsystem:** [slog2 API Reference](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/s/slog2.html)
- **Target Quick Start with QEMU:** [Target Emulation Guide](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.getting_started/topic/qemu_target.html)
