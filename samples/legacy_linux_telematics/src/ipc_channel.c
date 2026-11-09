/**
 * Legacy Linux IPC Channel
 * Uses Linux eventfd and System V shared memory (Non-portable to QNX 8.0).
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/eventfd.h>
#include <sys/ipc.h>
#include <sys/shm.h>

int create_ipc_event(void) {
    // Non-portable Linux eventfd
    int efd = eventfd(0, EFD_NONBLOCK);
    if (efd == -1) {
        perror("eventfd");
        return -1;
    }

    uint64_t val = 1;
    write(efd, &val, sizeof(val));

    // Legacy System V IPC
    key_t key = 0x1234;
    int shmid = shmget(key, 1024, 0666 | IPC_CREAT);
    if (shmid != -1) {
        shmctl(shmid, IPC_RMID, NULL);
    }

    close(efd);
    return 0;
}
