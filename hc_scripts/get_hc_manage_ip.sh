#!/bin/bash                                                                     
MANAGE_IP=`ipmitool lan print 2> /dev/null | grep "IP Address" | grep -v "IP Address Source" | awk '{print $4}'`

echo "MANAGE_IP=$MANAGE_IP | 管理IP:$MANAGE_IP" 
