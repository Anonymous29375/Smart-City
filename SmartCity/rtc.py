from machine import I2C

# RTC values
RTC_ADDR = 0x68
RTC_START_REG = 0x00

class RTC:
    def __init__(self, i2c: I2C):
        self.i2c = i2c

    # RTC read date and time
    def read_date_time(self) -> str:
        t = self.i2c.readfrom_mem(int(RTC_ADDR),int(RTC_START_REG),7)
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
    def read_time(self) -> str:
        t = self.i2c.readfrom_mem(int(RTC_ADDR),int(RTC_START_REG),7)
        sec = t[0]&0x7F
        min = t[1]&0x7F
        hour = t[2]&0x3F
        formatted_time = "{:02x}:{:02x}:{:02x}".format(hour, min, sec)
        return formatted_time

    # RTC read current minute
    def read_minute(self) -> int:
        t = self.i2c.readfrom_mem(int(RTC_ADDR),int(RTC_START_REG),7)
        min = t[1]&0x7F
        return min