from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

# MySQL Configuration
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1213',  # Your MySQL password
    'database': 'traffic_fine_system'
}

# Supabase Configuration
SUPABASE_URL = 'https://otofhhkrnslrgwpgoanu.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im90b2ZoaGtybnNscmd3cGdvYW51Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczOTgyMjQ5NSwiZXhwIjoyMDU1Mzk4NDk1fQ.SBNebBht6tmgcAhuJZgxNfe4MoVMo_csEBYnTPojfcs'

# YOLO Configuration
YOLO_MODEL_PATH = 'models/license_plate_detection.pt'
CONFIDENCE_THRESHOLD = 0.5

# API Configuration
API_SECRET_KEY = 'lZRMNbwoumH7CJtyrX0epzSua13SAmMrs/VwjaPkhne8UmyADpCmgKCMv289vQDU1qvQI4IXk5uEbQb/nwH1PA=='
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# File Storage Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'} 