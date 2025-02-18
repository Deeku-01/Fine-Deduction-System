import mysql.connector
from mysql.connector import Error
import uuid
import os
import sys
from werkzeug.security import generate_password_hash

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import MYSQL_CONFIG

def create_police_station():
    """Create a sample police station"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        # Create sample police station
        station_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO POLICE_STATION (station_id, name, location, contact_no)
            VALUES (%s, %s, %s, %s)
        """, (
            station_id,
            'Central Police Station',
            'City Center, Main Road',
            '1234567890'
        ))
        
        connection.commit()
        print("Sample police station created successfully!")
        return station_id
        
    except Error as e:
        print(f"Error creating police station: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_predefined_police():
    """Create predefined police officers"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        # First create a police station
        station_id = create_police_station()
        if not station_id:
            print("Failed to create police station")
            return
        
        # Predefined police officers
        police_officers = [
            {
                'email': 'officer1@police.com',
                'password': 'Police@123',
                'badge_number': 'PD001',
                'name': 'John Smith',
                'rank': 'Inspector',
            },
            {
                'email': 'officer2@police.com',
                'password': 'Police@123',
                'badge_number': 'PD002',
                'name': 'Sarah Johnson',
                'rank': 'Sergeant',
            },
            {
                'email': 'officer3@police.com',
                'password': 'Police@123',
                'badge_number': 'PD003',
                'name': 'Michael Brown',
                'rank': 'Constable',
            }
        ]
        
        # Create police officers
        for officer in police_officers:
            police_id = str(uuid.uuid4())
            
            # Create user account first (for login)
            cursor.execute("""
                INSERT INTO USER (user_id, email, password, name, l_no, user_type)
                VALUES (%s, %s, %s, %s, %s, 'police')
            """, (
                police_id,
                officer['email'],
                generate_password_hash(officer['password']),
                officer['name'],
                officer['badge_number'],  # Using badge number as license number
            ))
            
            # Create police record
            cursor.execute("""
                INSERT INTO POLICE (
                    police_id, email, password, badge_number,
                    name, police_rank, station_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                police_id,
                officer['email'],
                generate_password_hash(officer['password']),
                officer['badge_number'],
                officer['name'],
                officer['rank'],
                station_id
            ))
            
            print(f"Created police officer: {officer['name']} ({officer['badge_number']})")
        
        connection.commit()
        print("\nAll police officers created successfully!")
        print("\nLogin credentials:")
        for officer in police_officers:
            print(f"\nOfficer: {officer['name']}")
            print(f"Email: {officer['email']}")
            print(f"Password: {officer['password']}")
            print(f"Badge Number: {officer['badge_number']}")
        
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_predefined_police() 