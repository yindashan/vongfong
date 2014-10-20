#!/opt/virtual_python/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time

TMPDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/tmp/'
FILENAME = TMPDIR + '.check_net_dev.tmp'

def error_handler(error_message=""):
    # print error_message
    print "HOST_STATUS | NET_DEV_IN=-1, NET_DEV_OUT=-1, NET_DEV_TOTAL=-1"
    sys.exit(1)

def success_handler(receive, transmit, total):
    print "HOST_STATUS | NET_DEV_IN=%.2f, NET_DEV_OUT=%.2f, NET_DEV_TOTAL=%.2f" % \
            (receive, transmit, total)
    sys.exit(0)

def change_unit(traffic):
    # Change Bytes to kb
    return traffic / 128.0

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
    receive, transmit, total = get_net_dev_bytes()
    value = "%s#%s#%s#%s" % (receive, transmit, total, uptime)
    write_tmp_file(filename, value)
    success_handler(0, 0, 0)
        
def check_tmp_file(filename, uptime):
    try:
        f = open(filename, "r")
    except:
        error_handler("无法打开数据文件")
    else:
        try:
            old_uptime = float(f.readline().split('#')[3])
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

def get_net_dev_bytes():
    try:
        f = open('/proc/net/dev', 'r')
        lines = f.readlines()

        receive = 0
        transmit = 0
        total = 0

        for line in lines:
            if line.lstrip().startswith("eth"):
                values = line.split(":")[1].split()
                receive += int(values[0])
                transmit += int(values[8])
        total = receive + transmit

        f.close()
    except:
        error_handler("无法访问/proc/stat")
    return receive, transmit, total

def check_net_dev():
    uptime = get_uptime()

    if os.path.exists(FILENAME):
        if check_tmp_file(FILENAME, uptime):
            receive, transmit, total = get_net_dev_bytes()
            new_values = "%s#%s#%s#%s" % (receive, transmit, total, uptime)
            old_values = read_tmp_file(FILENAME)
            write_tmp_file(FILENAME, new_values)

            try:
                receive_diff = change_unit(receive - int(old_values[0]))
                transmit_diff = change_unit(transmit - int(old_values[1]))
                total_diff = change_unit(total - int(old_values[2]))
                time_diff = uptime - float(old_values[3])

                receive_per_second = receive_diff / time_diff
                transmit_per_second = transmit_diff / time_diff
                total_per_second = total_diff / time_diff
            except:
                error_handler("数据文件内值有误")
            else:
                return receive_per_second, transmit_per_second, total_per_second
    else:
        init_tmp_file(FILENAME)


if __name__ == "__main__":
    receive_per_second, transmit_per_second, total_per_second = check_net_dev()
    success_handler(receive_per_second, transmit_per_second, total_per_second)

