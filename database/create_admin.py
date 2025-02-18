import mysql.connector
from mysql.connector import Error
import uuid
import os
import sys
from werkzeug.security import generate_password_hash

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import MYSQL_CONFIG

def create_admin_user(email, password, name, phone, license_no):
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        # Create admin user
        user_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO USER (user_id, email, password, name, phone, l_no, user_type)
            VALUES (%s, %s, %s, %s, %s, %s, 'admin')
        """, (
            user_id,
            email,
            generate_password_hash(password),
            name,
            phone,
            license_no
        ))
        
        connection.commit()
        print(f"Admin user created successfully with email: {email}")
        
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("Creating admin user...")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")
    name = input("Enter admin name: ")
    phone = input("Enter admin phone: ")
    license_no = input("Enter admin license number: ")
    
    create_admin_user(email, password, name, phone, license_no) 