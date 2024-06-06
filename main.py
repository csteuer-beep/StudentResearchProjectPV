import json
import paho.mqtt.client as mqtt
import subprocess

import mysql_module
import mqtt_handler

# MQTT-Broker-Einstellungen
broker_address = "192.168.56.1"  # Hier die IP-Adresse oder den Hostnamen deines MQTT-Brokers einfügen
broker_port = 1883  # Standard MQTT-Port
topic = "pv/data"




# Command für die Ausführung
command = "websocat ws://192.168.56.1:8765"




def execute_bash_command(comm, message):
    # Execute the command
    process = subprocess.Popen(comm, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Send a message
    process.stdin.write(message.encode())
    process.stdin.flush()

    # Optionally, you can read the output
    # output, error = process.communicate()

    process.stdin.close()

    # Return the output and error if any
    # return process #output.decode(), error.decode()



# Start the MQTT client
mqtt_handler.start_mqtt_client(broker_address, broker_port, topic)




