""" Application configuration parameters """

# Time to sleep in second if no movement
SLEEP_TIMER = 300
# Sleep cycles between send if no movement, 1 hour.
COUNT_CYCLES = 12
# LoRaWAN OTAA Keys, change APP_EUI and APP_KEY 
APP_EUI = '0123456789012345'
APP_KEY = '01234567890123450123456789012345'
# Disable ADR for mobile objects
ADR = False
# Set Datarate, from 0 to 5
DATARATE = 3

# Leds colors
COLOR_YELLOW = 0xffff00
COLOR_RED = 0xff0000
COLOR_GREEN = 0x00ff00
COLOR_BLUE = 0x0000ff
COLOR_BROWN = 0x996633
COLOR_BLACK = 0x000000
