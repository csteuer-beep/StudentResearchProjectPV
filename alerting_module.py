# alert_module.py
import asyncio
import datetime
import uuid
import json
import websocket_handler
import mysql_module
from decimal import Decimal

uri = "ws://localhost:8765/alerts"
client = websocket_handler.WebSocketClient(uri)


def get_parameter_name(index):
    parameters = ["", "G", "Tc", "I", "V", "P"]
    return parameters[index]


def handle_existing_alert(alert_id, timestamp, value, closing=False):
    if closing:
        # close the alert
        mysql_module.update_field("Alerts", "AlertStatus", "Closed", "AlertID", alert_id)
        mysql_module.update_field("Alerts", "Currentvalue", value, "AlertID", alert_id)
    else:
        #update last occurrence timestamp and current value
        mysql_module.update_field("Alerts", "LastOccurrenceTimestamp", timestamp, "AlertID", alert_id)
        mysql_module.update_field("Alerts", "Currentvalue", value, "AlertID", alert_id)


def handle_new_alert(sensor_id, message, parameter, cuvalue, timestamp):
    print("No open alert with matching instance and parameter value found")
    send_alert_to_database(sensor_id, message, parameter, cuvalue, timestamp)


def handle_offline_alert(G, Tc, fechahora, Inst):
    if G is not None and G < 10:
        message = f"G, Tc sensor is offline. G: {G} , Tc: {Tc}"
        websocket_message = generate_alertjson("G/Tc", 1, message, G, fechahora, Inst)

        # Send the alert to the WebSocket server
        try:
            asyncio.get_event_loop().run_until_complete(client.connect())
            asyncio.get_event_loop().run_until_complete(client.send_message(websocket_message))
        except Exception as e:
            print(f"WebSocket error: {e}")

        try:
            existing_alert = mysql_module.get_open_alert_id(Inst, "G/Tc")
            if existing_alert is not None:
                print(f"An open alert with AlertID {existing_alert} already exists")
                handle_existing_alert(existing_alert, fechahora, "to low")
            else:
                handle_new_alert(Inst, message, "G/Tc", "to low", fechahora)


        except Exception as e:
            print(f"MySQL error: {e}")


def generate_alert_id():
    return str(uuid.uuid4())


def check_threshold(values):
    asyncio.get_event_loop().run_until_complete(client.connect())
    # Thresholds for G, Tc, I, V, P
    thresholds = (20, 20, 20, 20, 20)
    alerts = []
    # Extract values from the list
    timestamp = values[0]
    Inst = values[6]
    G = values[1]
    Tc = values[2]
    P = values[5]

    # Calculate performance and loss with provided equation
    coef = mysql_module.get_efficiency_coefficient(Inst)
    P1 = G * float(Decimal(coef)) * (1 - 0.0035 * (Tc - 25)) if G is not None and coef is not None else 0
    performance = P1 / 1000


    # Handle offline alert
    handle_offline_alert(G, Tc, timestamp, Inst)

    try:
        if P is not None:
            alertvalue2 = abs((performance - P) / performance)
            if P is not None and performance != 0 and alertvalue2 > 0.25:
                print(
                    f"--------Handle Value 2 P: {P}, performance: {performance}, Alarm Condition: {alertvalue2}--------")
                handle_alert_value2(P, alertvalue2, timestamp, Inst, False)
            else:
                handle_alert_value2(P, alertvalue2, timestamp, Inst, True)
    except Exception as e:
        print(f"Error calculating alertvalue2: {e}")

    # Check if the values exceed the thresholds
    for i in range(1, 6):
        value = values[i]
        if value is not None:
            parameter = get_parameter_name(i)
            if value > thresholds[i - 1]:
                # Send alert to WebSocket server
                message = f"Parameter {parameter}: {value} exceeds threshold {thresholds[i - 1]}"
                websocket_message = generate_alertjson(parameter, thresholds[i - 1], message, value, timestamp, Inst)
                alerts.append(message)
                # Check for existing alert
                existing_alert = mysql_module.get_open_alert_id(Inst, parameter)

                if existing_alert is not None:
                    # print(f"An open alert with AlertID {existing_alert} already exists")
                    handle_existing_alert(existing_alert, timestamp, value)
                else:
                    handle_new_alert(Inst, message, parameter, value, timestamp)
                # Send the alert to the WebSocket server
                asyncio.get_event_loop().run_until_complete(client.send_message(websocket_message))
            elif value < thresholds[i - 1]:
                message = f"Parameter {parameter}: {value} is below threshold {thresholds[i - 1]}"
                alerts.append(message)
                existing_alert = mysql_module.get_open_alert_id(Inst, parameter)

                if existing_alert is not None:
                    # print(f"An open alert with AlertID {existing_alert} already exists")
                    handle_existing_alert(existing_alert, timestamp, value, closing=True)

    return alerts


def handle_alert_value2(P, new_value, timestamp, Inst, Closing):
    # convert P to W
    P = P * 1000
    message = f"Alert: Significant deviation detected : {new_value}"
    websocket_message = generate_alertjson("DE", 0.25, message, P, timestamp, Inst)
    if not Closing:
        try:
            asyncio.get_event_loop().run_until_complete(client.connect())
            asyncio.get_event_loop().run_until_complete(client.send_message(websocket_message))
        except Exception as e:
            print(f"WebSocket error: {e}")

    try:
        # Check for existing alert
        existing_alert = mysql_module.get_open_alert_id(Inst, "DE")

        if existing_alert is not None:
            # If an existing alert is found, update or close it based on the Closing flag
            if Closing:
                # Mark the alert as closed in the database
                handle_existing_alert(existing_alert, timestamp, new_value, True)
                print(f"Alert ID {existing_alert} closed.")
            else:
                # Update the existing alert with new values
                handle_existing_alert(existing_alert, timestamp, new_value, False)
                print(f"Alert ID {existing_alert} updated with new value.")
        elif not Closing:
            # Only create a new alert if we're not closing the current alert
            handle_new_alert(Inst, message, "DE", P, timestamp)
            print("New alert created.")

    except Exception as e:
        print(f"MySQL error: {e}")

    print(f"--------Handle Value 2 triggert, Value: {new_value}--------")


def generate_alertjson(parameter, threshold, message, value, timestamp, inst):
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
    # Insert the alert into the database
    # Prepare the query and values
    insert_query = """
    INSERT INTO Alerts 
    (AlertID, SensorID, Timestamp, AlertType, AlertMessage, AlertStatus, FirstOccurrenceTimestamp, LastOccurrenceTimestamp, Parameter, CurrentValue) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    # Execute the query
    values = (alert_id, sensor_id, timestamp, alert_type, message, alert_status, first_occurrence_timestamp,
              last_occurrence_timestamp, parameter, cuvalue)
    mysql_module.insert_to_mysql_alert(values, insert_query)

