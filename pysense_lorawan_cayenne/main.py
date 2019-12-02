import time
import pycom
import gc

from network import LoRa
from pysense import Pysense
from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2, ALTITUDE, PRESSURE
from CayenneLPP import CayenneLPP


# Disable default blue LED blink
pycom.heartbeat(False)
# Pytrack GPS
time.sleep(2)
# enable garbage collector
gc.enable()
# Enable pytrack shield
py = Pysense()
print("Pysense firmware version: " + str(py.read_fw_version()))
counter = 0
# Init sensors
si = SI7006A20(py)
lt = LTR329ALS01(py)
li = LIS2HH12(py)
mpp = MPL3115A2(py,mode=PRESSURE) # Returns pressure in Pa. Mode may also be set to ALTITUDE, returning a value in meters
lpp = CayenneLPP()


"""
print("MPL3115A2 temperature: " + str(mp.temperature()))
print("Altitude: " + str(mp.altitude()))
print("Pressure: " + str(mpp.pressure()))

print("Dew point: "+ str(si.dew_point()) + " deg C")
t_ambient = 24.4
print("Humidity Ambient for " + str(t_ambient) + " deg C is " +\
        str(si.humid_ambient(t_ambient)) + "%RH")
print("Light (channel Blue lux, channel Red lux): " + str(lt.light()))
print("Acceleration: " + str(li.acceleration()))
print("Roll: " + str(li.roll()))
print("Pitch: " + str(li.pitch()))
print("Battery voltage: " + str(py.read_battery_voltage()))
"""

while True:
    # Build message data
    lpp.reset()
    lpp.add_temperature(1, si.temperature())
    lpp.add_relative_humidity(2, si.humidity())
    lpp.add_barometric_pressure(3, int(mpp.pressure() / 100))
    lpp.add_luminosity(4, lt.light()[0])
    lpp.add_voltage(5, py.read_battery_voltage())
    x,y,z = li.acceleration()
    lpp.add_accelerometer(1, x,y,z)

    s.setblocking(True)
    s.send(bytes(lpp.get_buffer()))
    s.setblocking(False)
    # Print if received data
    data = s.recv(64)
    print(data)
    # Print last RX LoRa stats
    print(lora.stats())
    counter = counter + 1
    print(counter)
    time.sleep(20)
