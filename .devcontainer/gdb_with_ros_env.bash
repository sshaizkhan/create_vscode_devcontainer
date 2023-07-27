#!/bin/bash

# Source our environment
source /application_name/install/setup.bash

# Run gdb, forwarding all args through
/usr/bin/gdb ${@}
