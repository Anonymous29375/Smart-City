# Time helpers
import utime

# Hardware related libraries
from machine import Pin, I2C

# Import pin numbers
from pins import *

# Buzzer library
from buzzer import sound_buzzer, turn_off_buzzer

# WIFI library
from wifi import wifi_connect, WIFI_SSID

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

# Create a bank state (contains the state of the bank and its devices)
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

# Update LCD to initialising
lcd.update_initialising()

adafruit = AdafruitIO(bank)

# Update LCD to initialising WIFI
lcd.update_initialising("WIFI", WIFI_SSID)

# Try and connect to the WIFI
wifi_connected = wifi_connect()
if not wifi_connected:
    print('WIFI related functionality disabled')


# Update LCD to initialising WIFI
lcd.update_initialising("AdafruitIO", 'Remote Arm')

# Only connect to Adafruit IO if we could connect to WIFI
adafruit_io_connected = False
if wifi_connected:
    adafruit_io_connected = adafruit.connect()

# Update alarm state on boot
if adafruit_io_connected is not None:
    adafruit.send_alarm_update()

print('Bank up and running...')

while True:
    try:
        # Update bank state
        bank.door_open = door_input.value()
        bank.beam_triggered = ir_beam_input.value()

        # Get the current date and time
        date_time = rtc.get_date_time()

        # After hours is before 7am and 7pm and after
        is_after_hours = date_time.hour < 7 or date_time.hour >= 19 # 19 is 19:00 (or 7pm)

        # The back is armed if it is remote armed OR it is after hours
        bank.is_armed = bank.is_remote_armed or is_after_hours

        prev_alarm_state = bank.in_alarm
        bank.in_alarm = (bank.beam_triggered or bank.door_open) and bank.is_armed

        if prev_alarm_state is not bank.in_alarm:
            adafruit.send_alarm_update()

        # sound buzzer if beam triggered
        if bank.in_alarm == True:
            sound_buzzer(100, 0.5)
        else:
            # make sure buzzer is off
            turn_off_buzzer()

        lcd.update_state(rtc, bank)
        
        if adafruit_io_connected is not None:
            adafruit.check_msg()
        utime.sleep(0.1)

    finally:
        pass

