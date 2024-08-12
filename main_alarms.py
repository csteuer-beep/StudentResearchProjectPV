# alarm_processing.py
import mqtt_handler
import alerting_module
import os

def process_alarms(values_list):
    for values in values_list:
        alerts = alerting_module.check_threshold(values)
        print("Alerts:", alerts)

# if __name__ == "__main__":
#     broker_address = "192.168.56.1"
#     broker_port = 1883
#     topic = "pv/data"
#     mqtt_handler.start_mqtt_client(broker_address, broker_port, topic, process_alarms)


if __name__ == "__main__":
    connection_file = '/tmp/mqtt_connection'
    if not mqtt_handler.connection_exists(connection_file):
        broker_address = "192.168.56.1"
        broker_port = 1883
        topic = "pv/data"
        mqtt_handler.start_mqtt_client(broker_address, broker_port, topic, process_alarms)
        mqtt_handler.create_connection_file(connection_file)
    else:
        print("MQTT connection already exists.")