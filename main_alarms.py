# alarm_processing.py
import mqtt_handler
import alerting_module

def process_alarms(values_list):
    for values in values_list:
        alerts = alerting_module.check_threshold(values)
        print("Alerts:", alerts)

if __name__ == "__main__":
    broker_address = "192.168.56.1"
    broker_port = 1883
    topic = "pv/data"
    mqtt_handler.start_mqtt_client(broker_address, broker_port, topic, process_alarms)
