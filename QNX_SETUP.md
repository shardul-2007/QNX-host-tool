# QNX SDP 8.0 Official Environment & Target Setup Guide

This document provides a comprehensive, verified guide for installing, configuring, and verifying **QNX Software Development Platform (SDP) 8.0** across host operating systems (Windows, Linux, macOS), setting up the **QNX Toolkit for Visual Studio Code**, and configuring **QEMU virtual targets via `mkqnximage`**.

---

## 1. Obtaining & Installing QNX SDP 8.0

QNX SDP 8.0 is distributed through the **QNX Software Center (QSC)** under commercial, academic, or non-commercial (QNX Everywhere) licensing.

### Step 1: Install QNX Software Center (QSC)
1. Download the QSC installer from the official [myQNX Developer Portal](https://www.qnx.com/download/).
2. Run the installer:
   - **Windows:** `qsc-setup.exe` (installs to `C:\Program Files\QNX Software Center\qsc.exe`)
   - **Linux:** `./qsc-setup.bin` (installs to `~/qnx/qsc/qsc`)
3. Launch QSC and sign in with your myQNX credentials.

### Step 2: Install QNX SDP 8.0 Packages
Within QSC, select and install:
- **QNX Software Development Platform 8.0** (`com.qnx.sdp.800`)
- **QNX Quick Start Target Image (QSTI) for QEMU** (`com.qnx.qnx800.quickstart.qemu`)
- Target architectures:
  - `com.qnx.qnx800.target.aarch64` (64-bit ARM)
  - `com.qnx.qnx800.target.x86_64` (64-bit x86)

Default installation directory:
- **Windows:** `C:\qnx800`
- **Linux / macOS:** `~/qnx800`

---

## 2. Setting Up Host Environment Variables

The QNX build infrastructure requires specific environment variables to direct compilers, linkers, and CMake to target sysroots.

### On Windows (Command Prompt / PowerShell)
Invoke the environment batch script generated during installation:

```cmd
call C:\qnx800\qnxsdp-env.bat
```

To persist in PowerShell profile (`$PROFILE`):
```powershell
# Add to profile:
$env:QNX_HOST = "C:\qnx800\host\win64\x86_64"
$env:QNX_TARGET = "C:\qnx800\target\qnx"
$env:QNX_CONFIGURATION = "$env:USERPROFILE\.qnx"
$env:Path = "$env:QNX_HOST\usr\bin;$env:Path"
```

### On Linux / macOS
Source the environment script in your shell session:

```bash
source ~/qnx800/qnxsdp-env.sh
```

To persist in `~/.bashrc` or `~/.zshrc`:
```bash
if [ -f ~/qnx800/qnxsdp-env.sh ]; then
    source ~/qnx800/qnxsdp-env.sh
fi
```

### Environment Verification
Test that `qcc` is recognized and points to QNX SDP 8.0:

```bash
qcc -V
```

Expected output:
```text
qcc: GCC 12.2.0 (QNX Neutrino 8.0.0)
```

---

## 3. QNX Toolkit for Visual Studio Code Setup

The official **QNX Toolkit for VS Code** provides language intelligence, remote target debugging via `qconn`, and CMake presets integration.

### Step 1: Install the Extension
1. Open VS Code.
2. Press `Ctrl+P` (or `Cmd+P` on macOS) and run:
   ```text
   ext install blackberry.qnx-toolkit
   ```

### Step 2: Configure Workspace Settings (`.vscode/settings.json`)
Point the extension to your active QNX SDP path:

```json
{
  "qnx.sdpPath": "C:/qnx800",
  "qnx.targetArchitecture": "aarch64le",
  "cmake.configureOnOpen": true
}
```

### Step 3: C/C++ IntelliSense Configuration (`.vscode/c_cpp_properties.json`)
To enable accurate autocompletion and prevent false IntelliSense warnings when including `<sys/neutrino.h>` or `<sys/slog2.h>`:

```json
{
  "configurations": [
    {
      "name": "QNX SDP 8.0 AArch64",
      "includePath": [
        "${workspaceFolder}/**",
        "${env:QNX_TARGET}/usr/include"
      ],
      "defines": [
        "__QNX__",
        "__QNXNTO__",
        "__ARM_ARCH_8A__"
      ],
      "compilerPath": "${env:QNX_HOST}/usr/bin/qcc",
      "cStandard": "c11",
      "cppStandard": "c++17",
      "intelliSenseMode": "linux-clang-arm64"
    }
  ],
  "version": 4
}
```

---

## 4. Configuring QEMU Virtual Targets with `mkqnximage`

QNX SDP 8.0 introduces the **`mkqnximage`** CLI utility, which automates creating and running virtual machine target images inside QEMU.

### Step 1: Generate the Target Image
Specify your desired target architecture (`aarch64le` or `x86_64`):

```bash
mkqnximage --type=qemu --hostname=qnxmachine --arch='aarch64le'
```

### Step 2: Boot the Target in QEMU
Launch the virtual machine in headless or console mode:

```bash
mkqnximage --run
```

QEMU boots the QNX Neutrino microkernel (`procnto-smp`) with virtio networking.

### Step 3: Obtain the Target IP Address
In another host terminal:

```bash
mkqnximage --getip
```

Expected output:
```text
127.0.0.1:2222
```

### Step 4: Connect via SSH
```bash
ssh -p 2222 qnxuser@127.0.0.1
```

Once connected, run:
```bash
uname -a
pidin
slog2info
```

---

## 5. Connecting Physical Hardware Targets

For developers targeting production silicon (Raspberry Pi 4, NXP i.MX8, Renesas R-Car, Texas Instruments Jacinto 7, or x86 SBCs):

1. **Board Support Package (BSP):** Download the target-specific BSP from QSC.
2. **Boot Image (IFS):** Generate the Image Filesystem (`ifs-*.bin`) using `mkifs`.
3. **Flash Image:** Write to an SD card, eMMC, or boot via TFTP/NFS over Ethernet.
4. **Remote Debugging Daemon (`qconn`):**
   Ensure `qconn` is started in your `/etc/rc.local` or target boot script:
   ```bash
   qconn port=8000
   ```
5. **Configuring Environment in QNX Sentinel:**
   ```bash
   export QNX_TARGET_IP="192.168.1.150"
   export QNX_TARGET_SSH_PORT=22
   export QNX_TARGET_ARCH="aarch64le"
   ```
   QNX Sentinel's Target Assistant will automatically detect and communicate with this physical target.

---

## 6. How QNX Sentinel Integrates with Your Setup

QNX Sentinel audits your active environment in real time:

```bash
python -m qnx_sentinel.cli audit
```

If any component is missing or misconfigured, Sentinel will diagnose:
- Missing `QNX_HOST` or `QNX_TARGET`.
- Missing compiler binary `qcc`.
- Missing target sysroots (`aarch64le`, `x86_64`).
- Missing QEMU or `mkqnximage`.

And when developing on a machine without hardware or SDP licenses, Sentinel seamlessly runs in **Host Simulation Mode**, allowing you to validate code, generate CMake toolchain files, and diagnose compiler errors without blockers!
