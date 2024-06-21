# mqtt_module.py
import json
import paho.mqtt.client as mqtt
import mysql_module
import alerting_module


def process_message(received_json):
    fechahora = received_json.get("FechaHora", None)
    G = received_json.get("G", None)
    Tc = received_json.get("Tc", None)
    I = received_json.get("I", None)
    V = received_json.get("V", None)
    P = received_json.get("P", None)
    Inst = received_json.get("Inst", None)
    values = (fechahora, G, Tc, I, V, P, Inst)
    return values

def on_message(client, userdata, message):
    # Nachricht im JSON-Format empfangen

    received_message = message.payload.decode('utf-8')


    # Die Nachricht in separate JSON-Objekte aufteilen (Annahme: Nachrichten sind durch Zeilenumbrüche getrennt)
    json_objects = received_message.strip().split('\n')

    # Jedes JSON-Objekt einzeln verarbeiten
    for json_str in json_objects:
        # JSON-Objekt laden
        received_json = json.loads(json_str)
        print("Empfangene Nachricht:", received_json)

        # Process the JSON and get the values
        values = process_message(received_json)

        # Send the values to the MySQL database
        mysql_module.send_to_mysql_raw(values, "INSERT INTO pycharm_table (FechaHora, G, Tc, I, V, P, Inst) VALUES (%s, %s, %s, %s, %s, %s, %s)")
        print("Timestamp before MySQL operation:", values[0])
        # Hier kannst du die weiteren Schritte für die Verarbeitung der JSON-Daten einfügen


        alerts = alerting_module.check_threshold(values)
        print(alerts)

        # check_threshold(values) # Assuming you have a check_threshold function

def get_message(self):
    return self.received_message


def start_mqtt_client(broker_address, broker_port, topic):
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(broker_address, broker_port)
    client.subscribe(topic)
    client.loop_forever()
