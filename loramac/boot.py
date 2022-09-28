""" Boot file """

import socket
import binascii
import pycom
import time
import os
import machine
from machine import UART
from network import WLAN
from network import Bluetooth
from network import LoRa

uart = UART(0, baudrate=115200)
os.dupterm(uart)

# Disable WLAN/Bluetooth and save energy
wlan = WLAN()
wlan.deinit()
bt = Bluetooth()
bt.deinit()

# Disable heartbeat LED
pycom.heartbeat(False)
