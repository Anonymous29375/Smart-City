# Secure sockets layer (encryption and hashing) libraries
import ssl

# MQTT libraries for talking to Adafruit IO feeds
from umqtt.robust import MQTTClient

# Configuration settings for WIFI
from config import get_config_setting, get_config_setting_bytes_encoded

from bank_state import BankState

# Load config settings
ADAFRUIT_IO_URL = get_config_setting_bytes_encoded("mqtt_host")
ADAFRUIT_USERNAME = get_config_setting_bytes_encoded("mqtt_username")
ADAFRUIT_IO_KEY = get_config_setting_bytes_encoded("mqtt_key")
ADAFRUIT_IO_FEEDNAME = get_config_setting_bytes_encoded("mqtt_topic")

# Create feed names from MQTT topics
feed_topic = f'{get_config_setting("mqtt_username")}/feeds/{get_config_setting("mqtt_topic")}'.encode('utf-8')

# Create a client ID for MQTT
mqtt_client_id = 'the_secure_bank'
class AdafruitIO:
    def __init__(self, bank: BankState) -> None:
        self.bank = bank

    # The function that is called back when a topic update is received
    def mqtt_callback(self, topic, msg):
        # is_armed needs to be defined as a global as this is a callback method and not in normal file scope
        print(f"Received topic '{topic.decode('utf-8')}' with value '{msg.decode('utf-8')}'")
        if topic == feed_topic:
            self.bank.is_armed = msg == b'ON'


    def connect(self) -> MQTTClient | None:
        print(f"Connecting to MQTT as user '{ADAFRUIT_USERNAME.decode('utf-16')}'")
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.verify_mode = ssl.CERT_NONE
        client = MQTTClient(client_id=mqtt_client_id, 
                            server=ADAFRUIT_IO_URL, 
                            user=ADAFRUIT_USERNAME, 
                            password=ADAFRUIT_IO_KEY,
                            ssl=context)

        try:      
            client.connect()
            print(f"Connected to MQTT, subscribing to feed topic '{ADAFRUIT_IO_FEEDNAME.decode('utf-16')}'")
            mqtt_feedname = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, ADAFRUIT_IO_FEEDNAME), 'utf-8')    
            client.set_callback(self.mqtt_callback)                    
            client.subscribe(mqtt_feedname)  
            return client
        
        except Exception as e:
            print(f'Could not connect to MQTT server {ADAFRUIT_IO_URL.decode('utf-16')}{e}')
            return None