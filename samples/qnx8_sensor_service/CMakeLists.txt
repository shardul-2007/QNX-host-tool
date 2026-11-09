cmake_minimum_required(VERSION 3.25)
project(qnx8_sensor_service C)

set(CMAKE_C_STANDARD 11)

include_directories(src)

add_executable(qnx8_sensor_service
    src/main.c
    src/sensor_mgr.c
)

# On QNX Neutrino, threads and timers are built into libc.so
if(NOT CMAKE_SYSTEM_NAME STREQUAL "QNX")
    find_package(Threads REQUIRED)
    target_link_libraries(qnx8_sensor_service PRIVATE Threads::Threads)
endif()

enable_testing()
add_executable(test_sensor tests/test_sensor.c)
add_test(NAME SensorUnitTest COMMAND test_sensor)
