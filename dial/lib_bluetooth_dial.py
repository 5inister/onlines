#!/usr/bin/python2.7
#
# This program provides the functionality for a quadrature rotary encoder
# to act as a bluetooth keuboard. All the Bluetooth-Keyboard functionality
# was lifted from http://www.linuxuser.co.uk/tutorials/emulate-a-bluetooth-keyboard-with-the-raspberry-pi
# Quoting this website:
# PiTooth allows the Raspberry Pi to act as a Bluetooth keyboard, and relays
# keypresses from a USB keyboard to a Bluetooth client. Written by Liam Fraser
# for a Linux User & Developer tutorial.
#
# This was written by Diego Trujillo-Pisanty at Newcastel University (UK) 
# for the Charting the Digital Lifespan Project.
#

import os # Used to call external commands
import sys # Used to exit the script
import bluetooth
from bluetooth import *
import dbus # Used to set up the SDP record
import time # Used for pausing the process
import evdev # Used to get input from the keyboard
from evdev import *
import keymap # Used to map evdev input to hid keycodes


class Bluetooth:
    P_CTRL = 17
    P_INTR = 19
    HOST = 0 # BT Mac address
    PORT = 1 # Bluetooth Port Number...

    def __init__(self):
        # Set the device class to a keyboard and set the name
        os.system("hciconfig hci0 class 0x002540")
        os.system("hciconfig hci0 name Raspberry\ Pi")
        # Make device discoverable
        os.system("hciconfig hci0 piscan")

        #Define socket type as L2CAP
        self.scontrol = BluetoothSocket(L2CAP)
        self.sinterrupt = BluetoothSocket(L2CAP)
        # Bind these sockets to a port
        self.scontrol.bind(("", Bluetooth.P_CTRL))
        self.sinterrupt.bind(("", Bluetooth.P_INTR))

        # Set up dbus for advertising the service record
        self.bus = dbus.SystemBus()
        try:
            self.manager = dbus.Interface(self.bus.get_object("org.bluez", "/"), "org.bluez.Manager")
            adapter_path = self.manager.DefaultAdapter()
            self.service = dbus.Interface(self.bus.get_object("org.bluez", adapter_path), "org.bluez.Service")
        except:
            sys.exit("Could not configure bluetooth. Is bluetoothd started?")

        # Read the service record from file
        try:
            fh = open(sys.path[0] + "/sdp_record.xml", "r")
        except:
            sys.exit("Could not open the sdp record. Exiting...")
        self.service_record = fh.read()
        fh.close()

    def listen(self):
          # Advertise our service record
          self.service_handle = self.service.AddRecord(self.service_record)
          print "Service record added"
          # Start listening on the server sockets
          self.scontrol.listen(1) # Limit of 1 connection
          self.sinterrupt.listen(1)
          print "Waiting for a connection"
          self.ccontrol, self.cinfo = self.scontrol.accept()
          print "Got a connection on the control channel from " + self.cinfo[Bluetooth.HOST]
          self.cinterrupt, self.cinfo = self.sinterrupt.accept()
          print "Got a connection on the interrupt channel from " + self.cinfo[Bluetooth.HOST]
