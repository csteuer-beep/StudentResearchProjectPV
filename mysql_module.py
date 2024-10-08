# mysql_module.py
import mysql.connector
from mysql.connector import Error

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost", #192.168.56.1",
            user="server",
            password="IoTpw2024!",
            database="solarplant_db"
        )
        if connection.is_connected():
            print("Connection established")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# saving the non-processed data to the database
def send_to_mysql_raw(values, insert_query):

    connection = connect_to_database()
    if connection is None:
        print("Failed to establish database connection")
        return

    try:
        # Insert the new entry
        cursor = connection.cursor()
        check_query = "SELECT COUNT(*) FROM Solarplant_Raw WHERE FechaHora = %s AND Inst = %s"
        cursor.execute(check_query, (values[0], values[6]))
        result = cursor.fetchone()
        # if result != 0 then the entry already exists
        if result[0] > 0:
            print("Entry with the same FechaHora and Inst already exists")
        else:
            print("Tuple", values)
            cursor.execute(insert_query, values)
            connection.commit()
            print("SQL erfolgreich")
            print("Data saved to DB:", values)

    except Error as e:
        print(f"Error during database operation(raw): {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed(send_to_mysql_raw)")

# saving the processed data to the database
def insert_to_mysql_alert(values, insert_query):
    connection = connect_to_database()
    if connection is None:
        print("Failed to establish database connection")
        return

    try:
        cursor = connection.cursor()
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
        query = "SELECT AlertID FROM Alerts WHERE SensorID = %s AND Parameter = %s AND AlertStatus = 'Open'"
        cursor.execute(query, (inst, parameter))
        result = cursor.fetchall()

        if result:
            alert_id = str(result[0])
            alert_id = alert_id.strip("(),'\"")
            #print("alertid: ", alert_id)
            return alert_id
        else:
            #print("No open alert with matching inst and parameter value found")
            return None

    except mysql.connector.Error as e:
        print(f"Error during database query: {e}")
        return None

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed(get_open_alert_id)")

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

# collect raw data from the database for specific month and year, needed for aggregation
def fetch_raw_data(month, year):
    connection = connect_to_database()
    if connection is None:
        print("Failed to establish database connection")
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT * FROM Solarplant_Raw 
            WHERE MONTH(FechaHora) = %s AND YEAR(FechaHora) = %s
        """
        cursor.execute(query, (month, year))
        result = cursor.fetchall()
        return result

    except Error as e:
        print(f"Error during database operation(fetch_raw_data): {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed(fetch_raw_data)")

# insert aggregated data into the database
def insert_aggregated_data(values):
    connection = connect_to_database()
    if connection is None:
        print("Failed to establish database connection")
        return

    try:
        cursor = connection.cursor()
        insert_query = """
            INSERT INTO Solarplant_Ag_Data 
            (EntryID, Inst, Year, Month, SumOfP, MeanOfP, MinOfP, MaxOfP, MaxOfTc, MinOfTc, MeanOfTc, 
            MaxOfI, MinOfI, MeanOfI, MaxOfV, MinOfV, MeanOfV, MaxOfG, MinOfG, MeanOfG) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, values)
        connection.commit()
        print("Aggregated data inserted successfully")

    except Error as e:
        print(f"Error during database operation(insert_aggregated_data): {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed(insert_aggregated_data)")

def get_efficiency_coefficient(facility_name):
    connection = connect_to_database()
    if connection is None:
        print("Failed to establish database connection")
        return None

    try:
        cursor = connection.cursor()
        query = "SELECT eff_coeff FROM Facilities WHERE inst = %s"
        cursor.execute(query, (facility_name,))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            print(f"No efficiency coefficient found for facility '{facility_name}'")
            return None

    except Error as e:
        print(f"Error during database operation(get_efficiency_coefficient): {e}")
        return None

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed(get_efficiency_coefficient)")
