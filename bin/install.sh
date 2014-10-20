#! /bin/bash
############################################
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

# 如果已经安装, 则无需重复安装
IsRuning
if [ $? -eq 0 ];then
	echo "OK - The monitor agent had installed.You don't need install it in this machine. `date`" >> $INSTALL_LOG
	echo "OK - The monitor agent had installed.You don't need install it in this machine. `date`"
	exit 1;		
fi


# 1. 虚拟python环境的安装
# 1.1 检查操作系统的位数
BITS=64
file /bin/ls 2> /dev/null |grep -qi 32-bit
if [ $? -eq 0 ];then
        BITS=32
else
        file /bin/ls 2> /dev/null |grep -qi 64-bit
        if [ $? -eq 0 ];then
                BITS=64
        else
                ost=`getconf LONG_BIT 2> /dev/null`
                if [ -z "$ost" ];then
			echo "ERROR - get os bit type error. `date`" >> $INSTALL_LOG
                        echo "ERROR - get os bit type error. `date`"
                        exit 1;
                elif [ "$ost" -eq 32 ];then
                        BITS=32
                fi
        fi
fi

# 1.2 安装统一版本的python环境
VP_FILE="http://$DEFAULT_UPGRADE_SERVER:$DEFAULT_UPGRADE_PORT/download/Python-2.7.3.tar.bz2"
echo "OK - begin install virtual_python `date`" >> $INSTALL_LOG
echo "OK - begin install virtual_python `date`"

wget -q --tries=3 --timeout=10 $VP_FILE 2> /dev/null

if [ $? -ne 0 ];then
	echo "ERROR - download virtual_python error. `date`" >> $INSTALL_LOG
	echo "ERROR - download virtual_python error. `date`"
	exit 2;
fi


# 记录当前目录
curdir=`pwd`
mkdir -p /opt/virtual_python
tar jxf Python-2.7.3.tar.bz2
cd Python-2.7.3
./configure --prefix=/opt/virtual_python > /dev/null 2>&1

if [ $? -ne 0 ];then
	echo "ERROR - configure virtual_python error. `date`" >> $INSTALL_LOG
	echo "ERROR - configure virtual_python error. `date`"
	exit 3;
else
	echo "OK - configure virtual_python success. `date`" >> $INSTALL_LOG
	echo "OK - configure virtual_python success. `date`"
fi

make > /dev/null 2>&1

if [ $? -ne 0 ];then
	echo "ERROR - make virtual_python error. `date`" >> $INSTALL_LOG
	echo "ERROR - make virtual_python error. `date`"
	exit 3;
else
	echo "OK - make virtual_python success. `date`" >> $INSTALL_LOG
	echo "OK - make virtual_python success. `date`"
fi

make install > /dev/null 2>&1

if [ $? -ne 0 ];then
	echo "ERROR - make install virtual_python error. `date`" >> $INSTALL_LOG
	echo "ERROR - make install virtual_python error. `date`"
	exit 3;
else
	echo "OK - make install virtual_python success. `date`" >> $INSTALL_LOG
	echo "OK - make install virtual_python success. `date`"
fi

# 回到当前目录
cd $curdir

echo "OK - install virtual_python success `date`" >> $INSTALL_LOG
echo "OK - install virtual_python success `date`"



# 2. 安装vongfong
# 2.1 部署agent文件
VONGFONG_FILE="http://$DEFAULT_UPGRADE_SERVER:$DEFAULT_UPGRADE_PORT/download/vongfong.tar.gz"
wget -q --tries=3 --timeout=10 $VONGFONG_FILE 2> /dev/null
if [ $? -ne 0 ];then
	echo "ERROR - download vongfong tarball error. `date`" >> $INSTALL_LOG
	echo "ERROR - download vongfong tarball error. `date`"
	exit 2;
fi
tar zxf vongfong.tar.gz -C /opt 2> /dev/null
if [ $? -ne 0 ];then
	echo "ERROR - decompression vongfong tarball error. `date`" >> $INSTALL_LOG
	echo "ERROR - decompression vongfong tarball error. `date`"
	exit 3;
fi
echo "OK - decompression vongfong success `date`" >> $INSTALL_LOG

# 2.2 修改主机ID
# 获取新的主机ID
HOST_ID=`curl --connect-timeout 10 --retry 3 http://$DEFAULT_UPGRADE_SERVER:$DEFAULT_UPGRADE_PORT/number 2> /dev/null`
if [ $? -ne 0 ];then
	echo "ERROR - connect to DEFAULT_UPGRADE_SERVER time out. `date`" >> $INSTALL_LOG
	echo "ERROR - connect to DEFAULT_UPGRADE_SERVER time out. `date`" 
	exit 2;
fi
sed -i "s/anonymous/$HOST_ID/g" $HOST_ID_CFG
if [ $? -ne 0 ];then
	echo "ERROR - modify host_id error. `date`" >> $INSTALL_LOG
	echo "ERROR - modify host_id error. `date`"
	exit 3;
fi
echo "OK - modify host_id success `date`" >> $INSTALL_LOG
 
# 2.3 启动agent
echo "OK - install vongfong success. start ... ... `date`" >> $INSTALL_LOG
StopAgent
echo "OK - stop vongfong. `date`" >> $INSTALL_LOG
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

# 配置agent的开机自启动
AUTORUN_FILE="/etc/rc.d/rc.local"
cat /etc/issue |grep -qi 'ubuntu'
if [ $? -eq 0 ];then
	AUTORUN_FILE="/etc/rc.local"
fi
# 是否已经配置过开机自启动
cat $AUTORUN_FILE |grep -qi '/opt/virtual_python/bin/python /opt/vongfong/bin/vongfong.py'
if [ $? -ne 0 ];then
	echo "/opt/virtual_python/bin/python /opt/vongfong/bin/vongfong.py"  >> $AUTORUN_FILE
fi

# 3. 清除tar包
#rm -f "virtual_python-$BITS.tar.gz"
rm -f "Python-2.7.3.tar.bz2"
rm -rf "Python-2.7.3"
rm -f "vongfong.tar.gz"

exit 0







