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