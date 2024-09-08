# mqtt_module.py
import json
import os
import re
from datetime import datetime, timedelta
from decimal import Decimal

import paho.mqtt.client as mqtt

import mysql_module

def is_numeric(value):
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def process_message(received_json):
    def matches_pattern(value, pattern):
        return re.match(pattern, str(value)) is not None

    # Define patterns for specific fields
    patterns = {
        "FechaHora": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$",  # ISO datetime pattern
    }

    # Process each value in the received JSON
    processed_values = {}
    for key, value in received_json.items():
        if key == "FechaHora":
            if not matches_pattern(value, patterns[key]):
                processed_values[key] = None
            else:
                processed_values[key] = value
        elif key == "Inst":
            if not isinstance(value, str):
                processed_values[key] = None
            else:
                processed_values[key] = value
        else:
            # Handle numeric fields
            if not is_numeric(value):
                processed_values[key] = None
            else:
                processed_values[key] = float(value)

    fechahora = processed_values.get("FechaHora", None)
    G = processed_values.get("G", None)
    Tc = processed_values.get("Tc", None)
    I = processed_values.get("I", None)
    V = processed_values.get("V", None)
    P = processed_values.get("P", None)
    Inst = processed_values.get("Inst", None)

    # Convert the date-time string to UTC+0
    if fechahora:
        fechahora_dt = datetime.strptime(fechahora, "%Y-%m-%dT%H:%M:%S")
        fechahora_dt = fechahora_dt - timedelta(hours=2)
        fechahora = fechahora_dt.isoformat()

    # Get efficiency coefficient
    coef = mysql_module.get_efficiency_coefficient(Inst)

    # Calculate performance and loss
    if G is not None and Tc is not None and coef is not None:
        performance = G * float(Decimal(coef)) * (1 - 0.0035 * (Tc - 25))
        performance /= 1000
        loss = max(0, P - performance) if P is not None else performance
    else:
        performance = 0
        loss = 0

    values = (fechahora, G, Tc, I, V, P, Inst, performance, loss)

    return values

def on_message(client, userdata, message):
    received_message = message.payload.decode('utf-8')
    json_objects = received_message.strip().split('\n')
    values_list = []

    for json_str in json_objects:
        json_str = json_str.strip()  # Remove leading/trailing whitespace
        if json_str:  # Check if the string is not empty
            print(f"Raw JSON string: {json_str}")
            try:
                received_json = json.loads(json_str)
                print("Received message:", received_json)
                values = process_message(received_json)
                values_list.append(values)
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON: {e}. Skipping this entry.")
                continue

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

