#ifndef TELEMETRY_H
#define TELEMETRY_H

#ifdef __cplusplus
extern "C" {
#endif

int init_event_loop(void);
int create_ipc_event(void);
void run_telemetry_worker(void);

#ifdef __cplusplus
}
#endif

#endif /* TELEMETRY_H */
