import mysql.connector
from mysql.connector import Error
import os
import sys

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import MYSQL_CONFIG

def setup_database():
    # First connection without database (to create it)
    config = MYSQL_CONFIG.copy()
    config.pop('database', None)
    
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS traffic_fine_system")
        print("Database created successfully!")
        
        # Switch to the database
        cursor.execute("USE traffic_fine_system")
        
        # Create USER table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS USER (
            user_id VARCHAR(36) PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            l_no VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(20),
            user_type ENUM('driver', 'admin', 'police') NOT NULL DEFAULT 'driver',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("USER table created successfully!")
        
        # Create POLICE table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS POLICE (
            police_id VARCHAR(36) PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            badge_number VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            police_rank VARCHAR(50) NOT NULL,
            station_id VARCHAR(36),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("POLICE table created successfully!")
        
        # Create POLICE_STATION table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS POLICE_STATION (
            station_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            location VARCHAR(255) NOT NULL,
            contact_no VARCHAR(20)
        )
        """)
        print("POLICE_STATION table created successfully!")
        
        # Create VEHICLE table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS VEHICLE (
            vehicle_id VARCHAR(36) PRIMARY KEY,
            reg_number VARCHAR(20) UNIQUE NOT NULL,
            owner_id VARCHAR(36),
            vehicle_type VARCHAR(50) NOT NULL,
            model VARCHAR(100),
            manufacturer VARCHAR(100),
            image_url VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (owner_id) REFERENCES USER(user_id)
        )
        """)
        print("VEHICLE table created successfully!")
        
        # Create VIOLATION_TYPE table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS VIOLATION_TYPE (
            type_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            base_fine_amt DECIMAL(10,2) NOT NULL,
            description TEXT
        )
        """)
        print("VIOLATION_TYPE table created successfully!")
        
        # Create CHALLAN table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS CHALLAN (
            challan_id VARCHAR(36) PRIMARY KEY,
            challan_no VARCHAR(50) UNIQUE NOT NULL,
            vehicle_id VARCHAR(36),
            issued_by VARCHAR(36),
            violation_type VARCHAR(36),
            fine_amt DECIMAL(10,2) NOT NULL,
            location VARCHAR(255),
            description TEXT,
            image_url VARCHAR(255),
            status ENUM('pending', 'paid', 'disputed', 'cancelled') DEFAULT 'pending',
            issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            payment_date TIMESTAMP NULL,
            FOREIGN KEY (vehicle_id) REFERENCES VEHICLE(vehicle_id),
            FOREIGN KEY (issued_by) REFERENCES POLICE(police_id),
            FOREIGN KEY (violation_type) REFERENCES VIOLATION_TYPE(type_id)
        )
        """)
        print("CHALLAN table created successfully!")
        
        # Create PAYMENT table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS PAYMENT (
            payment_id VARCHAR(36) PRIMARY KEY,
            challan_id VARCHAR(36),
            amt DECIMAL(10,2) NOT NULL,
            payment_method VARCHAR(50),
            transaction_id VARCHAR(100),
            status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (challan_id) REFERENCES CHALLAN(challan_id)
        )
        """)
        print("PAYMENT table created successfully!")

        # Insert some sample violation types
        cursor.execute("TRUNCATE TABLE VIOLATION_TYPE")  # Clear existing entries
        
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
        
        for name, fine, desc in violation_types:
            cursor.execute("""
                INSERT INTO VIOLATION_TYPE (type_id, name, base_fine_amt, description)
                VALUES (UUID(), %s, %s, %s)
            """, (name, fine, desc))
            
        print("Sample violation types inserted successfully!")

        connection.commit()
        print("\nDatabase setup completed successfully!")
        
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    setup_database() 