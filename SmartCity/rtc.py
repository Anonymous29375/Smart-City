from machine import I2C


# RTC values
RTC_ADDR = 0x68
RTC_START_REG = 0x00

class DateTime:
    def __init__(self, year: int, month: int, day: int, hour: int, minute: int, second: int, weekday: int) -> None:
        # Default to Thursday 1 Jan 1970 00:00:00 
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.weekday = weekday

class RTC:
    def __init__(self, i2c: I2C):
        self.i2c = i2c

    # RTC read date and time
    def get_date_time(self) -> DateTime:
        # Read date and time from RTC chip in I2C bus, 7 bytes in total
        # Bytes are returnd as binary coded decimal (BCD)
        date_time_bytes = self.i2c.readfrom_mem(int(RTC_ADDR),int(RTC_START_REG),7)
        
        # Get the date time parts
        second = self.bcd_to_int(date_time_bytes[0]&0x7F)
        minute = self.bcd_to_int(date_time_bytes[1]&0x7F)
        hour = self.bcd_to_int(date_time_bytes[2]&0x3F)
        weekday = self.bcd_to_int(date_time_bytes[3]&0x07)
        day = self.bcd_to_int(date_time_bytes[4]&0x3F)
        month = self.bcd_to_int(date_time_bytes[5]&0x1F)
        year = self.bcd_to_int(date_time_bytes[6]&0xFF)
        
        # Year 0 == actual year 2000, so add 2000 to year
        return DateTime(2000 + year, month, day, hour, minute, second, weekday)
    
    def bcd_to_int(self, bcd: int) -> int:
        formatted = f"{bcd:02X}"
        return int(formatted, 10)