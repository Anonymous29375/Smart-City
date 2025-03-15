import machine
import time

# Set up the GPIO pin for the passive buzzer
BUZZER_PIN = 28  # You can change this to the pin you're using

# Create a Pin object for the buzzer
buzzer = machine.Pin(BUZZER_PIN, machine.Pin.OUT)

# Function to play a tone on the buzzer
def buzz(frequency, duration):
    period = 1.0 / frequency  # Calculate period (time for one cycle)
    half_period = period / 2
    end_time = time.ticks_ms() + (duration * 1000)  # Convert duration to milliseconds

    while time.ticks_ms() < end_time:
        buzzer.value(1)  # Turn on the buzzer
        time.sleep(half_period)
        buzzer.value(0)  # Turn off the buzzer
        time.sleep(half_period)

try:
    # Example usage: Play a 1000 Hz tone for 1 second
    print("Buzzer is on!")
    buzz(1000, 1)
    print("Buzzer finished!")

finally:
    pass  # No need for cleanup in MicroPython, just let the program exit


