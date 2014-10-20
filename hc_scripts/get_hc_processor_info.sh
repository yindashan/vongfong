#!/bin/bash                                                                     
PROCESSOR_MANUFACTURER=`dmidecode -s processor-manufacturer | head -1| sed -e 's/[ ]*$//g'`
PROCESSOR_TYPE=`dmidecode -s processor-version | head -1| sed -e 's/[ ]*$//'| xargs echo`
# physical core
# 物理核数
PROCESSOR_CORES=`cat /proc/cpuinfo | grep "core id"|sort|uniq|wc -l`
PROCESSOR_NUMBER=`cat /proc/cpuinfo |grep "physical id"|sort |uniq|wc -l`


echo "PROCESSOR_MANUFACTURER=$PROCESSOR_MANUFACTURER,PROCESSOR_TYPE=$PROCESSOR_TYPE,PROCESSOR_CORES=$PROCESSOR_CORES, PROCESSOR_NUMBER=$PROCESSOR_NUMBER | 处理器制造商:$PROCESSOR_MANUFACTURER,型号:$PROCESSOR_TYPE,物理核数:$PROCESSOR_CORES,个数:$PROCESSOR_NUMBER"


