import mysql.connector
from mysql.connector import Error



def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="192.168.56.1",  # Hostname des MySQL-Servers
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


def send_to_mysql(values, insert_query):
    connection = connect_to_database()
    if connection is None:
        print("Failed to establish database connection")
        return

    try:
        cursor = connection.cursor()
        #insert_query = "INSERT INTO pycharm_table (FechaHora, G, Tc, I, V, P, Inst) VALUES (%s, %s, %s, %s, %s, %s, %s)" #Raw data insert query
        cursor.execute(insert_query, values)
        connection.commit()
        print("SQL erfolgreich")
    except Error as e:
        print(f"Error during database operation: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed")

