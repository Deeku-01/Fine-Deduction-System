# Traffic Fine Deduction System

A comprehensive system for detecting traffic violations using computer vision (YOLOv8) and managing fines through a hybrid database approach (MySQL + Supabase).

## Features

- License plate detection using YOLOv8
- Real-time violation recording
- Hybrid database system:
  - MySQL for transactional data (users, vehicles, challans, payments)
  - Supabase for real-time features and file storage
- RESTful API using FastAPI
- Secure authentication and authorization
- Image processing and storage
- Payment processing integration

## System Architecture

The system uses a hybrid database approach:

### MySQL Tables
- USER: Store user information
- POLICE: Police officer details
- VEHICLE: Vehicle registration information
- CHALLAN: Traffic violation records
- PAYMENT: Fine payment transactions
- POLICE_STATION: Police station details
- STATION_ASSIGNMENT: Officer station assignments
- VIOLATION_TYPE: Types of traffic violations

### Supabase
- VEHICLE_OWNER_HISTORY: Temporal data for vehicle ownership
- Storage Buckets:
  - vehicle_images: Vehicle registration images
  - challan_images: Traffic violation evidence

## Prerequisites

- Python 3.8+
- MySQL 8.0+
- Supabase account
- CUDA-capable GPU (recommended for YOLOv8)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd traffic-fine-system
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (.env):
```env
# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=traffic_fine_system

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Application Configuration
API_SECRET_KEY=your_secret_key
YOLO_MODEL_PATH=models/license_plate_detection.pt
```

5. Initialize the database:
```bash
mysql -u root -p < database/mysql_schema.sql
```

6. Run Supabase migrations:
```bash
psql -h your_supabase_host -d your_database < database/supabase_schema.sql
```

## Usage

1. Start the FastAPI server:
```bash
python src/main.py
```

2. Access the API documentation:
```
http://localhost:8000/docs
```

## API Endpoints

### POST /detect-violation
Upload an image to detect license plate and record violation

### GET /challans/{vehicle_id}
Get all challans for a specific vehicle

### POST /payments/{challan_id}
Process payment for a challan

## Development

1. Run tests:
```bash
pytest tests/
```

2. Format code:
```bash
black src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- YOLOv8 for object detection
- FastAPI for the web framework
- Supabase for real-time features and storage
- MySQL for reliable transactional data storage 