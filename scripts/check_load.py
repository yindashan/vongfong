#!/opt/virtual_python/bin/python
# -*- coding: utf-8 -*-

import sys

def error_handler(error_message=""):
    # print error_message
    print "HOST_STATUS | CPU_LOAD1=-1, CPU_LOAD5=-1, CPU_LOAD15=-1"
    sys.exit(1)

def success_handler(load1, load5, load15):
    print "HOST_STATUS | CPU_LOAD1=%s, CPU_LOAD5=%s, CPU_LOAD15=%s" % (load1, load5, load15)
    sys.exit(0)

def get_load():
    try:
        f = open('/proc/loadavg','r')
        tmp = f.readline().split()
        lavg_1 = float(tmp[0])
        lavg_5 = float(tmp[1])
        lavg_15 = float(tmp[2])
        f.close()
    except:
        error_handler("访问/proc/loadavg文件失败")
    return (lavg_1, lavg_5, lavg_15)

if __name__ == "__main__":
    (l1, l5, l15) =  get_load()
    success_handler(l1, l5, l15)

