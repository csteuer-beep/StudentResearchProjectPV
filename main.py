# main.py

import bash_command_handler
import mqtt_handler

# MQTT-Broker-Einstellungen
broker_address = "192.168.56.1"  # Hier die IP-Adresse oder den Hostnamen deines MQTT-Brokers einfügen
broker_port = 1883  # Standard MQTT-Port
topic = "pv/data"

# Command für die Ausführung
command = "websocat ws://192.168.56.1:8765"

# Function call
bash_command_handler.execute_bash_command(command, "Your message here")

# Start the MQTT client
mqtt_handler.start_mqtt_client(broker_address, broker_port, topic)
