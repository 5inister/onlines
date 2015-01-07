#!/bin/python

###################################################################
#The main program to be executed by the Onlines Network Analyser  #
#is contained within this file. It requires a properly structured #
#config.py program in the same directory as this.                 #
###################################################################

import onlinesConfig
import lib_sniffer
import RPi.GPIO as GPIO
import signal
import os
import sys

#Get process id and store it under /var/run/sniffer.pid
PID=os.getpid()
with open('/var/run/sniffer.pid','w') as sniffer_pid:
        sniffer_pid.write(str(PID))
#Define and turn on LED
GPIO.setmode(GPIO.BOARD)
GPIO.setup(13,GPIO.OUT)
GPIO.output(13,GPIO.HIGH)

#Create a Packet instance.
analyser=lib_sniffer.Analysis(onlinesConfig.router_mac,onlinesConfig.server,onlinesConfig.services,onlinesConfig.user)

def signal_handler(signal, frame):
	'''A signal catcher for when system calls SIGTERM through
	a killall command.
	'''
	print("SIGTERM recieved, terminating")
	GPIO.output(13,GPIO.LOW)
	GPIO.cleanup()
        os.remove('/var/run/sniffer.pid')
        sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
lib_sniffer.sniff(iface='wlan0',prn=analyser.quickAnalysis,store=0)
