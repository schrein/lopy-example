""" Main file """

import time
import pycom

from pytrack import Pytrack
from network import LoRa
from L76GNSS import L76GNSS
from LIS2HH12 import LIS2HH12

from CayenneLPP import CayenneLPP

import config

# Possible values of wakeup reason are:
WAKE_REASON_ACCELEROMETER = 1
WAKE_REASON_PUSH_BUTTON = 2
WAKE_REASON_TIMER = 4
WAKE_REASON_INT_PIN = 8

# Init Pytrack
py = Pytrack()
fw_version = py.read_fw_version()
print("Pytrack firmware version: " + str(fw_version))
# Get wakeup reason
wakeup = py.get_wake_reason()
print("Wakeup reason: " + str(wakeup) + "; Aproximate sleep remaining: " + str(py.get_sleep_remaining()) + " sec")
# Init GPS
gps = L76GNSS(py, timeout=10)
# Init accelerometer
acc = LIS2HH12()
# Init CayenneLPP buffer
lpp = CayenneLPP()
# Init LoRaWAN
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868, adr=config.ADR)
# Restore LoRaWAN states after deepsleep
lora.nvram_restore()


def blink_led(color, delay=0.2):
    """ blink led for a short time """
    pycom.rgbled(color)
    time.sleep(delay)
    pycom.rgbled(config.COLOR_BLACK)

def check_join():
    """ Join OTAA if not already """
    if not lora.has_joined():
        # print DevEUI
        print("DevEUI: %s" % (binascii.hexlify(lora.mac())))
        app_eui = binascii.unhexlify(config.APP_EUI)
        app_key = binascii.unhexlify(config.APP_KEY)
        print("AppEUI: %s" % (binascii.hexlify(app_eui)))
        print("AppKey: %s" % (binascii.hexlify(app_key)))
        lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0, dr=0)
        while not lora.has_joined():
            blink_led(color=config.COLOR_RED, delay=2.5)
            time.sleep(1.0)
            print('Not yet joined...')
        print('OTAA joined')
        lora.nvram_save()
        blink_led(color=config.COLOR_GREEN, delay=1.0)

def send_data_lorawan():
    """ Acquire and send data """
    coord = gps.coordinates()
    battery = py.read_battery_voltage()
    print("Battery voltage: " + str(battery))
    blink_led(color=config.COLOR_GREEN)
    lpp.reset()
    if coord[0] != None and coord[1] != None:
        print("GPS: " + str(coord))
        lpp.add_gps(3, coord[0], coord[1], 0)
    else:
        print("Failed to fix GPS")
        blink_led(color=config.COLOR_BROWN)
    lpp.add_voltage(5, py.read_battery_voltage())
    lpp.add_digital_input(1, wakeup)
    print('Sending data (uplink)...')
    s.setblocking(True)
    s.bind(1)
    s.send(bytes(lpp.get_buffer()))
    s.setblocking(False)
    dl_data = s.recv(64)
    if dl_data != "":
        print('Received data (downlink)', dl_data)
        print(lora.stats)

# Main program
check_join()
# Create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
# Set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, config.DATARATE)
# check if we were awaken due to activity
if wakeup == WAKE_REASON_ACCELEROMETER:
    blink_led(color=config.COLOR_BLUE)
    # Acquire GPS
    print("--SEND ACC")
    # currently moving, wait between next GPS send
    time.sleep(30)
    send_data_lorawan()
elif wakeup == WAKE_REASON_TIMER:
    # increment counter
    pulse = pycom.nvs_get('count')
    if pulse == None:
        pulse = 0
    print("Wakeup Timer count: " + str(pulse))
    pulse += 1
    if pulse == config.COUNT_CYCLES:
        pulse = 0
        print("--SEND TIMER")
        # Try to acquire GPS
        time.sleep(30)
        send_data_lorawan()
    pycom.nvs_set('count', pulse)

# Save LoRaWAN states before deepsleep
lora.nvram_save()
# Enable activity and disable inactivity interrupts, using the default callback handler
py.setup_int_wake_up(True, False)
# enable the activity/inactivity interrupts
# set the accelereation threshold to 200mG and the min duration to 100ms
acc.enable_activity_interrupt(1000, 200)
print("Go Deep Sleep")
time.sleep(0.2)
# go to sleep for 5 minutes maximum if no accelerometer interrupt happens
py.setup_sleep(config.SLEEP_TIMER)
py.go_to_sleep()
