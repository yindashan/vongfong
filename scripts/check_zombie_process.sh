#!/bin/bash                                                                     
PROCESSOR_MAN=` ps -ef | grep defunct | grep -v grep | wc -l`
echo "HOST_STATUS | ZOMBIE_PROCESS=$PROCESSOR_MAN"
