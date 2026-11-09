/**
 * Legacy Linux Telemetry Worker
 * Uses GNU pthread_yield, strndupa, and Linux sysfs /sys/class.
 */

#include "telemetry.h"
#include <iostream>
#include <fstream>
#include <cstring>
#include <pthread.h>
#include <unistd.h>

void run_telemetry_worker(void) {
    // Non-portable GNU strndupa stack allocation
    const char* raw_tag = "VEHICLE_CAN_BUS_DATA";
    char* tag_copy = strndupa(raw_tag, 10);
    std::cout << "Processing tag: " << tag_copy << std::endl;

    // Non-portable Linux sysfs assumption
    std::ifstream iface_file("/sys/class/net/eth0/address");
    if (iface_file.is_open()) {
        std::string mac;
        iface_file >> mac;
        std::cout << "Hardware MAC: " << mac << std::endl;
    }

    // Non-standard GNU extension pthread_yield
    pthread_yield();
}
