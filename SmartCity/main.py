# Time helpers
import utime

# Hardware related libraries
from machine import Pin, SPI, I2C

# LCD library for wall display
import pcd8544_fb

# Import pin numbers
from pins import *

# Buzzer library
from buzzer import sound_buzzer

# Configuration settings for WIFI, MQTT, etc
from config import get_config_setting, get_config_setting_bytes_encoded

# Real time clock configuration and libraries
from rtc import read_time

# WIFI library
from wifi import wifi_connect

# Adafruit IO library
from adafruit_io import adafruit_connect, get_is_armed

# setup IO
ir_beam = Pin(IR_BEAM_PIN, Pin.IN, Pin.PULL_UP)
reed_sw = Pin(REED_SWITCH_PIN, Pin.IN, Pin.PULL_UP)

# RTC setup using I2C
rtc = I2C(RTC_I2C_PORT, scl=Pin(RTC_I2C_SCL), sda=Pin(RTC_I2C_SDA))

# LCD set up using SPI
lcd_spi = SPI(0, mosi=Pin(LCD_MOSI_PIN), sck=Pin(LCD_SCK_PIN))
lcd_spi.init(baudrate=2000000, polarity=0, phase=0)
lcd_cs = Pin(LCD_CS_PIN)
lcd_dc = Pin(LCD_DC_PIN)
lcd_rst = Pin(LCD_RST_PIN)
lcd_back_light = Pin(LCD_BL_PIN, Pin.OUT, value=1)
lcd = pcd8544_fb.PCD8544_FB(lcd_spi, lcd_cs, lcd_dc, lcd_rst)

if not wifi_connect():
    print('WIFI related functionality disabled')

adafruit_client = adafruit_connect()

if adafruit_client is None:
    print('Adafruit IO related functionality disabled')    

# set up program variables
is_in_alarm = False
is_entering = False


# LCD control
def lcd_update():
     lcd.text('Bank', 25, 0, 1)
     lcd.text('Security', 10, 8, 1)
     if is_in_alarm:
          lcd.text('! ALARM !', 6, 16, 1)
     elif get_is_armed():
        lcd.text('ARMED', 15, 16, 1)
     elif is_entering:
        lcd.text('Entering', 10, 16, 1)
     else:
        lcd.text('UNARMED', 10, 16, 1)

     if is_door_open():
        lcd.text('door open', 10, 24, 1)
     else:
        lcd.text('door closed', 10, 24, 1)

     lcd.text(read_time(rtc), 0, 32, 1)
     lcd.clear()
     lcd.show()



def is_beam_triggered():
        # the IR beam is triggered when the input is low
        return ir_beam.value() == 0

def is_door_open():
        # the door is open when the input is high
        return reed_sw.value() == 1

print('Bank up and running...')

while True:
    try:
        is_entering = is_beam_triggered()
        door_open = is_door_open()

        is_in_alarm = is_entering and get_is_armed()

        # sound buzzer if beam triggered
        if is_in_alarm == True:
            sound_buzzer(100, 0.5)

        lcd_update()
        lcd.fill(0)

        if adafruit_client is not None:
            adafruit_client.check_msg()
        utime.sleep(0.1)

    finally:
        pass

