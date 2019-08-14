FROM debian
MAINTAINER Jessica Hahn
RUN apt -y update && \
    apt -y upgrade && \
    apt -y install wget build-essential && \
    apt -y install git-core subversion libjansson-dev sqlite autoconf automake libxml2-dev libncurses5-dev libtool && \
    mkdir /tmp/asterisk && \
    cd /tmp/asterisk && \
    wget http://downloads.asterisk.org/pub/telephony/asterisk/asterisk-16.5.0.tar.gz && \
    tar -zxf asterisk-16.5.0.tar.gz && \
    cd asterisk-16.*/ && \
    apt -y install libedit-dev uuid-dev libsqlite3-dev && \
    ./configure && \
    make && \
    make install && \
    make samples && \
    make config && \
    make install-logrotate