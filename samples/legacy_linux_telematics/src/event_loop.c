/**
 * Legacy Linux Event Loop
 * Uses Linux-specific epoll and timerfd APIs (Non-portable to QNX 8.0).
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/epoll.h>
#include <sys/timerfd.h>
#include <time.h>

#define MAX_EVENTS 16

int init_event_loop(void) {
    // Non-portable Linux epoll
    int epoll_fd = epoll_create1(0);
    if (epoll_fd == -1) {
        perror("epoll_create1");
        return -1;
    }

    // Non-portable Linux timerfd
    int tfd = timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK);
    if (tfd == -1) {
        close(epoll_fd);
        return -1;
    }

    struct itimerspec new_value;
    new_value.it_interval.tv_sec = 1;
    new_value.it_interval.tv_nsec = 0;
    new_value.it_value.tv_sec = 1;
    new_value.it_value.tv_nsec = 0;
    timerfd_settime(tfd, 0, &new_value, NULL);

    struct epoll_event ev;
    ev.events = EPOLLIN;
    ev.data.fd = tfd;
    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, tfd, &ev);

    struct epoll_event events[MAX_EVENTS];
    int nfds = epoll_wait(epoll_fd, events, MAX_EVENTS, 500);
    printf("Processed %d events from epoll\n", nfds);

    close(tfd);
    close(epoll_fd);
    return 0;
}
