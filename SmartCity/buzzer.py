import utime
from machine import Pin

from pins import BUZZER_PIN

buzzer = Pin(BUZZER_PIN, Pin.OUT, 0)

def turn_off_buzzer():
     buzzer.value(0)  # Turn off the buzzer


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
