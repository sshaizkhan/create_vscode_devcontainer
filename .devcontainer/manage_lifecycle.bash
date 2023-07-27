#!/bin/bash
lifecycle_node=$1; shift
transition=$1; shift

source /home/bot/.bashrc

YELLOW='\033[1;33m'
GREEN='\033[1;32m'
RED='\033[1;91m'
RESETCOLOUR='\033[0m'

echo -e "\nros2 lifecycle set ${lifecycle_node} ${transition}"

result=$(ros2 lifecycle set ${lifecycle_node} ${transition} 2>&1)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}${result}${RESETCOLOUR}"
else
    echo -e "${RED}${result}${RESETCOLOUR}"
fi
