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
	print("SIGTERM recieved, terminatng")
	GPIO.output(13,GPIO.LOW)
	GPIO.cleanup()
        sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
lib_sniffer.sniff(iface='wlan0',prn=analyser.quickAnalysis,store=0)
