#!/opt/virtual_python/bin/python
# -*- coding: utf-8 -*-

import os
import sys

def error_handler(error_message=""):
    # print error_message
    print "HOST_STATUS | SYS_DISK_MAX=-1, SYS_DISK_AVG=-1"
    sys.exit(1)

def success_handler(disk_max, disk_avg):
    print "HOST_STATUS | SYS_DISK_MAX=%.0f, SYS_DISK_AVG=%.0f" % (disk_max, disk_avg)
    sys.exit(0)
	
def get_percent(use, total):
    try:
        ret = (float(use) / total) * 100
    except ZeroDivisionError:
        error_handler("除0错误")
    return ret

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

def check_disk():
    try:
        return_dict = {}
        p_list = get_disk_partition()
        for i in p_list:
            dt = os.statvfs(i)
            use = (dt.f_blocks - dt.f_bfree) * dt.f_frsize
            all = dt.f_blocks * dt.f_frsize
            #return_dict[i] = ('%.0f' % (get_percent(use, all),), ('%.2f' % (all*1.0/(1024*1000000))))
            return_dict[i] = ('%.0f' % (get_percent(use, all),), use, all)
    except:
        error_handler("检测磁盘使用率失败")
    if not return_dict:
        error_handler("检测磁盘使用率失败")
    return return_dict
	
if __name__ == "__main__":
    return_dir = check_disk()
    # 计算硬盘平均使用率
    use = 0.0
    all = 0.0
    disk_avg = 0.0
    # 计算硬盘最大使用率
    disk_max = 0.0
    for mountname in return_dir:
        if float(return_dir[mountname][0]) > disk_max:
            disk_max = float(return_dir[mountname][0])
        use += return_dir[mountname][1]
        all += return_dir[mountname][2]
    disk_avg = get_percent(use, all)
    success_handler(disk_max, disk_avg)
	
