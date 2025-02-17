import mysql.connector
import os
import sys

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import MYSQL_CONFIG

def test_connection():
    try:
        # Try to connect to MySQL
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        
        if connection.is_connected():
            print("Successfully connected to MySQL!")
            
            # Get server information
            db_info = connection.get_server_info()
            print(f"MySQL Server version: {db_info}")
            
            # Get cursor and test query
            cursor = connection.cursor()
            
            # Test database
            cursor.execute("SELECT DATABASE();")
            database = cursor.fetchone()
            print(f"Connected to database: {database[0]}")
            
            # Test tables
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print("\nAvailable tables:")
            for table in tables:
                print(f"- {table[0]}")
                
            # Test violation types
            cursor.execute("SELECT * FROM VIOLATION_TYPE;")
            violations = cursor.fetchall()
            print("\nViolation types:")
            for violation in violations:
                print(f"- {violation[1]}: ₹{violation[2]}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nMySQL connection closed.")

def check_violation_types():
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # Check violation types
        cursor.execute("SELECT * FROM violation_type ORDER BY name")
        violations = cursor.fetchall()
        
        print("\nCurrent violation types:")
        for violation in violations:
            print(f"- {violation['name']}: ₹{violation['base_fine_amt']}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    test_connection()
    check_violation_types() 