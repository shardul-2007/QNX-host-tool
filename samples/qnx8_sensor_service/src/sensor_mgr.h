/**
 * QNX 8.0 Sensor Service - Architecture Header
 * Demonstrates idiomatic QNX Neutrino microkernel IPC, pulses, and slog2 logging.
 */

#ifndef SENSOR_MGR_H
#define SENSOR_MGR_H

#include <stdint.h>
#include <sys/neutrino.h>

#define SENSOR_CHANNEL_NAME "/dev/qnx_sensor"
#define PULSE_CODE_TIMER    _PULSE_CODE_MINAVAIL
#define PULSE_CODE_SHUTDOWN (_PULSE_CODE_MINAVAIL + 1)

typedef struct {
    uint32_t sensor_id;
    float temperature;
    float pressure;
    uint64_t timestamp_ns;
} sensor_reading_t;

typedef struct {
    int16_t msg_type;
    sensor_reading_t payload;
} sensor_msg_t;

int sensor_mgr_init(void);
int sensor_mgr_process_event(int chid);
void sensor_mgr_cleanup(void);

#endif /* SENSOR_MGR_H */
