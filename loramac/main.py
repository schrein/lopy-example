from network import LoRa
import socket
import machine
import time

# initialise LoRa in LORA mode
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
# more params can also be given, like frequency, tx power and spreading factor

lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868, frequency=867100000)

# create a raw LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

my_deveui = binascii.hexlify(lora.mac()).decode('utf-8')
print("DevEUI:%s " % my_deveui)

while True:
    # send some data
    s.setblocking(True)
    s.send('Hello from %s' % my_deveui)
    s.setblocking(False)
    # get any data received...
    data = s.recv(64)
    if len(data) > 0:
        print(data)
        print(lora.stats())
    # wait a random amount of time
    sleep_time = machine.rng() & 0x0F
    print('waiting for %s seconds' % sleep_time)
    time.sleep(sleep_time)
