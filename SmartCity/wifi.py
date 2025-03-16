# Time libraries
import utime

# Import network libraries
import network

# Configuration settings for WIFI
from config import get_config_setting

WIFI_SSID = get_config_setting("wifi_ssid")
WIFI_PASSWORD = get_config_setting("wifi_password")
WIFI_MAX_CONNECT_ATTEMPTS = 20


def wifi_connect() -> bool:
    try:
        # Connect to WIFI
        print(f"Connecting to WIFI: '{WIFI_SSID}'")
        wifi = network.WLAN(network.STA_IF)
        wifi.active(True)
        wifi.connect(WIFI_SSID, WIFI_PASSWORD)

        # Wait until the device is connected to the WiFi network
        connect_attempt_count = 0
        while not wifi.isconnected() and connect_attempt_count < WIFI_MAX_CONNECT_ATTEMPTS:
            # Increment connect count
            connect_attempt_count += 1 

            # Sleep for a second to give more time for WIFI to connecct
            utime.sleep(1)
 
        # Were we able to connect?
        if not wifi.isconnected():
            print(f"Could not connect to the WiFi: '{WIFI_SSID}'")
        else:
            print(f"Connected to  WIFI: '{WIFI_SSID}'")

        return True
    except:
        print(f"Failed to connect to WIFI: '{WIFI_SSID}'")
        return False
