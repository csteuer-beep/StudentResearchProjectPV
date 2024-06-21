import mysql.connector
from mysql.connector import Error


def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="192.168.56.1", #"192.168.56.1",  # Hostname des MySQL-Servers
            user="server",  # Benutzername für die Verbindung zur Datenbank
            password="IoTpw2024!",  # Passwort für die Verbindung zur Datenbank
            database="test_jupyter_input"  # Name der Datenbank
        )
        if connection.is_connected():
            print("Connection established")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None


def send_to_mysql_raw(values, insert_query):
    connection = connect_to_database()
    if connection is None:
        print("Failed to establish database connection")
        return

    try:
        cursor = connection.cursor()

        # Check for existing entry with the same FechaHora and Inst
        check_query = "SELECT COUNT(*) FROM pycharm_table WHERE FechaHora = %s AND Inst = %s"
        cursor.execute(check_query, (values[0], values[6]))
        result = cursor.fetchone()

        if result[0] > 0:
            print("Entry with the same FechaHora and Inst already exists")
        else:
            # Insert the new entry
            #insert_query = "INSERT INTO pycharm_table (FechaHora, G, Tc, I, V, P, Inst) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_query, values)
            connection.commit()
            print("SQL erfolgreich")

    except Error as e:
        print(f"Error during database operation(raw): {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed(send_to_mysql_raw)")

def insert_to_mysql_alert(values, insert_query):
    connection = connect_to_database()
    if connection is None:
        print("Failed to establish database connection")
        return

    try:
        cursor = connection.cursor()

        # Insert the new entry
        cursor.execute(insert_query, values)
        connection.commit()
        print("SQL erfolgreich")

    except Error as e:
        print(f"Error during database operation(alert): {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed(insert_to_mysql_alert)")

def get_open_alert_id(inst, parameter):
    connection = connect_to_database()
    if connection is None:
        print("Failed to establish database connection")
        return None

    try:
        cursor = connection.cursor()

        # SQL-Abfrage, um die AlertID für offene Alerts mit übereinstimmendem Inst- und Parameter-Wert abzurufen
        query = "SELECT AlertID FROM alerts WHERE SensorID = %s AND Parameter = %s AND AlertStatus = 'Open'"
        cursor.execute(query, (inst, parameter))
        result = cursor.fetchall() #fetchone()

        if result:
            alert_id = str(result[0])
            alert_id = alert_id.strip("(),'\"")
            print("alertid: ", alert_id)
            return alert_id
        else:
            print("Kein offener Alert mit übereinstimmendem Inst- und Parameter-Wert gefunden")
            return None

    except mysql.connector.Error as e:
        print(f"Fehler bei der Datenbankabfrage: {e}")
        return None

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed(get_open_alert_id)")


    #update_field("column_name", "table_name", "new_value")
    #update_field("column_name", "table_name", "new_value", "condition_column = 'condition_value'")
def update_field(table, field, new_value, condition_field=None, condition_value=None):
    connection = connect_to_database()
    if connection is None:
        print("Failed to establish database connection")
        return

    try:
        cursor = connection.cursor()

        if condition_field and condition_value:
            query = f"UPDATE {table} SET {field} = %s WHERE {condition_field} = %s"
            cursor.execute(query, (new_value, condition_value))
        else:
            query = f"UPDATE {table} SET {field} = %s"
            cursor.execute(query, (new_value,))

        connection.commit()
        print(f"Field {field} in table {table} updated successfully")

    except mysql.connector.Error as e:
        print(f"Error during database operation(update_field): {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed(update_field)")
