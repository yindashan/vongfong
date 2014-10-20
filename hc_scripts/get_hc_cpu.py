#!/opt/virtual_python/bin/python
# -*- coding:utf-8 -*- 

# std lib
import sys, os
import re
import subprocess


def getCpuNum():
    try:
        return os.sysconf("SC_NPROCESSORS_ONLN")
    except ValueError:
        num = 0
        f = open('/proc/cpuinfo', 'r')
        try:
            lines = f.readlines()
        finally:
            f.close()
        for line in lines:
            if line.lower().startswith('processor'):
                num += 1
    if num == 0:
        f = open('/proc/stat', 'r')
        try:
            lines = f.readlines()
        finally:
            f.close()
        search = re.compile('cpu\d')
        for line in lines:
            line = line.split(' ')[0]
            if search.match(line):
                num += 1
    return num


def main():
    cpu_num = getCpuNum()
    print "CPU_COUNT=%d | cpu核数:%d"%(cpu_num, cpu_num)
    
#-------------------------------start----------------------------------
if __name__ == '__main__':
    main()
    
    
    
    