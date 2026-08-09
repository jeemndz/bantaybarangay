import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()


def get_connection():
    
    try:
        connection = mysql.connector.connect(
           host="bantaybarangay.mysql.database.azure.com",
        port=3306,
        user="bantayadmin",
        password="Bantayadmin1",
        database="bantay",
        ssl_disabled=False
        )

        if connection.is_connected():
            return connection

    except Error as e:
        print(f"MySQL connection error: {e}")

    return None


def test_connection():
    """Test the Azure MySQL connection."""
    connection = get_connection()

    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()

            print("Successfully connected to Azure MySQL!")
            print(f"MySQL version: {version[0]}")

            cursor.close()
        except Error as e:
            print(f"Query error: {e}")
        finally:
            if connection.is_connected():
                connection.close()
                print("Connection closed.")
    else:
        print("Failed to connect to Azure MySQL.")


if __name__ == "__main__":
    test_connection()