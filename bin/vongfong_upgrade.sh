#! /bin/bash
############################################
# exit_1	环境检查失败
# exit_2	下载或访问更新服务器失败
# exit_3	解压或安装过程失败
############################################
export PATH=$PATH:/usr/sbin:/sbin:/bin:/usr/bin
DEFAULT_UPGRADE_SERVER="update.mon.autonavi.com"
DEFAULT_UPGRADE_PORT=80
HOME_DIR="/opt/vongfong"
HOST_ID_CFG="$HOME_DIR/config/host_id.py"
AGENT_CFG="$HOME_DIR/config/agent.py"
VONGFONG_APP="$HOME_DIR/bin/vongfong.py"
UPGRADE_LOG="$HOME_DIR/log/upgrade.log"
TMP_DIR="$HOME_DIR/tmp"
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

# 定期清除agent升级日志
ClearLog(){
	# 每月1号清除一次
	day=`date +%d`
	if [ "$day" = "1" ];then
		rm -f $UPGRADE_LOG
		echo "OK - clear upgrade_log success. `date`" >> $UPGRADE_LOG	
	fi
}

# 1. 判断是否需要更新
# 1.1 获取agent当前版本号
CURRENT_VERSION=`cat "$AGENT_CFG" |grep AGENT_VERSION |awk -F'[=]' '{print $2}' |sed 's/^ *//g' |sed 's/ *$//g'|sed 's/"//g' 2> /dev/null`
# 1.2 获取agent最新版本号
LATEST_VERSION=`curl --connect-timeout 10 --retry 3 http://$DEFAULT_UPGRADE_SERVER:$DEFAULT_UPGRADE_PORT/version 2> /dev/null`
if [ $? -ne 0 ];then
	echo "ERROR - connect to DEFAULT_UPGRADE_SERVER time out. `date`" >> $INSTALL_LOG
	echo "ERROR - connect to DEFAULT_UPGRADE_SERVER time out. `date`" 
	exit 2;
fi


# 2. 更新
if [ -n "$LATEST_VERSION" ] &&  [ "$CURRENT_VERSION" != "$LATEST_VERSION" ];then
	echo "OK - need update agent. current_version:"$CURRENT_VERSION". new_version: "$LATEST_VERSION" begin download agent. `date`" >> $UPGRADE_LOG
	echo "OK - need update agent. current_version:"$CURRENT_VERSION". new_version: "$LATEST_VERSION" begin download agent. `date`"
	
	# 2.1 下载
	VONGFONG_FILE="http://$DEFAULT_UPGRADE_SERVER:$DEFAULT_UPGRADE_PORT/download/vongfong.tar.gz"
	wget -q --tries=3 --timeout=10 -O $TMP_DIR/vongfong.tar.gz $VONGFONG_FILE 2> /dev/null
	if [ $? -ne 0 ];then
		echo "ERROR - download vongfong tarball error. `date`" >> $UPGRADE_LOG
		echo "ERROR - download vongfong tarball error. `date`"
		exit 2;
	fi

	# 2.2 解压
	tar zxf "$TMP_DIR/vongfong.tar.gz" -C "$TMP_DIR" 2> /dev/null
	if [ $? -ne 0 ];then
		echo "ERROR - decompression vongfong tarball error. `date`" >> $UPGRADE_LOG
		echo "ERROR - decompression vongfong tarball error. `date`"
		exit 3;
	fi
	
	# 2.3 删除新版本中某些文件防止覆盖
	rm -f "$TMP_DIR/vongfong/config/host_id.py"

	# 2.4 覆盖原app
	/bin/cp -r -u "$TMP_DIR/vongfong" "/opt"
   	rm -rf "$TMP_DIR/vongfong"

	# 2.5 重启
	echo "OK - update vongfong success. restart ... ... `date`" >> $UPGRADE_LOG
     	StopAgent
     	echo "OK - stop vongfong. `date`" >> $UPGRADE_LOG
     	StartAgent
     	echo "OK - start vongfong. `date`" >> $UPGRADE_LOG
     	echo "OK - start vongfong. `date`"
else
        echo "OK - current_version:"$CURRENT_VERSION". new_version:"$LATEST_VERSION". not need update agent. `date`" >> $UPGRADE_LOG
        echo "OK - current_version:"$CURRENT_VERSION". new_version:"$LATEST_VERSION". not need update agent. `date`"
        
fi

# 3. 清除tar包及日志文件
rm -f "$TMP_DIR/vongfong.tar.gz"

# 清除agent升级日志
ClearLog

exit 0;








