#!/opt/virtual_python/bin/python
# -*- coding: utf-8 -*-

import sys

def error_handler(error_message=""):
    # print error_message
    print "HOST_STATUS | SYS_MEM=-1"
    sys.exit(1)

def success_handler(sys_mem):
    print "HOST_STATUS | SYS_MEM=%.1f" % sys_mem
    sys.exit(0)

def get_percent(use, total):
    try:
        ret = (float(use) / total) * 100
    except ZeroDivisionError:
        error_handler("除0错误")
    return ret

def get_phy_mem():
    try:
        f = open('/proc/meminfo', 'r')
        for line in f:
            if line.startswith('MemTotal:'):
                mem_total = int(line.split()[1])
            elif line.startswith('MemFree:'):
                mem_free = int(line.split()[1])
            elif line.startswith('Buffers:'):
                mem_buffer = int(line.split()[1])
            elif line.startswith('Cached:'):
                mem_cache = int(line.split()[1])
            else:
                continue
        f.close()
    except:
        error_handler("/proc/meminfo文件访问失败")
    return (mem_total, mem_free, mem_buffer, mem_cache)
	
def check_mem():
    try:
        total, free, buffers, cache = get_phy_mem()
        percent = get_percent(total - (free + buffers + cache), total)
    except:
        error_handler("检测系统内存使用率失败")
    return percent

if __name__ == "__main__":
    sys_mem = check_mem()
    success_handler(sys_mem)

