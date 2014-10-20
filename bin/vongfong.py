#!/opt/virtual_python/bin/python
# -*- coding:utf-8 -*- 

####################################
#  vongfong
#  部署在host上用于
#  1) 收集应用状态
#  2) 收集硬件信息　
####################################
# std lib
import sys, os
# -----------------------------------------------------
# 将项目路径加入系统目录
path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(path)
sys.path.append(project_path)
# ----------------------------------------------------
import time, random
import json, logging
from threading import Thread, Event
import subprocess
import socket, httplib
import traceback

# our own lib
from daemon import Daemon
from log_record import initlog
from config import agent, host_id

# 为了使代码更规范整洁                
class AppEntry(object):
    def __init__(self, appname):
        self.appname = appname
        self.status = []
        
    def add_status(self, key, value):
        self.status.append({'name':key,'value':value})
    
    def jsonate(self):
        return {'appname':self.appname,'status':self.status} 

class LoopTimer(Thread):
    """重写了Threading.Timer 类,以定时循环执行"""
    # interval    --单位:秒
    def __init__(self, interval,function, args=[], kwargs={}):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = Event()

    def cancel(self):
        """停止定时器"""
        self.finished.set()

    def run(self):
        # 随机休眠一段时间, 再开始循环
        t = random.randint(0, self.interval)
        time.sleep(t)
        while not self.finished.is_set():
            self.finished.wait(self.interval)
            if not self.finished.is_set():
                self.function(*self.args, **self.kwargs)

# 执行外部命令                
def external_cmd(cmd, msg_in=''):
    logger = logging.getLogger('agent')
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
        logger.error("执行插件:%s, ValueError: %s", cmd, err)
        return None, None
    except IOError, err:
        logger.error("执行插件:%s, IOError: %s", cmd, err)
        return None, None
    except BaseException, err:
        logger.error("执行插件:%s, error: %s", cmd, err)
        return None, None
        
# 硬件配置数据上报
def hardware_check(project_path):
    try:
        logger = logging.getLogger('agent')
    
        path = os.path.join(project_path, 'hc_scripts')
    
        # 每个具体的项的值
        item_list = []
        # 硬件配置的详细信息
        detail_list = []
        for filename in os.listdir(path):
            command = os.path.join(path, filename)
            stdout_value, stderr_value = external_cmd(command)
            try:
                if stdout_value:
                    temp_list = stdout_value.split('|')
                    item_list_str = temp_list[0].strip()
                    for kv in item_list_str.split(','):
                        kv_list = kv.split('=')
                        key = kv_list[0].strip()
                        value = kv_list[1].strip()
                        item = {'name':key, 'value':value}
                        item_list.append(item)
                    detail_list.append(temp_list[1].strip())
            except BaseException, e:
                pass
        
        item_list.append({'name':'DETAIL', 'value':'\n'.join(detail_list)})
    
        res = {'host_id':host_id.HOST_ID, 'hardware':item_list}
        
        # 发送给监控服务器
        data = json.dumps(res)
        send_info('hardware', data)
        logger.debug('硬件配置数据上报:%s', data)
        
    except BaseException, e:
        logger.error('exception:%s\n%s', e, traceback.format_exc())

# 应用状态数据上报
def app_check(project_path):
    try:
        logger = logging.getLogger('agent')
        
        path = os.path.join(project_path, 'scripts')
        
        # 每个应用1项
        app_list = []
        app_dict = {}
        for filename in os.listdir(path):
            command = os.path.join(path, filename)
            # 跳过文件夹的情况
            if os.path.isdir(command):
                continue
    
            stdout_value, stderr_value = external_cmd(command)
            try:
                if stdout_value:
                    temp_list = stdout_value.split('|')
                    appname = temp_list[0].strip()
                    app  = None
                    if appname not in app_dict:
                        app_dict[appname] = AppEntry(appname)
                    app = app_dict[appname]
                    item_list_str = temp_list[1].strip()
                    for kv in item_list_str.split(','):
                        kv_list = kv.split('=')
                        app.add_status(kv_list[0].strip(), kv_list[1].strip())
            except BaseException, e:
                pass
                    
        # 整理
        for appname in app_dict:
            app_list.append(app_dict[appname].jsonate())
            
        res = {'host_id':host_id.HOST_ID, 'app_list':app_list}
        
        # 发送给监控服务器
        data = json.dumps(res)
        send_info('status', data)
        logger.debug('应用状态数据上报:%s', data)
        
    except BaseException, e:
        logger.error('exception:%s\n%s', e, traceback.format_exc())

# 升级检查
def upgrade_check(project_path):
    command = os.path.join(project_path, 'bin', 'vongfong_upgrade.sh')
    stdout_value, stderr_value = external_cmd(command)

# 向状态转发服务器发送信息
def send_info(target, msg_body):
    logger = logging.getLogger('agent')
    headers = {}
    try:
        conn = httplib.HTTPConnection(agent.MONITOR_HOST, agent.MONITOR_PORT, timeout=5)
        conn.request("POST", "/" + target, msg_body, headers)
        response = conn.getresponse()
        data = response.read()
        logger.debug('返回结果status:%s, reason:%s, 返回输出:%s', response.status, response.reason, data)
        conn.close()
    except socket.error, e:
        logger.error('exception:%s\n%s', e, traceback.format_exc())
    except BaseException, e:
        logger.error('exception:%s\n%s', e, traceback.format_exc())
                  
class Agent(Daemon):
    def __init__(self, project_path):
        path = os.path.join(project_path, 'tmp')
        pidfile = os.path.join(path, 'vongfong.pid')
        stdout_path = os.path.join(path, 'vongfong.out')
        super(Agent, self).__init__(pidfile=pidfile, stdout=stdout_path, 
            stderr=stdout_path)
        self.project_path = project_path

        
    def run(self):
        logger = logging.getLogger('agent')
        # ------------------------
        # 1) 先上报1次硬件信息
        # ------------------------
        hardware_check(self.project_path)
        # ------------------------
        # 2) 启动定时器
        # ------------------------
        # 硬件配置数据上报 间隔:3600秒（1小时）
        t = LoopTimer(3600, hardware_check, [self.project_path])
        t.start()
        
        # 监控数据上报 间隔:30秒
        t = LoopTimer(30, app_check, [self.project_path])
        t.start()

        # 更新检查 间隔:3600秒（1小时）
        # FIXME
        t = LoopTimer(3600, upgrade_check, [self.project_path])
        t.start()
        
        
def main():
    # vongfong所在目录
    path = os.path.dirname(os.path.abspath(__file__))
    project_path = os.path.dirname(path) 
     
    log_path = os.path.join(project_path,'log')
    
    # 日志logger 初始化
    # 硬件配置及监控数据上报日志
    initlog('agent', log_path, 'agent.log', logging.DEBUG)
    # 更新日志
    initlog('upgrade', log_path, 'upgrade.log', logging.DEBUG)
    
    logger = logging.getLogger('agent')
    
    if host_id.HOST_ID == 'anonymous':
        logger.error('host_id do not config right. Quit... ...')
        print 'host_id do not config right. Quit... ...'
        return
    
    logger.info('vongfong start.')
    
    # 启动定时器   
    agent = Agent(project_path)
    agent.restart()

#-------------------------------start----------------------------------
if __name__ == '__main__':
    main()
        
    
   
 
