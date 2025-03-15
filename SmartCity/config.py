config = {
    "wifi_ssid": "%SSID%",
    "wifi_password": "%PASSWORD%",
    "mqtt_host": "%HOST%",
    "mqtt_username": "%USER%",
    "mqtt_key": "%KEY%",
    "mqtt_topic": "%TOPIC%"
}

def get_config_setting(name: str) -> str:
    return config[name]

def get_config_setting_bytes_encoded(name: str) -> bytes:
    return get_config_setting(name).encode('utf-8')
