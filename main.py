import json
import paho.mqtt.client as mqtt
import mysql.connector

# Verbindung zur MySQL-Datenbank herstellen
connection = mysql.connector.connect(
    host="localhost",  # Hostname des MySQL-Servers
    user="root",  # Benutzername für die Verbindung zur Datenbank
    password="IoTpw2024",  # Passwort für die Verbindung zur Datenbank
    database="test_jupyter_input"  # Name der Datenbank
)


# Cursor erstellen, um SQL-Abfragen auszuführen

def sendtomysql(values):
    cursor = connection.cursor()
    # SQL-Abfrage zum Einfügen eines Eintrags in die Tabelle
    insert_query = "INSERT INTO jupyter_table (FechaHora, G, Tc, I, V, P, Inst) VALUES (%s, %s, %s, %s, %s, %s, %s)"

    # SQL-Abfrage mit den Werten ausführen
    cursor.execute(insert_query, values)

    # Änderungen in der Datenbank bestätigen
    connection.commit()

    cursor.close()


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
        sendtomysql(values)

        # Hier kannst du die weiteren Schritte für die Verarbeitung der JSON-Daten einfügen
        # Zum Beispiel:
        print("Empfangene Nachricht:", received_json)
        # Verarbeitung der JSON-Daten ...


# MQTT-Broker-Einstellungen
broker_address = "localhost"  # Hier die IP-Adresse oder den Hostnamen deines MQTT-Brokers einfügen
broker_port = 1883  # Standard MQTT-Port

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

connection.close()