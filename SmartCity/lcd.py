# Hardware related libraries
from machine import Pin, SPI, I2C

# LCD library for wall display
from pcd8544_fb import PCD8544_FB

# Pins used for LCD
from pins import LCD_MOSI_PIN, LCD_SCK_PIN, LCD_CS_PIN, LCD_DC_PIN, LCD_RST_PIN, LCD_BL_PIN

from rtc import RTC

from bank_state import BankState

# The LCD frame buffer library is fixed at 8x8 font
# So for the 84x48 screen that means:
#   84/8 = 10 full characters (columns) in X direction
#   48/8 = 6 full characters (rows) in Y direction
CHARACTER_SIZE = 8

# Because X is 84 pixels wide and we can only have 10 characters it means there are 2 pixels either end of X
X_PADDING = 2

LCD_COLUMNS = 10
LCD_ROWS = 6

LINE_1 = 0
LINE_2 = 1
LINE_3 = 2
LINE_4 = 3
LINE_5 = 4
LINE_6 = 5

# Monochrome LCD so only dark color defined
LCD_DARK_COLOR = 1

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

    def update_display(self):
        self.lcd.clear()
        self.lcd.show()
        self.lcd.fill(0)

    def center_text(self, text: str, line: int) -> None:
        # Get length of text
        txt_len = len(text)

        # Work out how much padding left and right of text
        padding_total = LCD_COLUMNS - txt_len

        # Default to X_PADDING
        padding_left = X_PADDING

        # if there is no padding then just display starting at X_PADDING
        if padding_total > 0:
            # Left padding is half of total paddding
            padding_chars_left = float(padding_total) / 2.0
            padding_left = X_PADDING + int(padding_chars_left * CHARACTER_SIZE)
        
        self.lcd.text(text, padding_left, line * CHARACTER_SIZE, LCD_DARK_COLOR)

    def update_initialising(self, line2: str | None = None, line3: str | None = None) -> None:
        self.center_text('Initialise:', LINE_1)
        
        if line2 is not None:
            self.center_text(line2, LINE_2)

        if line3 is not None:
            self.center_text(line3, LINE_3)
        
        self.update_display()

    def update_state(self, rtc: RTC, bank: BankState):
        self.center_text('Bank', LINE_1)
        self.center_text('Security', LINE_2)
        if bank.in_alarm:
            self.center_text('! ALARM !', LINE_3)
        elif bank.is_armed:
            self.center_text('ARMED', LINE_3)
        elif bank.beam_triggered:
            self.center_text('Entering', LINE_3)
        else:
            self.center_text('UNARMED', LINE_3)

        if bank.door_open:
            self.center_text('Safe Open', LINE_4)
        else:
            self.center_text('Safe Close', LINE_4)

        date_time = rtc.get_date_time()

        self.center_text(f"{date_time.hour}:{date_time.minute}:{date_time.second}", LINE_5)
        self.center_text(f"{date_time.year}/{date_time.month}/{date_time.day}", LINE_6)
        self.update_display()
