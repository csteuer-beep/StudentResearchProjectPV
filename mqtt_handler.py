# mqtt_module.py
import asyncio
from datetime import datetime, timedelta
import json
import paho.mqtt.client as mqtt
import alerting_module
import websocket_handler

uri = "ws://localhost:8765/alerts" #"ws://192.168.56.1:8765/alerts"
client = websocket_handler.WebSocketClient(uri)

def process_message(received_json):
    fechahora = received_json.get("FechaHora", None)
    G = received_json.get("G", None)
    Tc = received_json.get("Tc", None)
    I = received_json.get("I", None)
    V = received_json.get("V", None)
    P = received_json.get("P", None)
    Inst = received_json.get("Inst", None)

    if fechahora:
        # Parse the date-time string into a datetime object
        fechahora_dt = datetime.strptime(fechahora, "%Y-%m-%dT%H:%M:%S")
        # Subtract 2 hours to convert from UTC+2 to UTC+0
        fechahora_dt = fechahora_dt - timedelta(hours=2)
        # Format back to string if needed, e.g., fechahora = fechahora_dt.strftime("%Y-%m-%dT%H:%M:%S")
        fechahora = fechahora_dt.isoformat()

    new_value = 0
    V = 0
    if Inst == "etsist1":
        V = 5.5
    if Inst == "etsist2":
        V = 4.8
    new_value = G * V * (1 - 0.0035 * (Tc - 25))
    performance = new_value / 1000
    try:
        loss = max(0, P - performance) if P is not None else 0
    except Exception as e:
        loss = performance

    values = (fechahora, G, Tc, I, V, P, Inst, performance, loss)

    alert_value1 = 1 if G < 10 else 0
    alert_value2 = 1 if abs((new_value - P) / new_value) > 0.25 else 0
    # Simple threshold check for performance
    performance_threshold = 20  # Example threshold value



    if alert_value1 == 1 :
        message = f"G, Tc sensor is offline. G: {G} , Tc:  {Tc}"
        websocket_message = alerting_module.generate_alertjson("Sensor Offline", 1, message, G, fechahora,
                                                               Inst)
        asyncio.get_event_loop().run_until_complete(client.connect())
        asyncio.get_event_loop().run_until_complete(client.send_message(websocket_message))

        # Send alert to MySQL database
        alerting_module.send_alert_to_database(Inst, message, "performance", performance, fechahora)

    return values


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

