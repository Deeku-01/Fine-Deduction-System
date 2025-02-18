import mysql.connector
from mysql.connector import Error
import os
import sys
import uuid

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import MYSQL_CONFIG

def reset_violation_types():
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        # First, remove any existing violation types
        print("Clearing existing violation types...")
        cursor.execute("DELETE FROM violation_type")
        
        # Define unique violation types
        violation_types = [
            ('Speeding', 1000.00, 'Exceeding speed limit'),
            ('Red Light', 500.00, 'Running red light'),
            ('No Parking', 300.00, 'Parking in no-parking zone'),
            ('Wrong Side', 500.00, 'Driving on wrong side'),
            ('No Helmet', 200.00, 'Riding without helmet'),
            ('No Seatbelt', 200.00, 'Driving without seatbelt'),
            ('Invalid License', 1000.00, 'Driving without valid license'),
            ('Overloading', 500.00, 'Vehicle overloading'),
            ('Dangerous Driving', 1000.00, 'Reckless or dangerous driving'),
            ('Noise Pollution', 300.00, 'Excessive honking or modified silencer')
        ]
        
        print("\nAdding new violation types:")
        for name, fine, desc in violation_types:
            type_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO violation_type (type_id, name, base_fine_amt, description)
                VALUES (%s, %s, %s, %s)
            """, (type_id, name, fine, desc))
            print(f"- Added: {name} (₹{fine})")
        
        connection.commit()
        print("\nViolation types reset successfully!")
        
        # Verify the results
        cursor.execute("SELECT name, base_fine_amt FROM violation_type ORDER BY name")
        print("\nCurrent violation types in database:")
        for name, fine in cursor.fetchall():
            print(f"- {name}: ₹{fine}")
        
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\nMySQL connection closed.")

if __name__ == "__main__":
    reset_violation_types() 