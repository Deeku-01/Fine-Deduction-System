from src.database.mysql_connection import get_db_cursor

def check_vehicle_records():
    with get_db_cursor() as cursor:
        # Check vehicle and associated user
        cursor.execute("""
            SELECT v.*, u.name, u.email, u.l_no 
            FROM vehicle v 
            LEFT JOIN USER u ON v.owner_id = u.user_id 
            WHERE v.reg_number = %s
        """, ('KL01CA2555',))
        vehicle_data = cursor.fetchall()
        
        print("\nVehicle and User Records:")
        print("-" * 50)
        for record in vehicle_data:
            print(record)
            
        # Check challans
        cursor.execute("""
            SELECT c.*, v.reg_number, vt.name as violation_name
            FROM challan c 
            JOIN vehicle v ON c.vehicle_id = v.vehicle_id 
            JOIN violation_type vt ON c.violation_type = vt.type_id
            WHERE v.reg_number = %s
        """, ('KL01CA2555',))
        challan_data = cursor.fetchall()
        
        print("\nChallan Records:")
        print("-" * 50)
        for record in challan_data:
            print(record)

if __name__ == "__main__":
    check_vehicle_records() 