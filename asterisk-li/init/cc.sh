#!/bin/bash
 
start() {
  echo 'Trying start service!'
  /opt/li-asterisk/tools/Python-3.6.7/bin/python3 /opt/ali/module_asterisk.pyc -d /var/run/cc.pid -c /opt/ali/modules/asterisk/conf/cc.conf

}
  
stop() {
  echo 'Trying stoping service!'
  kill $(cat /var/run/cc.pid)

restart() {
  stop
  start
}                                                                                                                                                                          
                                                                                                                                                                            
case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  restart)
    restart
    ;;
  *)
    echo $"Usage: $0 {start|stop|restart}"
    exit 1
esac
  
exit $?
