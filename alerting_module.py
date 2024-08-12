# alert_module.py
import asyncio
import datetime
import uuid
import json
import websocket_handler
import mysql_module


uri = "ws://localhost:8765/alerts" #"ws://192.168.56.1:8765/alerts"
client = websocket_handler.WebSocketClient(uri)



def get_parameter_name(index):
    parameters = ["", "G", "Tc", "I", "V", "P"]
    return parameters[index]

def handle_existing_alert(alert_id, timestamp, value, closing=False):
    if closing:
        mysql_module.update_field("Alerts", "AlertStatus", "Closed", "AlertID", alert_id)
        mysql_module.update_field("Alerts", "Currentvalue", value, "AlertID", alert_id)
    else:
        mysql_module.update_field("Alerts", "LastOccurrenceTimestamp", timestamp, "AlertID", alert_id)
        mysql_module.update_field("Alerts", "Currentvalue", value, "AlertID", alert_id)

def handle_new_alert(sensor_id, message, parameter, cuvalue, timestamp):
    print("No open alert with matching instance and parameter value found")
    send_alert_to_database(sensor_id, message, parameter, cuvalue, timestamp)

def check_threshold(values):
    asyncio.get_event_loop().run_until_complete(client.connect())
    thresholds = (20, 20, 20, 20, 20)
    alerts = []
    timestamp = values[0]

    for i in range(1, 6):  # Start from index 1 to skip the first element (assuming it's the timestamp)
        value = values[i]
        if value is not None:
            parameter = get_parameter_name(i)
            if value > thresholds[i - 1]:  # Check if value exceeds threshold
                message = f"Parameter {parameter}: {value} exceeds threshold {thresholds[i - 1]}"
                websocket_message = generate_alertjson(parameter, thresholds[i - 1], message, value, timestamp, values[6])
                alerts.append(message)
                print(alerts)
                existing_alert = mysql_module.get_open_alert_id(values[6], parameter)

                if existing_alert is not None:
                    print(f"An open alert with AlertID {existing_alert} already exists")
                    handle_existing_alert(existing_alert, timestamp, value)
                else:
                    handle_new_alert(values[6], message, parameter, value, timestamp)

                asyncio.get_event_loop().run_until_complete(client.send_message(websocket_message))
            elif value < thresholds[i - 1]:  # Check if value falls below threshold
                message = f"Parameter {parameter}: {value} is below threshold {thresholds[i - 1]}"
                alerts.append(message)
                print(alerts)
                existing_alert = mysql_module.get_open_alert_id(values[6], parameter)

                if existing_alert is not None:
                    print(f"An open alert with AlertID {existing_alert} already exists")
                    handle_existing_alert(existing_alert, timestamp, value, closing=True)


    return alerts

def generate_alertjson(parameter, threshold, message, value, timestamp, inst ):
    data = {
        "Timestamp": timestamp,
        "Parameter": parameter,
        "Threshold": threshold,
        "AlertMessage": message,
        "CurrentValue": value,
        "Inst": inst
    }

    return json.dumps(data)

def send_alert_to_database(sensor_id, message, parameter, cuvalue, timestamp):
    print("Timestamp before MySQL operation:", timestamp)
    alert_id = generate_alert_id()
    alert_type = "Threshold Exceeded"
    alert_status = "Open"
    first_occurrence_timestamp = timestamp
    last_occurrence_timestamp = timestamp

    print("Alert UUID:", alert_id)

    insert_query = """
    INSERT INTO Alerts 
    (AlertID, SensorID, Timestamp, AlertType, AlertMessage, AlertStatus, FirstOccurrenceTimestamp, LastOccurrenceTimestamp, Parameter, CurrentValue) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (alert_id, sensor_id, timestamp, alert_type, message, alert_status, first_occurrence_timestamp, last_occurrence_timestamp, parameter, cuvalue)
    mysql_module.insert_to_mysql_alert(values, insert_query)



def generate_alert_id():
    return str(uuid.uuid4())
