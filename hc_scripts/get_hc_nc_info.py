#!/opt/virtual_python/bin/python
# -*- coding:utf-8 -*- 
import socket
import fcntl
import struct
import sys, os
import subprocess

SIOCGIFADDR = 0x8915
SIOCGIFNETMASK = 0x891b

# 存储网卡配置信息
class NetCard(object):
    def __init__(self):
        self.name = ''
        self.ip = ''
        self.mask = ''
        self.gateway = ''

# 执行外部命令                
def external_cmd(cmd, msg_in=''):
    try:
        proc = subprocess.Popen(cmd,
                   shell=True,
                   stdin=subprocess.PIPE,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                  )
        stdout_value, stderr_value = proc.communicate(msg_in)
        return stdout_value, stderr_value
    except ValueError, err:
        return None, None
    except IOError, err:
        return None, None

# 取得指定网卡名上的IP地址
def get_ip_address(ifname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
            SIOCGIFADDR, struct.pack('256s', ifname[:15])
        )[20:24])
    except BaseException:
        return None
        
# 获取子网掩码
def get_mask(ifname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        mask = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 
            SIOCGIFNETMASK, struct.pack('256s', ifname[:15]))[20:24])
        return mask
    except BaseException:
        return None
        
# 获取默认网关 
def get_default_gateway(ifname):
    command ="ip route list dev %s | awk '/^default/ {print $3}'" % (ifname)
    stdout_value, stderr_value = external_cmd(command)
    return stdout_value.strip()
    
# 域名服务器
def get_nameserver():
    command = "cat /etc/resolv.conf | grep -E '^nameserver' | awk '{print $2}'"
    stdout_value, stderr_value = external_cmd(command)
    item_list = stdout_value.split('\n')
    res_list = []
    for item in item_list:
        if item:
            res_list.append(item)
    return res_list
   

def get_netcard_list():
    # 已启用的网卡列表
    netcard_active_list = []
    try:
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
    except BaseException:
        return []
    return netcard_active_list

# 网卡和IP对应关系
def get_info():
    ll = []
    nc_name_list = get_netcard_list()
    for nc_name in nc_name_list:
        ip = get_ip_address(nc_name)
        if ip:
            card = NetCard()
            card.name = nc_name
            card.ip = str(get_ip_address(nc_name))
            card.mask = str(get_mask(nc_name))
            card.gateway = get_default_gateway(nc_name)
            ll.append(card)
    return ll
        
def main():
    ll = get_info()
    # 网卡名1;IP1;; 网卡名2;IP2;;   
    key_list = []
    desc_list = []
    for card in ll:
        # 网卡名1:IP地址1:子网掩码1:默认网关1;网卡名2:IP地址2:子网掩码2:默认网关2
        key_list.append('%s:%s:%s:%s' % (card.name, card.ip, card.mask, card.gateway))
        desc_list.append('网卡名:%s,对应IP地址:%s,子网掩码:%s,默认网关:%s' % (card.name, 
            card.ip, card.mask, card.gateway))
    
    # 域名服务器
    server_list = get_nameserver()
    
    print "SYS_NETWORK=%s,NAMESERVER=%s | 已经启用的网卡: %s,域名服务器:%s" % (';'.join(key_list),
        ':'.join(server_list), ','.join(desc_list), ','.join(server_list), )  
    
    
if __name__ == "__main__":
    main()
    
    





