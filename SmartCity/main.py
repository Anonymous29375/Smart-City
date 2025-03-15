# python imports
import network
import pcd8544_fb
from machine import Pin, SPI, I2C
import utime
import ssl
from umqtt.robust import MQTTClient
from config import *

# pin numbers
IR_BEAM_PIN = 0

LCD_DC_PIN = 4
LCD_CS_PIN = 5
LCD_SCK_PIN = 6
LCD_MOSI_PIN = 7
LCD_RST_PIN = 8
LCD_BL_PIN = 9

RTC_I2C_PORT = 0
RTC_I2C_SDA = 20
RTC_I2C_SCL = 21

BUZZER_PIN = 28

# RTC values
RTC_ADDR = 0x68
RTC_START_REG = 0x00

# Load config settings (and convert to byte strings)
ADAFRUIT_IO_URL = config["mqtt_host"].encode('utf-8')
ADAFRUIT_USERNAME = config["mqtt_username"].encode('utf-8')
ADAFRUIT_IO_KEY = config["mqtt_key"].encode('utf-8')
ADAFRUIT_IO_FEEDNAME = config["mqtt_topic"].encode('utf-8')

WIFI_SSID = config["wifi_ssid"].encode('utf-8')
WIFI_PASSWORD = config["wifi_password"].encode('utf-8')

feed_topic = f'{config["mqtt_username"]}/feeds/{config["mqtt_topic"]}'.encode('utf-8')

# setup IO
ir_beam = Pin(IR_BEAM_PIN, Pin.IN, Pin.PULL_UP)
buzzer = Pin(BUZZER_PIN, Pin.OUT)

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



# RTC read date and time
def read_date_time() -> str:
    t = rtc.readfrom_mem(int(RTC_ADDR),int(RTC_START_REG),7)
    sec = t[0]&0x7F
    min = t[1]&0x7F
    hour = t[2]&0x3F
    weekday = t[3]&0x07
    day = t[4]&0x3F
    month = t[5]&0x1F
    year = t[6]&0xFF
    formatted_date_time = "{:02x}/{:02x}/{:02x} {:02x}:{:02x}:{:02x}".format(year, month, day, hour, min, sec)
    return formatted_date_time

# RTC read time only (no date)
def read_time() -> str:
    t = rtc.readfrom_mem(int(RTC_ADDR),int(RTC_START_REG),7)
    sec = t[0]&0x7F
    min = t[1]&0x7F
    hour = t[2]&0x3F
    formatted_time = "{:02x}:{:02x}:{:02x}".format(hour, min, sec)
    return formatted_time

# RTC read current minute
def read_minute() -> int:
    t = rtc.readfrom_mem(int(RTC_ADDR),int(RTC_START_REG),7)
    min = t[1]&0x7F
    return min

# LCD control
def lcd_update():
     lcd.text('Bank', 25, 0, 1)
     lcd.text('Security', 10, 10, 1)
     if is_in_alarm:
          lcd.text('! ALARM !', 6, 25, 1)
     elif is_armed:
        lcd.text('ARMED', 15, 25, 1)
     elif is_entering:
        lcd.text('Entering', 10, 25, 1)
     else:
        lcd.text('UNARMED', 10, 25, 1)
     lcd.text(read_time(), 0, 38, 1)
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

print('Bank up and running...')

while True:
    try:
        ir_beam_triggered = is_beam_triggered()
        is_entering = ir_beam_triggered

        is_in_alarm = ir_beam_triggered and is_armed

        # sound buzzer if beam triggered
        if is_in_alarm == True:
            sound_buzzer(100, 0.1)

        lcd_update()
        lcd.fill(0)

        client.check_msg()
        utime.sleep(0.1)

    finally:
        pass

