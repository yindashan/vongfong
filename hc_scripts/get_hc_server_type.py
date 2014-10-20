#!/opt/virtual_python/bin/python
# -*- coding:utf-8 -*- 

# std lib
import sys, os
import subprocess


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

def isVirtual(stdout_value):
    stdout_value = stdout_value.lower()
    '''判断服务器类型，返回结果：1表示虚拟机，0表示物理机'''
    # 根据服务器型号中是否包括虚拟机标识来判断当前服务器是虚拟机还是物理机
    virtual_flag_list = ['virtualbox', 'vmware', 'openvz', 'xen pv', 'uml', 'xen hvm', 'kvm', 'virtual pc']
    for virtual_flag in virtual_flag_list:
        if virtual_flag in stdout_value:
            return 1 
    return 0

def main():
    command = "dmidecode |grep -i product"
    stdout_value, stderr_value = external_cmd(command)
    flag = isVirtual(stdout_value)
    if flag == 1:
        serverType = '虚拟机'
    elif flag == 0:
        serverType = '物理机'
        
    print "IS_VIRTUAL=%d | 服务器类型:%s"%(flag, serverType)
    
#-------------------------------start----------------------------------
if __name__ == '__main__':
    main()
    
    
    
