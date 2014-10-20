#!/opt/virtual_python/bin/python
# -*- coding: utf-8 -*-

import sys

def error_handler(error_message=""):
    # print error_message
    print "HOST_STATUS | SYS_SWAP=-1"
    sys.exit(1)

def success_handler(sys_swap):
    print "HOST_STATUS | SYS_SWAP=%.1f" % sys_swap
    sys.exit(0)

def get_percent(use, total):
    if total == 0:
        return 0
    else:
        ret = (float(use) / total) * 100
    return ret

def check_swap():
    try:
        f = open('/proc/meminfo', 'r')
        total = free = None
        for line in f:
            if line.startswith('SwapTotal:'):
                total = int(line.split()[1]) * 1024
            elif line.startswith('SwapFree:'):
                free = int(line.split()[1]) * 1024
            if total is not None and free is not None:
                break
        f.close()
        assert total is not None and free is not None
        used = total - free
        percent = get_percent(used, total)
        return percent
    except:
        error_handler("检测系统SWAP使用率失败")

if __name__ == "__main__":
    sys_swap = check_swap()
    success_handler(sys_swap)

