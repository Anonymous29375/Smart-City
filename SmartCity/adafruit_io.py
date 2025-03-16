# Secure sockets layer (encryption and hashing) libraries
import ssl

# MQTT libraries for talking to Adafruit IO feeds
from umqtt.robust import MQTTClient

# Configuration settings for WIFI
from config import get_config_setting

from bank_state import BankState

# Load config settings
ADAFRUIT_IO_URL = get_config_setting("mqtt_host")
ADAFRUIT_USERNAME = get_config_setting("mqtt_username")
ADAFRUIT_IO_KEY = get_config_setting("mqtt_key")

# Create feed names from MQTT topics
remote_arm_feed = f'{get_config_setting("mqtt_username")}/feeds/remote-arm'.encode('utf-8')
remote_alarm_feed = f'{get_config_setting("mqtt_username")}/feeds/alarm-status'.encode('utf-8')

# Create a client ID for MQTT
mqtt_client_id = 'the_secure_bank'
class AdafruitIO:
    def __init__(self, bank: BankState) -> None:
        self.bank = bank

    # The function that is called back when a topic update is received
    def mqtt_callback(self, topic, msg):
        print(topic, msg)
        # is_armed needs to be defined as a global as this is a callback method and not in normal file scope
        if topic == remote_arm_feed:
            self.bank.is_remote_armed = msg == b'ON'


    def connect(self) -> bool:
        print(f"Connecting to MQTT as user '{ADAFRUIT_USERNAME}'")
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.verify_mode = ssl.CERT_NONE
        self.client = MQTTClient(client_id=mqtt_client_id, 
                            server=ADAFRUIT_IO_URL, 
                            user=ADAFRUIT_USERNAME, 
                            password=ADAFRUIT_IO_KEY,
                            ssl=context)

        try:      
            self.client.connect()
            print(f"Connected to MQTT, subscribing to feed 'Remote Arm'")
            mqtt_feedname = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, b'remote-arm'), 'utf-8')    
            self.client.set_callback(self.mqtt_callback)                    
            self.client.subscribe(mqtt_feedname)  

            return True
        
        except Exception as e:
            print(f'Could not connect to MQTT server {ADAFRUIT_IO_URL}{e}')
            return False
        
    def check_msg(self) -> None:
        self.client.check_msg()

    def send_alarm_update(self):
        if self.bank.in_alarm:
            self.client.publish(remote_alarm_feed, b'bell')
        else:
            self.client.publish(remote_alarm_feed, b'bell-slash')