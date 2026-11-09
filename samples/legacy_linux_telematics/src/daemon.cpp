/**
 * Legacy Linux Daemon
 * Uses Linux prctl, glibc get_current_dir_name, and /proc/self/exe.
 */

#include "telemetry.h"
#include <iostream>
#include <cstring>
#include <unistd.h>
#include <sys/prctl.h>

int main(int argc, char* argv[]) {
    // Non-portable Linux prctl
    prctl(PR_SET_NAME, "TelemetryDaemon", 0, 0, 0);

    // Non-standard GNU extension
    char* cwd = get_current_dir_name();
    if (cwd) {
        std::cout << "Running daemon from: " << cwd << std::endl;
        free(cwd);
    }

    // Non-portable Linux /proc/self/exe assumption
    char exe_path[256];
    ssize_t len = readlink("/proc/self/exe", exe_path, sizeof(exe_path) - 1);
    if (len != -1) {
        exe_path[len] = '\0';
        std::cout << "Self binary: " << exe_path << std::endl;
    }

    init_event_loop();
    create_ipc_event();
    run_telemetry_worker();

    return 0;
}
