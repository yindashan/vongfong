#!/opt/virtual_python/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time

TMPDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/tmp/'
FILENAME = TMPDIR + '.check_cpu.tmp'

def error_handler(error_message=""):
    # print error_message
    print "HOST_STATUS | SYS_CPU=-1"
    sys.exit(1)

def success_handler(sys_cpu):
    print "HOST_STATUS | SYS_CPU=%.2f" % sys_cpu
    sys.exit(0)

def get_percent(each, total):
    try:
        percent = 100.0 * each / total
    except ZeroDivisionError:
        error_handler("除0错误")
    return percent

def write_tmp_file(filename, value):
    try:
        f = open(filename, "w")
        f.write(value)
        f.flush()
        os.fsync(f)
        f.close()
    except:
        error_handler("无法写入数据")

def read_tmp_file(filename):
    values = []
    try:
        f = open(filename, "r")
    except:
        error_handler("无法打开数据文件")
    else:
        try:
            values = f.readline().split('#')
        except:
            f.close()
            init_tmp_file(filename)
        else:
            f.close()
    return values

def init_tmp_file(filename):
    uptime = get_uptime()
    idle_time, total_time = get_sys_cpu_time()
    value = "%s#%s#%s" % (idle_time, total_time, uptime)
    write_tmp_file(filename, value)
    success_handler(0.0)
        
def check_tmp_file(filename, uptime):
    try:
        f = open(filename, "r")
    except:
        error_handler("无法打开数据文件")
    else:
        try:
            old_uptime = float(f.readline().split('#')[2])
        except:
            f.close()
            init_tmp_file(filename)
        else:
            mode = os.stat(filename)
            f.close()
            if (int(time.time()) - int(mode.st_mtime) >= 3600) or (uptime <= old_uptime):
                init_tmp_file(filename)
            else:
                return 1
    
def get_uptime():
    try:
        f = open('/proc/uptime','r')
        uptime = float(f.readline().split()[0])
        f.close()
    except:
        error_handler("无法访问/proc/uptime文件")
    return uptime

def get_sys_cpu_time():
    try:
        f = open('/proc/stat', 'r')
        values = f.readline().split()
        total_time = 0
        for i in values[1:]:
            total_time += int(i)
        idle_time = int(values[4])
        f.close()
    except:
        error_handler("无法访问/proc/stat")
    return idle_time, total_time

def check_cpu():
    uptime = get_uptime()

    if os.path.exists(FILENAME):
        if check_tmp_file(FILENAME, uptime):
            idle_time, total_time = get_sys_cpu_time()
            new_values = "%s#%s#%s" % (idle_time, total_time, uptime)
            old_values = read_tmp_file(FILENAME)
            write_tmp_file(FILENAME, new_values)

            try:
                idle_time_diff = idle_time - int(old_values[0])
                total_time_diff = total_time - int(old_values[1])
                
                sys_cpu = get_percent((total_time_diff-idle_time_diff), total_time_diff)
            except:
                error_handler("数据文件内值有误")
            else:
                return sys_cpu
    else:
        init_tmp_file(FILENAME)


if __name__ == "__main__":
    sys_cpu = check_cpu()
    success_handler(sys_cpu)

