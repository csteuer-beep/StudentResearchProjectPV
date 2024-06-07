# main.py
import asyncio

import bash_command_handler
import mqtt_handler
import subprocess
import os

# MQTT-Broker-Einstellungen
broker_address = "localhost" #"192.168.56.1"  # Hier die IP-Adresse oder den Hostnamen deines MQTT-Brokers einfügen
broker_port = 1883  # Standard MQTT-Port
topic = "pv/data"

uri = "ws://localhost:8765/alerts"
client = bash_command_handler.WebSocketClient(uri)
asyncio.get_event_loop().run_until_complete(client.connect())

# Start the MQTT client
mqtt_handler.start_mqtt_client(broker_address, broker_port, topic)

asyncio.get_event_loop().run_until_complete(client.close())



