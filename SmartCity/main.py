# python imports
import pcd8544_fb
from machine import Pin, SPI
import utime

# pin numbers

IR_BEAM_PIN = 0

LCD_DC_PIN = 4
LCD_CS_PIN = 5
LCD_SCK_PIN = 6
LCD_MOSI_PIN = 7
LCD_RST_PIN = 8
LCD_BL_PIN = 9

BUZZER_PIN = 28

# setup

ir_beam = Pin(IR_BEAM_PIN, Pin.IN, Pin.PULL_UP)
buzzer = Pin(BUZZER_PIN, Pin.OUT)

# LCD set up using SPI
lcd_spi = SPI(0, mosi=Pin(LCD_MOSI_PIN), sck=Pin(LCD_SCK_PIN))
lcd_spi.init(baudrate=2000000, polarity=0, phase=0)
lcd_cs = Pin(LCD_CS_PIN)
lcd_dc = Pin(LCD_DC_PIN)
lcd_rst = Pin(LCD_RST_PIN)
lcd_back_light = Pin(LCD_BL_PIN, Pin.OUT, value=1)
lcd = pcd8544_fb.PCD8544_FB(lcd_spi, lcd_cs, lcd_dc, lcd_rst)

is_in_alarm = False

# LCD control
def lcd_update(is_in_alarm):
     lcd.text('Bank', 25, 0, 1)
     lcd.text('Security', 10, 10, 1)
     if is_in_alarm:
          lcd.text('! ALARM !', 6, 30, 1)
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


while True:
    try:
        ir_beam_triggered = is_beam_triggered()

        # sound buzzer if beam triggered
        if ir_beam_triggered == True:
            sound_buzzer(100, 0.1)

        is_in_alarm = ir_beam_triggered

        lcd_update(is_in_alarm)
        lcd.fill(0)

        utime.sleep(0.1)

    finally:
        pass

