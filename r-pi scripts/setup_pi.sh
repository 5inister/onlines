#!/bin/sh
# RUN THIS AS SUDO
echo "Installing and updating aptitude"
apt-get -y install aptitude
apt-get -y remove scratch
apt-get -y remove minecraft-pi
apt-get -y autoremove 
aptitude -y update; aptitude safe-upgrade
echo "Installing access point and sniffer"
aptitude -y install rfkill zd1211-firmware hostapd hostap-utils iw dnsmasq python-pip python-scapy whois
sudo easy_install -U distribute
#pip install ipwhois
pip install stompest
echo "Copying configuration files (backups can be found in ~/backups)"
mkdir ~/backups
cp /etc/network/interfaces ~/backups/interfaces.backup
cp /etc/dnsmasq.conf ~/backups/dnsmasq.conf.backup
cp ./interfaces /etc/network/interfaces
cp ./hostapd.conf /etc/hostapd/hostapd.conf
hostapd -B /etc/hostapd/hostapd.conf
cp ./dnsmasq.conf /etc/dnsmasq.conf
"Starting access point"
service dnsmasq restart
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A POSTROUTING -j MASQUERADE
echo "Seting up access point on boot"
cp ./pipoint /etc/init.d/pipoint
chmod +x /etc/init.d/pipoint
update-rc.d pipoint start 99
# echo "Installing LAMP server"
# aptitude install apache2 mysql-server php5 php5-mysql
# echo "Installing Node.js"
#Install node from official website
# mkdir /opt/node
# wget http://nodejs.org/dist/v0.10.4/node-v0.10.4-linux-arm-pi.tar.gz
# tar xvzf node-v0.10.4-linux-arm-pi.tar.gz
# cp -r node-v0.10.4-linux-arm-pi/* /opt/node
# cp .bash_profiles ~
# export PATH=$PATH:/opt/node/bin
# ln -s /opt/node/bin/node /usr/bin/node
# ln -s /opt/node/lib/node /usr/lib/node
# ln -s /opt/node/bin/npm /usr/bin/npm
# echo "Installing Node modules onoff and socket.io"
# npm install -g onoff
# npm install -g socket.io
# npm install -g express
echo "Going for reboot"
reboot
