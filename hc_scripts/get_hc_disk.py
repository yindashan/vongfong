#!/opt/virtual_python/bin/python
# -*- coding:utf-8 -*- 

# std lib
import sys, os
import subprocess


# 执行外部命令                
def external_cmd(cmd, msg_in=''):
    try:
        proc = subprocess.Popen(cmd,
                   shell=True,
                   stdin=subprocess.PIPE,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                  )
        stdout_value, stderr_value = proc.communicate(msg_in)
        return stdout_value, stderr_value
    except ValueError, err:
        return None, None
    except IOError, err:
        return None, None


def main():
    command = "fdisk -l |grep 'Disk' |awk -F , '{print $1}' | sed 's/Disk identifier.*//g' | sed '/^$/d'"
    stdout_value, stderr_value = external_cmd(command)
    #print type(stdout_value), stdout_value
    disk_list = stdout_value.split('\n')
    # 硬盘总大小
    HD_TOTAL = 0.0
    for i in range(0, len(disk_list)-1):
        HD_TOTAL += float(disk_list[i].split()[2])
    HD_DETAIL = ';'.join(disk_list)
    print "HD_TOTAL=%0.2f | 文件系统:%s"%(HD_TOTAL, HD_DETAIL)
    
#-------------------------------start----------------------------------
if __name__ == '__main__':
    main()
    
    
    
    