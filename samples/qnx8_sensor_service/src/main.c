/**
 * QNX 8.0 Sensor Service - Entry Point
 */

#include "sensor_mgr.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
#include <sched.h>

int main(int argc, char *argv[]) {
    // Configure deterministic RTOS thread priority
    struct sched_param param;
    param.sched_priority = 21; // QNX real-time priority (normal default is 10)
    pthread_setschedparam(pthread_self(), SCHED_RR, &param);

    int chid = sensor_mgr_init();
    if (chid == -1) {
        return EXIT_FAILURE;
    }

    int samples_to_run = 3;
    while (samples_to_run > 0) {
        int running = sensor_mgr_process_event(chid);
        if (!running) break;
        samples_to_run--;
    }

    sensor_mgr_cleanup();
    return EXIT_SUCCESS;
}
