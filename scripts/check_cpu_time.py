#!/opt/virtual_python/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time

TMPDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/tmp/'
FILENAME = TMPDIR + '.check_cpu_time.tmp'

def error_handler(error_message=""):
    # print error_message
    print "HOST_STATUS | SYS_CPU_IOWAIT=-1, SYS_CPU_SYSTIME=-1, SYS_CPU_NICETIME=-1, SYS_CPU_USERTIME=-1"
    sys.exit(1)

def success_handler(iowait_time, sys_time, nice_time, user_time):
    print "HOST_STATUS | SYS_CPU_IOWAIT=%.2f, SYS_CPU_SYSTIME=%.2f, SYS_CPU_NICETIME=%.2f, SYS_CPU_USERTIME=%.2f" % \
            (iowait_time, sys_time, nice_time, user_time)
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
    iowait_time, sys_time, nice_time, user_time, total_time = get_sys_cpu_time()
    value = "%s#%s#%s#%s#%s#%s" % (iowait_time, sys_time, nice_time, user_time, total_time, uptime)
    write_tmp_file(filename, value)
    success_handler(0.0, 0.0, 0.0, 0.0)
        
def check_tmp_file(filename, uptime):
    try:
        f = open(filename, "r")
    except:
        error_handler("无法打开数据文件")
    else:
        try:
            old_uptime = float(f.readline().split('#')[5])
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
        iowait_time = int(values[5])
        sys_time = int(values[3])
        nice_time = int(values[2])
        user_time = int(values[1])
        f.close()
    except:
        error_handler("无法访问/proc/stat")
    return iowait_time, sys_time, nice_time, user_time, total_time

def check_cpu_time():
    uptime = get_uptime()

    if os.path.exists(FILENAME):
        if check_tmp_file(FILENAME, uptime):
            iowait_time, sys_time, nice_time, user_time, total_time = get_sys_cpu_time()
            new_values = "%s#%s#%s#%s#%s#%s" % (iowait_time, sys_time, nice_time, user_time, total_time, uptime)
            old_values = read_tmp_file(FILENAME)
            write_tmp_file(FILENAME, new_values)

            try:
                iowait_time_diff = iowait_time - int(old_values[0])
                sys_time_diff = sys_time - int(old_values[1])
                nice_time_diff = nice_time - int(old_values[2])
                user_time_diff = user_time - int(old_values[3])
                total_time_diff = total_time - int(old_values[4])
                
                iowait_time_res = get_percent(iowait_time_diff, total_time_diff)
                sys_time_res = get_percent(sys_time_diff, total_time_diff)
                nice_time_res = get_percent(nice_time_diff, total_time_diff)
                user_time_res = get_percent(user_time_diff, total_time_diff)
            except:
                error_handler("数据文件内值有误")
            else:
                return iowait_time_res, sys_time_res, nice_time_res, user_time_res
    else:
        init_tmp_file(FILENAME)


if __name__ == "__main__":
    iowait_time_res, sys_time_res, nice_time_res, user_time_res = check_cpu_time()
    success_handler(iowait_time_res, sys_time_res, nice_time_res, user_time_res)

