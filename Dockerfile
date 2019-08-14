FROM debian
MAINTAINER Jessica Hahn
RUN apt-get update
RUN apt-get upgrade
RUN apt-get -y install wget build-essential
RUN apt-get -y install git-core subversion libjansson-dev sqlite autoconf automake libxml2-dev libncurses5-dev libtool
RUN mkdir /tmp/asterisk && \
cd /tmp/asterisk && \
wget http://downloads.asterisk.org/pub/telephony/asterisk/asterisk-16.5.0.tar.gz && \
tar -zxf asterisk-16.5.0.tar.gz && \
cd asterisk-16.*/ && \
contrib/scripts/install_prereq && \
contrib/scripts/get_mp3_source.sh && \
./configure && \
make && \
make install && \
make samples && \
make config && \
make install-logrotate


