ifndef QCONFIG
QCONFIG=qconfig.mk
endif
include $(QCONFIG)

NAME=sensor_service
EXTRA_INCVPATH += $(PROJECT_ROOT)/src
CCFLAGS += -Wall -Wextra -O2

include $(MKFILES_ROOT)/qtargets.mk
