#!/opt/virtual_python/bin/python
# -*- coding:utf-8 -*- 

# std lib
import sys, os
import subprocess


def GetMemTotal():
    try:
        f = open('/proc/meminfo', 'r')
        for line in f:
            if line.startswith('MemTotal:'):
                mem_total = int(line.split()[1])
            else:
                continue
        f.close()
    except:
        mem_total = 0
        sys.exit(3)
    return mem_total


def main():
    mem_total = GetMemTotal()
    # 由kB转化为MB
    mem_total = mem_total/1024
    print "MEM_TOTAL=%d | 内存总量:%dM"%(mem_total, mem_total)
    
#-------------------------------start----------------------------------
if __name__ == '__main__':
    main()
    
    
    
    