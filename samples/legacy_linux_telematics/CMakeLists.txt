cmake_minimum_required(VERSION 3.20)
project(legacy_linux_telematics C CXX)

set(CMAKE_CXX_STANDARD 17)

# Deprecated QNX flag and host-specific flag
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -lang-c++ -march=native -Wall")

include_directories(include)

add_executable(telematics_daemon
    src/daemon.cpp
    src/telemetry.cpp
    src/event_loop.c
    src/ipc_channel.c
)

# Non-portable explicit host libraries
target_link_libraries(telematics_daemon PRIVATE pthread dl rt)
