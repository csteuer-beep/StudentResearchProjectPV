# mqtt_module.py
import json
import os
from datetime import datetime, timedelta
from decimal import Decimal

import paho.mqtt.client as mqtt

import mysql_module


# Function to process the received JSON message splitting it into individual values
def process_message(received_json):
    fechahora = received_json.get("FechaHora", None)
    G = received_json.get("G", None)
    Tc = received_json.get("Tc", None)
    I = received_json.get("I", None)
    V = received_json.get("V", None)
    P = received_json.get("P", None)
    Inst = received_json.get("Inst", None)

    # Convert the date-time string to UTC+0

    if fechahora:
        # Parse the date-time string into a datetime object
        fechahora_dt = datetime.strptime(fechahora, "%Y-%m-%dT%H:%M:%S")
        # Subtract 2 hours to convert from UTC+2 to UTC+0
        fechahora_dt = fechahora_dt - timedelta(hours=2)
        # Format back to string if needed, e.g., fechahora = fechahora_dt.strftime("%Y-%m-%dT%H:%M:%S")
        fechahora = fechahora_dt.isoformat()


    # Calculate performance and loss
    coef = mysql_module.get_efficiency_coefficient(Inst)
    performance = G * float(Decimal(coef)) * (1 - 0.0035 * (Tc - 25)) if G is not None and coef is not None else 0
    performance /= 1000
    loss = max(0, P - performance) if P is not None else performance

    values = (fechahora, G, Tc, I, V, P, Inst, performance, loss)

    return values

# Function to handle the received MQTT message
def on_message(client, userdata, message):
    received_message = message.payload.decode('utf-8')
    json_objects = received_message.strip().split('\n')
    values_list = []

    for json_str in json_objects:
        received_json = json.loads(json_str)
        print("Received message:", received_json)
        values = process_message(received_json)
        values_list.append(values)

    # Pass the processed values to the callback function
    userdata['callback'](values_list)


def start_mqtt_client(broker_address, broker_port, topic, callback):
    client = mqtt.Client(userdata={'callback': callback})
    client.on_message = on_message
    client.connect(broker_address, broker_port)
    client.subscribe(topic)
    client.loop_forever()


def connection_exists(file_path):
    return os.path.exists(file_path)


def create_connection_file(file_path):
    with open(file_path, 'w') as f:
        f.write('connected')
