# alert_module.py
import asyncio
import datetime
import uuid
import json
import websocket_handler
import mysql_module

uri = "ws://localhost:8765/alerts"
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

def handle_offline_alert(G, Tc, fechahora, Inst):
    if G is not None and G < 10:
        message = f"G, Tc sensor is offline. G: {G} , Tc: {Tc}"
        websocket_message = generate_alertjson("G/Tc", 1, message, G, fechahora, Inst)

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
    thresholds = (20, 20, 20, 20, 20)
    alerts = []
    timestamp = values[0]
    Inst = values[6]

    G = values[1]
    Tc = values[2]
    P = values[5]

    # Calculate new_value, performance, and loss
    vv = 5.5 if Inst == "etsist1" else 4.8 if Inst == "etsist2" else 0
    P1 = G * vv * (1 - 0.0035 * (Tc - 25)) if G is not None else 0
    performance = P1 / 1000
    loss = max(0, P - performance) if P is not None else performance

    # Handle offline alert
    handle_offline_alert(G, Tc, timestamp, Inst)

    # Handle the second value alert (alert_value2)
    alertvalue2 = abs((performance - P) / performance)
    if P is not None and performance != 0 and alertvalue2 > 0.25:
        print(f"--------Handle Value 2 P: {P}, performance: {performance}, Alarm Condition: {alertvalue2}--------")
        handle_alert_value2(P, alertvalue2, timestamp, Inst)

    for i in range(1, 6):
        value = values[i]
        if value is not None:
            parameter = get_parameter_name(i)
            if value > thresholds[i - 1]:
                message = f"Parameter {parameter}: {value} exceeds threshold {thresholds[i - 1]}"
                websocket_message = generate_alertjson(parameter, thresholds[i - 1], message, value, timestamp, Inst)
                alerts.append(message)
                existing_alert = mysql_module.get_open_alert_id(Inst, parameter)

                if existing_alert is not None:
                   # print(f"An open alert with AlertID {existing_alert} already exists")
                    handle_existing_alert(existing_alert, timestamp, value)
                else:
                    handle_new_alert(Inst, message, parameter, value, timestamp)

                asyncio.get_event_loop().run_until_complete(client.send_message(websocket_message))
            elif value < thresholds[i - 1]:
                message = f"Parameter {parameter}: {value} is below threshold {thresholds[i - 1]}"
                alerts.append(message)
                existing_alert = mysql_module.get_open_alert_id(Inst, parameter)

                if existing_alert is not None:
                    #print(f"An open alert with AlertID {existing_alert} already exists")
                    handle_existing_alert(existing_alert, timestamp, value, closing=True)

    return alerts

def handle_alert_value2(P, new_value, timestamp, Inst, Closing):
    P=P*1000
    message = f"Alert: Significant deviation detected. P: {P}, Expected: {new_value}"
    websocket_message = generate_alertjson("P", 0.25, message, P, timestamp, Inst)
    if not Closing:
        try:
            asyncio.get_event_loop().run_until_complete(client.connect())
            asyncio.get_event_loop().run_until_complete(client.send_message(websocket_message))
        except Exception as e:
           print(f"WebSocket error: {e}")

    try:
        existing_alert = mysql_module.get_open_alert_id(Inst, "DE")
        if existing_alert is not None:
            # print(f"An open alert with AlertID {existing_alert} already exists")
            handle_existing_alert(existing_alert, timestamp, new_value, Closing)
        else:
            handle_new_alert(Inst, message, "DE", P, timestamp)

    except Exception as e:
        print(f"MySQL error: {e}")

    print(f"--------Handle Vlaue 2 P: {P}, Expected: {new_value}--------")



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

    insert_query = """
    INSERT INTO Alerts 
    (AlertID, SensorID, Timestamp, AlertType, AlertMessage, AlertStatus, FirstOccurrenceTimestamp, LastOccurrenceTimestamp, Parameter, CurrentValue) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (alert_id, sensor_id, timestamp, alert_type, message, alert_status, first_occurrence_timestamp, last_occurrence_timestamp, parameter, cuvalue)
    mysql_module.insert_to_mysql_alert(values, insert_query)



# alert_module.py
# import asyncio
# import datetime
# import uuid
# import json
# import websocket_handler
# import mysql_module
#
#
# uri = "ws://localhost:8765/alerts" #"ws://192.168.56.1:8765/alerts"
# client = websocket_handler.WebSocketClient(uri)
#
#
#
# def get_parameter_name(index):
#     parameters = ["", "G", "Tc", "I", "V", "P"]
#     return parameters[index]
#
# def handle_existing_alert(alert_id, timestamp, value, closing=False):
#     if closing:
#         mysql_module.update_field("Alerts", "AlertStatus", "Closed", "AlertID", alert_id)
#         mysql_module.update_field("Alerts", "Currentvalue", value, "AlertID", alert_id)
#     else:
#         mysql_module.update_field("Alerts", "LastOccurrenceTimestamp", timestamp, "AlertID", alert_id)
#         mysql_module.update_field("Alerts", "Currentvalue", value, "AlertID", alert_id)
#
# def handle_new_alert(sensor_id, message, parameter, cuvalue, timestamp):
#     print("No open alert with matching instance and parameter value found")
#     send_alert_to_database(sensor_id, message, parameter, cuvalue, timestamp)
#
# def check_threshold(values):
#     asyncio.get_event_loop().run_until_complete(client.connect())
#     thresholds = (20, 20, 20, 20, 20)
#     alerts = []
#     timestamp = values[0]
#
#     for i in range(1, 6):  # Start from index 1 to skip the first element (assuming it's the timestamp)
#         value = values[i]
#         if value is not None:
#             parameter = get_parameter_name(i)
#             if value > thresholds[i - 1]:  # Check if value exceeds threshold
#                 message = f"Parameter {parameter}: {value} exceeds threshold {thresholds[i - 1]}"
#                 websocket_message = generate_alertjson(parameter, thresholds[i - 1], message, value, timestamp, values[6])
#                 alerts.append(message)
#                 print(alerts)
#                 existing_alert = mysql_module.get_open_alert_id(values[6], parameter)
#
#                 if existing_alert is not None:
#                     print(f"An open alert with AlertID {existing_alert} already exists")
#                     handle_existing_alert(existing_alert, timestamp, value)
#                 else:
#                     handle_new_alert(values[6], message, parameter, value, timestamp)
#
#                 asyncio.get_event_loop().run_until_complete(client.send_message(websocket_message))
#             elif value < thresholds[i - 1]:  # Check if value falls below threshold
#                 message = f"Parameter {parameter}: {value} is below threshold {thresholds[i - 1]}"
#                 alerts.append(message)
#                 print(alerts)
#                 existing_alert = mysql_module.get_open_alert_id(values[6], parameter)
#
#                 if existing_alert is not None:
#                     print(f"An open alert with AlertID {existing_alert} already exists")
#                     handle_existing_alert(existing_alert, timestamp, value, closing=True)
#
#
#     return alerts
#
# def generate_alertjson(parameter, threshold, message, value, timestamp, inst ):
#     data = {
#         "Timestamp": timestamp,
#         "Parameter": parameter,
#         "Threshold": threshold,
#         "AlertMessage": message,
#         "CurrentValue": value,
#         "Inst": inst
#     }
#
#     return json.dumps(data)
#
# def send_alert_to_database(sensor_id, message, parameter, cuvalue, timestamp):
#     print("Timestamp before MySQL operation:", timestamp)
#     alert_id = generate_alert_id()
#     alert_type = "Threshold Exceeded"
#     alert_status = "Open"
#     first_occurrence_timestamp = timestamp
#     last_occurrence_timestamp = timestamp
#
#     print("Alert UUID:", alert_id)
#
#     insert_query = """
#     INSERT INTO Alerts
#     (AlertID, SensorID, Timestamp, AlertType, AlertMessage, AlertStatus, FirstOccurrenceTimestamp, LastOccurrenceTimestamp, Parameter, CurrentValue)
#     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#     """
#     values = (alert_id, sensor_id, timestamp, alert_type, message, alert_status, first_occurrence_timestamp, last_occurrence_timestamp, parameter, cuvalue)
#     mysql_module.insert_to_mysql_alert(values, insert_query)
#
# def handle_offline_alert(G, Tc, fechahora, Inst):
#     # Check if the sensor is offline
#     if G is not None and G < 10:
#         # Create the alert message
#         message = f"G, Tc sensor is offline. G: {G} , Tc: {Tc}"
#         websocket_message = generate_alertjson("G/Tc", 1, message, G, fechahora, Inst)
#
#         try:
#             # Send alert via WebSocket
#             asyncio.get_event_loop().run_until_complete(client.connect())
#             asyncio.get_event_loop().run_until_complete(client.send_message(websocket_message))
#         except Exception as e:
#             print(f"WebSocket error: {e}")
#
#         try:
#             # Send alert to MySQL database
#             send_alert_to_database(Inst, message, "G/Tc", 0, fechahora)
#         except Exception as e:
#             print(f"MySQL error: {e}")
#
# def generate_alert_id():
#     return str(uuid.uuid4())
