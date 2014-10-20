#!/bin/bash
############################################
# 重置host_id
# exit_1	环境检查失败
# exit_2	下载或访问更新服务器失败
# exit_3	解压或安装过程失败
############################################
export PATH=$PATH:/usr/sbin:/sbin:/bin:/usr/bin
DEFAULT_UPGRADE_SERVER="update.mon.autonavi.com"
DEFAULT_UPGRADE_PORT=80
INSTALL_LOG="/tmp/vongfong_install.log"
HOME_DIR="/opt/vongfong"
HOST_ID_CFG="$HOME_DIR/config/host_id.py"
VONGFONG_APP="$HOME_DIR/bin/vongfong.py"

StopAgent(){
        PID=""
        for PID in `ps -eo pid,cmd |grep -E "vongfong" |grep -v grep |grep -v "vongfong_upgrade.sh" |sed 's/^ *//g'|cut -d " " -f 1`
        do
                kill -9 $PID
        done
}

StartAgent(){
        $VONGFONG_APP
}

IsRuning(){
	ps -ef |grep -E "vongfong" |grep -v grep |grep -v "vongfong_upgrade.sh" > /dev/null 2>&1
}

# 1. 停止agent 
StopAgent
# 2. 修改host_id.py
HOST_ID=`curl --connect-timeout 10 --retry 3 http://$DEFAULT_UPGRADE_SERVER:$DEFAULT_UPGRADE_PORT/number 2> /dev/null`
if [ $? -ne 0 ];then
	echo "ERROR - connect to DEFAULT_UPGRADE_SERVER time out. `date`" >> $INSTALL_LOG
	echo "ERROR - connect to DEFAULT_UPGRADE_SERVER time out. `date`" 
	exit 2;
fi

echo "HOST_ID=\"$HOST_ID\"" > $HOST_ID_CFG
if [ $? -ne 0 ];then
	echo "ERROR - modify host_id error. `date`" >> $INSTALL_LOG
	echo "ERROR - modify host_id error. `date`"
	exit 3;
fi
echo "OK - modify host_id success `date`" >> $INSTALL_LOG

# 3. 启动agent
StartAgent
# 检查是否成功启动
IsRuning
if [ $? -eq 0 ];then
	echo "OK - start vongfong. `date`" >> $INSTALL_LOG
	echo "OK - start vongfong. `date`"
else
	echo "ERROR - stop vongfong. `date`" >> $INSTALL_LOG
	echo "ERROR - stop vongfong. `date`"
	exit 3;		
fi





