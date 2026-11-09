/**
 * QNX 8.0 Sensor Service - Implementation
 * Compliant with verified QNX SDP 8.0 Neutrino RTOS microkernel APIs.
 */

#include "sensor_mgr.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <time.h>
#include <pthread.h>
#include <sched.h>
#include <sys/netmgr.h>

#ifdef __QNX__
#include <sys/slog2.h>
static slog2_buffer_set_config_t slog_config;
static slog2_buffer_t slog_buf;
#endif

static int g_chid = -1;
static int g_coid = -1;
static timer_t g_timer_id;

int sensor_mgr_init(void) {
#ifdef __QNX__
    // Register QNX slog2 buffer
    slog_config.num_buffers = 1;
    slog_config.verbosity_level = SLOG2_INFO;
    slog_config.buffer_set_name = "sensor_mgr";
    slog_config.buffer_config[0].buffer_name = "default";
    slog_config.buffer_config[0].num_pages = 2;
    slog2_register(&slog_config, &slog_buf, 0);
    slog2c(slog_buf, 0, SLOG2_INFO, "Initializing QNX 8.0 Sensor Manager");
#endif

    // Create Neutrino message channel
    g_chid = ChannelCreate(0);
    if (g_chid == -1) {
        return -1;
    }

    // Connect to own channel for delivering periodic timer pulses
    g_coid = ConnectAttach(ND_LOCAL_NODE, 0, g_chid, _NTO_SIDE_CHANNEL, 0);
    if (g_coid == -1) {
        ChannelDestroy(g_chid);
        return -1;
    }

    // Configure periodic POSIX timer targeting QNX Pulse
    struct sigevent event;
    SIGEV_PULSE_INIT(&event, g_coid, SIGEV_PULSE_PRIO_INHERIT, PULSE_CODE_TIMER, 0);

    if (timer_create(CLOCK_MONOTONIC, &event, &g_timer_id) == -1) {
        ConnectDetach(g_coid);
        ChannelDestroy(g_chid);
        return -1;
    }

    struct itimerspec itime;
    itime.it_value.tv_sec = 0;
    itime.it_value.tv_nsec = 100000000; // 100ms
    itime.it_interval = itime.it_value;
    timer_settime(g_timer_id, 0, &itime, NULL);

    return g_chid;
}

int sensor_mgr_process_event(int chid) {
    struct _pulse pulse;
    int rcvid = MsgReceive(chid, &pulse, sizeof(pulse), NULL);

    if (rcvid == 0) {
        // Received a microkernel pulse
        if (pulse.code == PULSE_CODE_TIMER) {
            // Periodic sample event triggered deterministically
            return 1;
        } else if (pulse.code == PULSE_CODE_SHUTDOWN) {
            return 0;
        }
    } else if (rcvid > 0) {
        // Standard synchronous message received; reply back
        MsgReply(rcvid, EOK, NULL, 0);
    }
    return 1;
}

void sensor_mgr_cleanup(void) {
    if (g_timer_id != 0) {
        timer_delete(g_timer_id);
    }
    if (g_coid != -1) {
        ConnectDetach(g_coid);
    }
    if (g_chid != -1) {
        ChannelDestroy(g_chid);
    }
}
