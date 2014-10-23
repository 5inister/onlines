#!/bin/sh
# RUN THIS AS SUDO
echo "Installing and updating packages"
apt-get install aptitude
aptitude update; aptitude safe-upgrade
aptitude install rfkill zd1211-firmware hostapd hostap-utils iw dnsmasq python-pip python-scapy whois
pip install python-whois
echo "Copying configuration files"
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
"Seting up access point on boot"
cp ./pipoint /etc/init.d/pipoint
chmod +x /etc/init.d/pipoint
update-rc.d pipoint start 99
