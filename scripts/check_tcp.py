#!/opt/virtual_python/bin/python
# -*- coding:utf-8 -*-

import sys

def error_handler(error_message=""):
    # print error_message
    print "HOST_STATUS | SYS_SOCKET_TCP=-1"
    sys.exit(1)

def success_handler(tcp_count):
    print "HOST_STATUS | SYS_SOCKET_TCP=%d" % tcp_count
    sys.exit(0)

def check_tcp():
    try:
        count = 0
        f = open('/proc/net/sockstat')
        lines = f.readlines()
        f.close()
        for line in lines:
            line = line.lstrip()
            tcp_list = line.lower().split()
            if tcp_list[0] == 'tcp:':
                count = int(tcp_list[4]) + int(tcp_list[6]) + int(tcp_list[8])
    except:
        error_handler("读取/proc/net/sockstat失败")
    return count
    
if __name__ == '__main__':
    tcp_count = check_tcp()
    success_handler(tcp_count)
