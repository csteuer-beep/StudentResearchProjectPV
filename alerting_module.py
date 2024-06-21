# alert_module.py
import asyncio
import datetime
import uuid
import json
import websocket_handler
import mysql_module


uri = "ws://192.168.56.1:8765/alerts"
client = websocket_handler.WebSocketClient(uri)



def get_parameter_name(index):
    parameters = ["", "G", "Tc", "I", "V", "P"]
    return parameters[index]

def handle_existing_alert(alert_id, timestamp, value, closing=False):
    if closing:
        mysql_module.update_field("alerts", "AlertStatus", "Closed", "AlertID", alert_id)
        mysql_module.update_field("alerts", "Currentvalue", value, "AlertID", alert_id)
    else:
        mysql_module.update_field("alerts", "LastOccurrenceTimestamp", timestamp, "AlertID", alert_id)
        mysql_module.update_field("alerts", "Currentvalue", value, "AlertID", alert_id)

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

               # asyncio.get_event_loop().run_until_complete(client.send_message(websocket_message))
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
    INSERT INTO alerts 
    (AlertID, SensorID, Timestamp, AlertType, AlertMessage, AlertStatus, FirstOccurrenceTimestamp, LastOccurrenceTimestamp, Parameter, CurrentValue) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (alert_id, sensor_id, timestamp, alert_type, message, alert_status, first_occurrence_timestamp, last_occurrence_timestamp, parameter, cuvalue)
    mysql_module.insert_to_mysql_alert(values, insert_query)



def generate_alert_id():
    return str(uuid.uuid4())


'''
import mysql_module
import datetime

def check_threshold(values):
    thresholds = (12, 18, 2.5, 1.5, 30)
    alerts = []

    for i in range(1, 6):  # Start from index 1 to skip the first element (assuming it's the timestamp)
        value = values[i]
        timestamp = values[0]  # datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if value is not None and value > thresholds[i - 1]:

            if i == 1:
                parameter = "G"
            elif i == 2:
                parameter = "Tc"
            elif i == 3:
                parameter = "I"
            elif i == 4:
                parameter = "V"
            elif i == 5:
                parameter = "P"

            CuValue = values[i]

            message = f"Parameter {parameter}: {value} exceeds threshold {thresholds[i - 1]}"
            alerts.append(message)
            existing_alert = mysql_module.get_open_alert_id(values[6], parameter)
            if existing_alert is not None:
                # Es existiert bereits ein offener Alert mit übereinstimmendem Inst- und Parameter-Wert
                print(f"Es existiert bereits ein offener Alert mit AlertID {existing_alert}")
                # Last Occurrence
                mysql_module.update_field("alerts", "LastOccurrenceTimestamp", f"{timestamp}", "AlertID", f"{existing_alert}")
                # new Value
                mysql_module.update_field("alerts", "Currentvalue", f"{value}", "AlertID", f"{existing_alert}")


                # Führe hier weitere Aktionen aus, die bei einem vorhandenen Alert durchgeführt werden sollen
            elif existing_alert is None:
                # Es wurde kein offener Alert mit übereinstimmendem Inst- und Parameter-Wert gefunden
                print("Es wurde kein offener Alert mit übereinstimmendem Inst- und Parameter-Wert gefunden")
                send_alert_to_database(values[6], message, parameter, CuValue, values[0])

            else:
                print("Error while checking existing Alert Entries")

        elif value is not None and value < thresholds[i - 1]:

            if i == 1:
                parameter = "G"
            elif i == 2:
                parameter = "Tc"
            elif i == 3:
                parameter = "I"
            elif i == 4:
                parameter = "V"
            elif i == 5:
                parameter = "P"

            CuValue = values[i]

            message = f"Parameter {parameter}: {value} exceeds threshold {thresholds[i - 1]} but under it"
            alerts.append(message)
            existing_alert = mysql_module.get_open_alert_id(values[6], parameter)
            if existing_alert is not None:
                # Es existiert bereits ein offener Alert mit übereinstimmendem Inst- und Parameter-Wert
                print(f"Es existiert bereits ein offener Alert mit AlertID {existing_alert}")
                # Last Occurrence
                mysql_module.update_field("alerts", "LastOccurrenceTimestamp", f"{timestamp}", "AlertID",
                                          f"{existing_alert}")
                # new Value
                mysql_module.update_field("alerts", "AlertStatus", "Closed", "AlertID", f"{existing_alert}")

                # Führe hier weitere Aktionen aus, die bei einem vorhandenen Alert durchgeführt werden sollen
            elif existing_alert is None:
                # Es wurde kein offener Alert mit übereinstimmendem Inst- und Parameter-Wert gefunden
                print("Es wurde kein offener Alert mit übereinstimmendem Inst- und Parameter-Wert gefunden")
                #send_alert_to_database(values[6], message, parameter, CuValue)

            else:
                print("Error while checking existing Alert Entries")


    return alerts


def send_alert_to_database(sensor_id, message, parameter, cuvalue, timestamp):
    #timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print("Timestamp before MySQL operation:", timestamp)
    alert_id = generate_alert_id()
    alert_type = "Threshold Exceeded"
    alert_status = "Open"
    first_occurrence_timestamp = timestamp
    last_occurrence_timestamp = timestamp

    print("Alert UUID:", alert_id)

    insert_query = "INSERT INTO alerts (AlertID, SensorID, Timestamp, AlertType, AlertMessage, AlertStatus, FirstOccurrenceTimestamp, LastOccurrenceTimestamp, Parameter, CurrentValue) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (alert_id, sensor_id, timestamp, alert_type, message, alert_status, first_occurrence_timestamp, last_occurrence_timestamp, parameter, cuvalue)
    mysql_module.insert_to_mysql_alert(values, insert_query)

def generate_alert_id():
    # You can use a unique identifier for the AlertID.
    # Using current timestamp as AlertID might result in collision if multiple alerts occur simultaneously.
    # Using an auto-increment column in the database table is a safer approach, but you can also generate
    # a UUID or a combination of timestamp and some random number for AlertID.
    # Here, I'll generate a UUID as an example:
    import uuid
    return str(uuid.uuid4()) '''
