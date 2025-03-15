# Time helpers
import utime

# Network and secure sockets libraries
import network
import ssl

# Hardware related libraries
from machine import Pin, SPI, I2C

# MQTT libraries for talking to Adafruit IO feeds
from umqtt.robust import MQTTClient

# LCD library for wall display
import pcd8544_fb

# Import pin numbers
from pins import *

# Configuration settings for WIFI, MQTT, etc
from config import get_config_setting, get_config_setting_bytes_encoded

# Real time clocck configuration and libraries
from rtc import read_time


# Load config settings (and convert to byte strings)
ADAFRUIT_IO_URL = get_config_setting_bytes_encoded("mqtt_host")
ADAFRUIT_USERNAME = get_config_setting_bytes_encoded("mqtt_username")
ADAFRUIT_IO_KEY = get_config_setting_bytes_encoded("mqtt_key")
ADAFRUIT_IO_FEEDNAME = get_config_setting_bytes_encoded("mqtt_topic")

WIFI_SSID = get_config_setting_bytes_encoded("wifi_ssid")
WIFI_PASSWORD = get_config_setting_bytes_encoded("wifi_password")

feed_topic = f'{get_config_setting("mqtt_username")}/feeds/{get_config_setting("mqtt_topic")}'.encode('utf-8')

# setup IO
ir_beam = Pin(IR_BEAM_PIN, Pin.IN, Pin.PULL_UP)
buzzer = Pin(BUZZER_PIN, Pin.OUT)
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

# Connect to WIFI
print(f"Connecting to WIFI {WIFI_SSID}")
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASSWORD)

# set up program variables
is_in_alarm = False
is_entering = False
is_armed = False

# wait until the device is connected to the WiFi network
MAX_ATTEMPTS = 20
attempt_count = 0
while not wifi.isconnected() and attempt_count < MAX_ATTEMPTS:
    attempt_count += 1
    utime.sleep(1)

if attempt_count == MAX_ATTEMPTS:
    print('could not connect to the WiFi network')
else:
    print("Connected to  WIFI")

# Connect to adafruit IO
def mqtt_callback(topic, msg):
    global is_armed
    print(feed_topic)
    print(topic)
    if topic == feed_topic:
        is_armed = msg == b'ON'

mqtt_client_id = 'the_secure_bank'

print(f"Connecting to MQTT as user {ADAFRUIT_USERNAME}")
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.verify_mode = ssl.CERT_NONE
client = MQTTClient(client_id=mqtt_client_id, 
                    server=ADAFRUIT_IO_URL, 
                    user=ADAFRUIT_USERNAME, 
                    password=ADAFRUIT_IO_KEY,
                    ssl=context)

try:      
    client.connect()
    print(f'Connected to MQTT, subscribing to feed topic {ADAFRUIT_IO_FEEDNAME}')
    mqtt_feedname = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, ADAFRUIT_IO_FEEDNAME), 'utf-8')    
    client.set_callback(mqtt_callback)                    
    client.subscribe(mqtt_feedname)  
except Exception as e:
    print('Could not connect to MQTT server {}{}'.format(type(e).__name__, e))


# LCD control
def lcd_update():
     lcd.text('Bank', 25, 0, 1)
     lcd.text('Security', 10, 8, 1)
     if is_in_alarm:
          lcd.text('! ALARM !', 6, 16, 1)
     elif is_armed:
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

# Buzzer control
def sound_buzzer(frequency, duration):
    # Calculate period (time for one cycle)
    period = 1.0 / frequency  
    half_period = period / 2
    end_time = utime.ticks_ms() + (duration * 1000)  # Convert duration to milliseconds

    while utime.ticks_ms() < end_time:
        buzzer.value(1)  # Turn on the buzzer
        utime.sleep(half_period)
        buzzer.value(0)  # Turn off the buzzer
        utime.sleep(half_period)

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

        is_in_alarm = is_entering and is_armed

        # sound buzzer if beam triggered
        if is_in_alarm == True:
            sound_buzzer(100, 0.5)

        lcd_update()
        lcd.fill(0)

        client.check_msg()
        utime.sleep(0.1)

    finally:
        pass

