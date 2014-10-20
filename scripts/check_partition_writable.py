#!/opt/virtual_python/bin/python                                                     
# -*- coding: utf-8 -*-

import os
import sys

def error_handler(error_message=""):
    print error_message
    print "HOST_STATUS | SYS_PARTITION_WRITABLE=-1"
    sys.exit(1)

def success_handler(writable):
    print "HOST_STATUS | SYS_PARTITION_WRITABLE=%d" % (writable)
    sys.exit(0)

def get_disk_partition():                                                
    return_list = []
    pd = []
    try:
        f = open("/proc/filesystems", "r")
        for line in f:
            if not line.startswith("nodev"):
                d = line.strip()
                if d not in ['iso9660']:
                    pd.append(d)
        f.close()
        pd.append('nfs')
        pd.append('nfs4')
        
        f = open('/etc/mtab', "r")
        for line in f:
            if line.startswith('none'):
                continue
            tmp = line.strip().split()
            ft = tmp[2]
            if ft not in pd:
                continue
            return_list.append(tmp[1])
        f.close()
    except:
        error_handler("从 /proc/filesystems 或 /etc/mtab 获取分区表失败")
    if not return_list:
        error_handler("从 /proc/filesystems 或 /etc/mtab 获取分区表失败")
    return return_list

def check_partition_writable():
    partition_list = get_disk_partition()
    for partition in partition_list:
        filename = os.path.join(partition, ".check_partition_writable.tmp")
        try:
            f = open(filename, "w")
            f.write("check_partition_wriable")
            f.close()
            os.remove(filename)
        except:
            return 0
    return 1

if __name__ == "__main__":
    writable = check_partition_writable()
    success_handler(writable)
