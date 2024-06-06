# alert_module.py
import mysql_module
import datetime

def check_threshold(values):
    thresholds = (12, 18, 22, 20, 30)
    alerts = []


    for i in range(1, 6):  # Start from index 1 to skip the first element (assuming it's the timestamp)
        value = values[i]
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

            message = f"Parameter {parameter}: {value} exceeds threshold {thresholds[i - 1]}"
            alerts.append(message)

            send_alert_to_database(values[6], message, parameter)

    return alerts

def send_alert_to_database(sensor_id, message, parameter):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print("Timestamp before MySQL operation:", timestamp)
    alert_id = generate_alert_id()
    alert_type = "Threshold Exceeded"
    alert_status = "Open"
    first_occurrence_timestamp = timestamp
    last_occurrence_timestamp = timestamp

    print("Alert UUID:", alert_id)

    insert_query = "INSERT INTO alerts (AlertID, SensorID, Timestamp, AlertType, AlertMessage, AlertStatus, FirstOccurrenceTimestamp, LastOccurrenceTimestamp, Parameter) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (alert_id, sensor_id, timestamp, alert_type, message, alert_status, first_occurrence_timestamp, last_occurrence_timestamp, parameter)
    mysql_module.insert_to_mysql_alert(values, insert_query)

def generate_alert_id():
    # You can use a unique identifier for the AlertID.
    # Using current timestamp as AlertID might result in collision if multiple alerts occur simultaneously.
    # Using an auto-increment column in the database table is a safer approach, but you can also generate
    # a UUID or a combination of timestamp and some random number for AlertID.
    # Here, I'll generate a UUID as an example:
    import uuid
    return str(uuid.uuid4())
