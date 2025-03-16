# Hardware related libraries
from machine import Pin, SPI, I2C

# LCD library for wall display
from pcd8544_fb import PCD8544_FB

# Pins used for LCD
from pins import LCD_MOSI_PIN, LCD_SCK_PIN, LCD_CS_PIN, LCD_DC_PIN, LCD_RST_PIN, LCD_BL_PIN

from rtc import RTC

from bank_state import BankState


class LCD:
    def __init__(self):
        # LCD set up using SPI
        self.lcd_spi = SPI(0, mosi=Pin(LCD_MOSI_PIN), sck=Pin(LCD_SCK_PIN))
        self.lcd_spi.init(baudrate=2000000, polarity=0, phase=0) # type: ignore
        self.lcd_cs = Pin(LCD_CS_PIN)
        self.lcd_dc = Pin(LCD_DC_PIN)
        self.lcd_rst = Pin(LCD_RST_PIN)
        self.lcd_back_light = Pin(LCD_BL_PIN, Pin.OUT, value=1)
        self.lcd = PCD8544_FB(self.lcd_spi, self.lcd_cs, self.lcd_dc, self.lcd_rst)
        self.bank = bank


    # LCD control
    def update(self, rtc: RTC, bank: BankState):
        self.lcd.text('Bank', 25, 0, 1)
        self.lcd.text('Security', 10, 8, 1)
        if bank.in_alarm:
            self.lcd.text('! ALARM !', 6, 16, 1)
        elif bank.is_armed:
            self.lcd.text('ARMED', 15, 16, 1)
        elif bank.beam_triggered:
            self.lcd.text('Entering', 10, 16, 1)
        else:
            self.lcd.text('UNARMED', 10, 16, 1)

        if bank.door_open:
            self.lcd.text('door open', 10, 24, 1)
        else:
            self.lcd.text('door closed', 10, 24, 1)

        self.lcd.text(rtc.read_time(), 0, 32, 1)
        self.lcd.clear()
        self.lcd.show()
        self.lcd.fill(0)
