#!/bin/bash
 
start() {
  echo 'Trying start service!'
  /opt/tools/Python-3.6.7/bin/python3 /opt/ali/module_asterisk.pyc -d /var/run/asterisk.pid -c /opt/ali/conf/asterisk.conf

}
  
stop() {
  echo 'Trying stoping service!'
  kill -9 $(cat /var/run/asterisk.pid)
}

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
esac
