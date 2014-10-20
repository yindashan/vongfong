#!/opt/virtual_python/bin/python
# -*- coding:utf-8 -*- 
import socket
import subprocess
import fcntl
import struct

SIOCGIFADDR = 0x8915
# SIOCGIFNETMASK = 0x891b

# 取得指定网卡名上的IP地址
def get_ip_address(ifname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
            SIOCGIFADDR, struct.pack('256s', ifname[:15])
        )[20:24])
    except BaseException, e:
        return None

def get_net_data():
    try:
        # 已启用的网卡列表
        netcard_active_list = []
        f = open("/proc/net/dev", "r")
        all_lines = f.readlines()
        f.close()
        for line in all_lines[2:]:
            fields = line.split(':')
            name = fields[0].strip()
            
            tmp = fields[1].split()
            bytes_recv = int(tmp[0])
            bytes_sent = int(tmp[8])
            
            if name != 'lo' and bytes_recv != 0 and bytes_sent != 0:
                netcard_active_list.append(name)
    except:
        return []
    return netcard_active_list
    
def get_mark_ip():
    netcard_active_list = get_net_data()
    other_list = []
    for card_name in netcard_active_list:
        ip = get_ip_address(card_name)
        if ip:
            if ip.startswith('10.') or ip.startswith('192.168.'):
                return ip
            else:
                other_list.append(ip)
                
    if other_list:
        return other_list[0]
    
    return '0.0.0.0'
    

def main():
    local_ip = get_mark_ip()
    netcard_active_list = get_net_data()
    print "IP=%s | 已经启用的网卡: %s"%(local_ip, ','.join(netcard_active_list))
    

if __name__ == "__main__":
    main()






