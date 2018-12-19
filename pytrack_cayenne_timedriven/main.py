import time
import pycom
import gc

from pytrack import Pytrack
from network import LoRa
from L76GNSS import L76GNSS
from LIS2HH12 import LIS2HH12

from CayenneLPP import CayenneLPP

py = Pytrack()
fw_version = py.read_fw_version()
print("Pytrack firmware version: " + str(fw_version))
# Pytrack GPS
time.sleep(2)
# enable garbage collector
gc.enable()

coord = None
dl_data = ""
counter = 0
mvt = False

# Init GPS
lpp = CayenneLPP()


while True:
    print("--LOOP")
    pycom.rgbled(0x001400)
    lpp.reset()
    lpp.add_digital_output(0, counter)
    lpp.add_voltage(5, py.read_battery_voltage())
    print('Sending data (uplink)...')
    s.setblocking(True)
    s.send(bytes(lpp.get_buffer()))
    s.setblocking(False)
    pycom.rgbled(0x000000)
    dl_data = s.recv(64)
    if dl_data != "":
        print('Received data (downlink)', dl_data)
        print(lora.stats())
    counter = (counter + 1)%256
    print('Counter', counter)
    time.sleep(20)
