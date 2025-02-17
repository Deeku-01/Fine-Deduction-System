import mysql.connector
from mysql.connector import Error
from config.config import MYSQL_CONFIG
from contextlib import contextmanager

class MySQLConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MySQLConnection, cls).__new__(cls)
            cls._instance.connection = None
        return cls._instance

    def connect(self):
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**MYSQL_CONFIG)
            return self.connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

@contextmanager
def get_db_cursor():
    """Context manager for database cursor"""
    conn = MySQLConnection()
    connection = conn.connect()
    cursor = connection.cursor(dictionary=True)
    try:
        yield cursor
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()

# Usage example:
# with get_db_cursor() as cursor:
#     cursor.execute("SELECT * FROM users")
#     results = cursor.fetchall() 