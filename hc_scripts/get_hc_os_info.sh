#!/bin/bash                                                                     
OS_TYPE=`lsb_release -i | awk '{print $3}'`
OS_BIT=`getconf LONG_BIT`
OS_VERSION=`lsb_release -r | awk '{print $2}'`

echo "OS_TYPE=$OS_TYPE,OS_BIT=$OS_BIT,OS_VERSION=$OS_VERSION | 操作系统类型:$OS_TYPE,位数:$OS_BIT,版本:$OS_VERSION"

