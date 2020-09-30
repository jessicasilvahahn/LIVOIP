#!/bin/bash
 
start() {
  echo 'Trying start service!'
  /opt/tools/Python-3.6.7/bin/python3 /opt/ali/module_mediation.pyc -d /var/run/mediation.pid -c /opt/ali/conf/mediation_function.conf

}
  
stop() {
  echo 'Trying stoping service!'
  kill -9 $(cat /var/run/mediation.pid)
  rm /var/run/mediation.pid
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
    exit 1
esac
  
exit $?