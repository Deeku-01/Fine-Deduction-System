from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import uuid
import os
from datetime import datetime
import json

from detection.license_plate_detector import LicensePlateDetector
from database.mysql_connection import get_db_cursor
from database.supabase_connection import SupabaseConnection

app = FastAPI(title="Traffic Fine System API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize services
license_plate_detector = LicensePlateDetector()
supabase = SupabaseConnection()

@app.post("/detect-violation")
async def detect_violation(
    image: UploadFile = File(...),
    location: str = None,
    violation_type: str = None,
    token: str = Depends(oauth2_scheme)
):
    """
    Detect license plate and record violation
    """
    try:
        # Save uploaded image temporarily
        temp_path = f"temp_{uuid.uuid4()}.jpg"
        with open(temp_path, "wb") as buffer:
            buffer.write(await image.read())

        # Detect license plate
        plate_img, confidence, bbox = license_plate_detector.detect_license_plate(temp_path)
        
        if plate_img is None:
            raise HTTPException(status_code=400, detail="No license plate detected")

        # Process the plate image
        processed_plate = license_plate_detector.preprocess_plate_image(plate_img)
        
        # Save processed image to Supabase storage
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_name = f"violations/{timestamp}_{uuid.uuid4()}.jpg"
        
        # Upload original and processed images
        supabase.upload_image("challan_images", temp_path, image_name)
        image_url = supabase.get_image_url("challan_images", image_name)

        # Create challan record
        with get_db_cursor() as cursor:
            # Get vehicle details from reg_number (would need OCR integration)
            cursor.execute(
                "SELECT vehicle_id, owner_id FROM vehicle WHERE reg_number = %s",
                ("DUMMY_REG",)  # Replace with actual OCR result
            )
            vehicle = cursor.fetchone()
            
            if not vehicle:
                raise HTTPException(status_code=404, detail="Vehicle not found")

            # Create challan
            challan_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO challan (
                    challan_id, challan_no, vehicle_id, issued_by, violation_type,
                    fine_amt, location, image_url, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                challan_id,
                f"CHAL_{timestamp}",
                vehicle['vehicle_id'],
                "POLICE_ID",  # Get from token
                violation_type,
                1000.00,  # Get from violation_type table
                location,
                image_url,
                'pending'
            ))

        # Cleanup
        os.remove(temp_path)

        return {
            "message": "Violation recorded successfully",
            "challan_id": challan_id,
            "confidence": confidence
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/challans/{vehicle_id}")
async def get_vehicle_challans(
    vehicle_id: str,
    token: str = Depends(oauth2_scheme)
):
    """
    Get all challans for a vehicle
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT c.*, v.reg_number, vt.name as violation_name
                FROM challan c
                JOIN vehicle v ON c.vehicle_id = v.vehicle_id
                JOIN violation_type vt ON c.violation_type = vt.type_id
                WHERE c.vehicle_id = %s
                ORDER BY c.issue_date DESC
            """, (vehicle_id,))
            
            challans = cursor.fetchall()
            
            # Get vehicle history from Supabase
            history = supabase.get_vehicle_history(vehicle_id)
            
            return {
                "challans": challans,
                "history": history.data
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/payments/{challan_id}")
async def process_payment(
    challan_id: str,
    payment_method: str,
    amount: float,
    token: str = Depends(oauth2_scheme)
):
    """
    Process payment for a challan
    """
    try:
        with get_db_cursor() as cursor:
            # Verify challan exists and amount matches
            cursor.execute(
                "SELECT fine_amt, status FROM challan WHERE challan_id = %s",
                (challan_id,)
            )
            challan = cursor.fetchone()
            
            if not challan:
                raise HTTPException(status_code=404, detail="Challan not found")
            
            if challan['status'] != 'pending':
                raise HTTPException(status_code=400, detail="Challan is not pending")
            
            if challan['fine_amt'] != amount:
                raise HTTPException(status_code=400, detail="Invalid payment amount")

            # Create payment record
            payment_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO payment (
                    payment_id, challan_id, amt, payment_method,
                    transaction_id, status
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                payment_id,
                challan_id,
                amount,
                payment_method,
                f"TXN_{uuid.uuid4()}",
                'completed'
            ))

            # Update challan status
            cursor.execute(
                "UPDATE challan SET status = 'paid', payment_date = NOW() WHERE challan_id = %s",
                (challan_id,)
            )

            return {
                "message": "Payment processed successfully",
                "payment_id": payment_id
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 