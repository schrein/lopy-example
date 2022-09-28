""" Main file """

import machine
import time
import pycom

from network import LoRa
from CayenneLPP import CayenneLPP

import config

# Possible values of wakeup reason are:
WAKE_REASON_ACCELEROMETER = 1
WAKE_REASON_PUSH_BUTTON = 2
WAKE_REASON_TIMER = 4
WAKE_REASON_INT_PIN = 8
NUM_ADC_READINGS = 10

# Get wakeup reason
lpp = CayenneLPP()
# Init LoRaWAN
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868, public=True, tx_retries=3, device_class=LoRa.CLASS_C, adr=config.ADR)

def blink_led(color, delay=0.2):
    """ blink led for a short time """
    pycom.rgbled(color)
    time.sleep(delay)
    pycom.rgbled(config.COLOR_BLACK)

def check_join():
    """ Join OTAA if not already """
    if not lora.has_joined():
        app_eui = binascii.unhexlify(config.APP_EUI.replace(' ',''))
        app_key = binascii.unhexlify(config.APP_KEY.replace(' ',''))
        dev_eui = binascii.unhexlify(config.DEV_EUI.replace(' ',''))
        print("AppEUI: %s" % (binascii.hexlify(app_eui)))
        print("AppKey: %s" % (binascii.hexlify(app_key)))
        print("Custom DevEUI: %s" % (binascii.hexlify(dev_eui)))
        lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0, dr=config.DATARATE)
        while not lora.has_joined():
            blink_led(color=config.COLOR_RED, delay=2.5)
            time.sleep(1.0)
            print('Not yet joined...')
        print('OTAA joined')
        blink_led(color=config.COLOR_GREEN, delay=1.0)

def get_battery():
    """
    """
    adc = machine.ADC()
    # put here ESP32 VRef measured in mV with a voltmeter
    # adc.vref(1126)
    # For Expansion Board v3.x
    adcP16 = adc.channel(pin='P16', attn=machine.ADC.ATTN_11DB)
    analog_value = adcP16.value()
    print("analog_value " + str(analog_value))
    our_voltage = (analog_value * (3.6 / 4095))*2
    print("our_voltage   " + str(our_voltage))
    pycom_voltage = adcP16.voltage()
    samples_voltage = (2*pycom_voltage)//1
    return samples_voltage / 1000

def send_data_lorawan():
    """ Acquire and send data """
    battery = get_battery()
    print("Battery voltage: " + str(battery))
    blink_led(color=config.COLOR_GREEN)
    lpp.reset()
    lpp.add_analog_input(1, battery)
    print('Sending data (uplink)...')
    s.setblocking(True)
    s.bind(1)
    s.send(bytes(lpp.get_buffer()))
    s.setblocking(False)
    dl_data = s.recv(64)
    if len(dl_data) > 0:
        print('Received data (downlink)', dl_data)
        print(lora.stats)

# Main program
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, config.DATARATE)

check_join()
send_data_lorawan()

while True:
    dl_data = s.recv(64)
    if len(dl_data) > 0:
        print('Received data (downlink)', dl_data)
        send_data_lorawan()
        print(lora.stats())
    time.sleep(1)
