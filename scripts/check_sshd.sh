#!/bin/bash  
IsRuning(){
       ps -ef |grep -v grep | grep ssh > /dev/null 2>&1
} 
IsRuning
if [ $? -eq 0 ];then
        echo "HOST_STATUS | SYS_SSHD=1"
else
        echo "HOST_STATUS | SYS_SSHD=0"
fi 
