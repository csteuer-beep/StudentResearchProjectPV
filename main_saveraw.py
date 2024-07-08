# main_saveraw.py
import mqtt_handler
import mysql_module

def save_to_db(values_list):
    for values in values_list:
        mysql_module.send_to_mysql_raw(values, "INSERT INTO raw_testing (FechaHora, G, Tc, I, V, P, Inst, Performance) VALUES (%s, %s, %s, %s, %s, %s, %s %s)")
        print("Data saved to DB:", values)

if __name__ == "__main__":
    broker_address = "192.168.56.1"
    broker_port = 1883
    topic = "pv/data"
    mqtt_handler.start_mqtt_client(broker_address, broker_port, topic, save_to_db)

