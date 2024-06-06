import json
import paho.mqtt.client as mqtt
import mysql.connector
import subprocess

# MQTT-Broker-Einstellungen
broker_address = "localhost"  # Hier die IP-Adresse oder den Hostnamen deines MQTT-Brokers einfügen
broker_port = 1883  # Standard MQTT-Port

# Verbindung zur MySQL-Datenbank herstellen
connection = mysql.connector.connect(
    host="localhost",  # Hostname des MySQL-Servers
    user="root",  # Benutzername für die Verbindung zur Datenbank
    password="IoTpw2024",  # Passwort für die Verbindung zur Datenbank
    database="test_jupyter_input"  # Name der Datenbank
)

# Cursor erstellen, um SQL-Abfragen auszuführen
cursor = connection.cursor()

# Command für die Ausführung
command = "websocat ws://localhost:8765"




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


def send_to_mysql(values):
    # SQL-Abfrage zum Einfügen eines Eintrags in die Tabelle
    insert_query = "INSERT INTO pycharm_table (FechaHora, G, Tc, I, V, P, Inst) VALUES (%s, %s, %s, %s, %s, %s, %s)"

    # SQL-Abfrage mit den Werten ausführen
    cursor.execute(insert_query, values)

    # Änderungen in der Datenbank bestätigen
    connection.commit()

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
        send_to_mysql(values)
        check_threshold(values)

        # Hier kannst du die weiteren Schritte für die Verarbeitung der JSON-Daten einfügen
        # Zum Beispiel:
        print("Empfangene Nachricht:", received_json)

        # output, error = (
        execute_bash_command(command, "test")
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

# Verbindung schließen
cursor.close()
connection.close()
