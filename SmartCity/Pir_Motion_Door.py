import machine
import time

# Set up the PIR sensor connected to GP0 (Input)
motion_sensor_pin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)

# Set up the passive buzzer connected to GP5 (Output)
buzzer_pin = machine.Pin(5, machine.Pin.OUT)

# Define debounce time (in seconds)
debounce_time = 100  # 2000 milliseconds = 2 seconds
last_motion_time = 0  # Store the last time motion was detected

while True:
    # Read the current value of the PIR sensor
    motion_detected = motion_sensor_pin.value() == 0

    if motion_detected:
        # If motion is detected, check the time since the last motion
        current_time = time.ticks_ms()  # Get the current time in milliseconds
        if time.ticks_diff(current_time, last_motion_time) > debounce_time:  # Debounce time in milliseconds
            print("Motion detected!")
            buzzer_pin.value(1)  # Turn on the buzzer
            time.sleep(3)        # Buzzer will stay on for 1 second
            buzzer_pin.value(0)  # Turn off the buzzer
            last_motion_time = current_time  # Update the last motion time
    else:
        # No motion detected, ensure the buzzer is off
        buzzer_pin.value(0)

    time.sleep(0.1)  # Small delay to debounce the motion sensor


