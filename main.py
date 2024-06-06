import json
import paho.mqtt.client as mqtt
import subprocess

import mysql_module

# MQTT-Broker-Einstellungen
broker_address = "192.168.56.1"  # Hier die IP-Adresse oder den Hostnamen deines MQTT-Brokers einfügen
broker_port = 1883  # Standard MQTT-Port




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




#values = (fechahora, G, Tc, I, V, P, Inst)
def check_threshold(values):
    thresholds = (12, 18, 22, 20, 30)

    for i in range(5):  # Assuming you want to iterate over the first 5 elements of values
        if values[i+1] > thresholds[i]:
            print(f"Value at index {i}: {values[i]} exceeds threshold at index {i}: {thresholds[i]}")


# Funktion zum Verarbeiten eingehender MQTT-Nachrichten
def on_message(client, userdata, message):
    # Nachricht im JSON-Format empfangen
    received_message = message.payload.decode('utf-8')

    # Die Nachricht in separate JSON-Objekte aufteilen (Annahme: Nachrichten sind durch Zeilenumbrüche getrennt)
    json_objects = received_message.strip().split('\n')

    # Jedes JSON-Objekt einzeln verarbeiten
    for json_str in json_objects:
        # JSON-Objekt laden
        received_json = json.loads(json_str)

        fechahora = received_json.get("FechaHora", None)
        G = received_json.get("G", None)
        Tc = received_json.get("Tc", None)
        I = received_json.get("I", None)
        V = received_json.get("V", None)
        P = received_json.get("P", None)
        Inst = received_json.get("Inst", None)
        # Werte für die zu füllenden Spalten
        values = (fechahora, G, Tc, I, V, P, Inst)
        mysql_module.send_to_mysql(values, "INSERT INTO pycharm_table (FechaHora, G, Tc, I, V, P, Inst) VALUES (%s, %s, %s, %s, %s, %s, %s)")
        check_threshold(values)

        # Hier kannst du die weiteren Schritte für die Verarbeitung der JSON-Daten einfügen
        # Zum Beispiel:
        print("Empfangene Nachricht:", received_json)

        # output, error = (
        #execute_bash_command(command, "test")
        # print("Output:", output)
        # print("Error:", error)
        # Verarbeitung der JSON-Daten ...


# MQTT-Client initialisieren
client = mqtt.Client()
client.on_message = on_message

# Mit dem Broker verbinden
client.connect(broker_address, broker_port)

# MQTT-Topic abonnieren, von dem du die Nachrichten empfangen möchtest
topic = "pv/data"
client.subscribe(topic)

# Endlosschleife, um eingehende Nachrichten zu verarbeiten
client.loop_forever()



