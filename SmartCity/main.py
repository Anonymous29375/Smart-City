# Time helpers
import utime

# Hardware related libraries
from machine import Pin, SPI, I2C

# Import pin numbers
from pins import *

# Buzzer library
from buzzer import sound_buzzer

# WIFI library
from wifi import wifi_connect

# Adafruit IO library
from adafruit_io import AdafruitIO

# Liquid crystal display library
from lcd import LCD

# Real time clock library
from rtc import RTC

# The state of the bank
from bank_state import BankState

# Input helper class
from input import Input

# Create a bank state
bank = BankState()

# The infrared beam is triggered when the input is low
ir_beam_input =  Input(IR_BEAM_PIN, 0, Pin.PULL_UP)

# The door is open when the input is high (reed switch open)
door_input = Input(REED_SWITCH_PIN, 1, Pin.PULL_UP)

# Setup I2C port 0
i2c_port0 = I2C(0, scl=Pin(RTC_I2C_SCL), sda=Pin(RTC_I2C_SDA))

# Setup RTC on I2C port 0
rtc = RTC(i2c_port0)

# Liquid crystal display 
lcd = LCD()

if not wifi_connect():
    print('WIFI related functionality disabled')

adafruit = AdafruitIO(bank)
adafruit_client = adafruit.connect()

if adafruit_client is None:
    print('Adafruit IO related functionality disabled')    

print('Bank up and running...')

while True:
    try:
        # Update bank state
        bank.door_open = door_input.value()
        bank.beam_triggered = ir_beam_input.value()

        bank.in_alarm = bank.beam_triggered and bank.is_armed

        # sound buzzer if beam triggered
        if bank.in_alarm == True:
            sound_buzzer(100, 0.5)

        lcd.update(rtc, bank)

        if adafruit_client is not None:
            adafruit_client.check_msg()
        utime.sleep(0.1)

    finally:
        pass

