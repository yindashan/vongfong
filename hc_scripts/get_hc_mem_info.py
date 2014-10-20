#!/opt/virtual_python/bin/python
# -*- coding:utf-8 -*- 

# std lib
import sys, os
import subprocess

class MemDev(object):
    def __init__(self):
        # 制造商
        self.manufacturer = ''
        # 类型
        self.type = ''
        # 容量 单位: MB
        self.size = 0
        
    def __hash__(self):
        return hash(self.key())
        
    def __eq__(self, other):
        if self.key() == other.key():
            return True
        else:
            return False
        
    def key(self):
        return '%s:%s:%s' % (self.manufacturer, self.type, self.size)
        
    def desc(self):
        return '制造商:%s,类型:%s,容量:%s MB' % (self.manufacturer, self.type, self.size)
        
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
        
# 是否是虚拟机
def is_virtual():
    command = "dmidecode |grep -i product"
    stdout_value, stderr_value = external_cmd(command)
    stdout_value = stdout_value.lower()
    '''判断服务器类型，返回结果：1表示虚拟机，0表示物理机'''
    # 根据服务器型号中是否包括虚拟机标识来判断当前服务器是虚拟机还是物理机
    virtual_flag_list = ['virtualbox', 'vmware', 'openvz', 'xen pv', 'uml', 'xen hvm', 'kvm', 'virtual pc']
    for virtual_flag in virtual_flag_list:
        if virtual_flag in stdout_value:
            return True
    return False

# 内存总量 单位:MB
def get_mem_total():
    mem_total = 0
    try:
        f = open('/proc/meminfo', 'r')
        for line in f:
            if line.startswith('MemTotal:'):
                mem_total = int(line.split()[1])
            else:
                continue
        f.close()
    except:
        pass
    return mem_total / 1024

# 从 dmidecode 中提取内存信息
def get_info():
    if is_virtual():
        total = get_mem_total()
        return '::%s:' % total, '当前机器为虚拟机，内存总量:%s MB' % total
    else:
        command = 'dmidecode | grep -A 16 -E "Memory Device$"'
        data, stderr_value = external_cmd(command)
        block_list = data.split('--')
        dd = {}
        for block in block_list:
            device = parse(block)
            if not device:
                continue
            if device not in dd:
                dd[device] = 1
            else:
                dd[device] = dd[device] + 1
                
        key_list = []    
        desc_list = []
        for item in dd:
            key_list.append(item.key() + ':' + str(dd[item]))
            desc_list.append(item.desc() + ',数量:' + str(dd[item]))
        # 如果有多个用冒号分隔
        return ';'.join(key_list), ';'.join(desc_list)

def parse(block):
    dd = {}
    item_list = block.split('\n')
    for item in item_list:
        if item.find(':') == -1:
            continue
        temp = item.split(':')
        dd[temp[0].strip()] = temp[1].strip()
    if dd['Manufacturer'] and valid_size(dd['Size']):
        device = MemDev()
        device.manufacturer = dd['Manufacturer']
        device.type = dd['Type']
        device.size = get_size(dd['Size'])
        return device
    return None

def valid_size(data):
    data = data.upper()
    for key in ['KB','MB','GB']:
        if data.find(key) != -1:
            return True
    return False
        

# 从大小信息中去出大小
def get_size(data):
    data = data.upper()
    item_list = data.split(' ');
    if data.find('MB') != -1:
        return item_list[0]
    elif data.find('GB') != -1:
        return int(item_list[0]) * 1024
    else:
        return int(item_list[0]) / 1024

def main():
    info, desc = get_info() 
    print "MEM_INFO=%s | 内存信息:%s" % (info, desc)
    
#-------------------------------start----------------------------------
if __name__ == '__main__':
    main()
    
    
    
