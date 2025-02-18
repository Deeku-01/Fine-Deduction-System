# Traffic Fine Deduction System

A comprehensive system for managing traffic violations and fines, featuring automatic license plate detection, real-time challan generation, and a hybrid database approach.

## Features

### Core Functionality
- Automatic license plate detection using YOLOv8 and EasyOCR
- Real-time violation recording with image evidence
- Secure challan generation and management
- Integrated payment processing system
- User-specific dashboards for drivers and police officers

### Technical Features
- Hybrid database system (MySQL + Supabase)
- Computer vision-based license plate detection
- Secure authentication and authorization
- Real-time statistics and reporting
- Image processing and storage
- RESTful API endpoints

## System Architecture

### Database Structure
- **MySQL Database**: Primary database for transactional data
  - USER: User information and authentication
  - POLICE: Police officer details and credentials
  - VEHICLE: Vehicle registration information
  - CHALLAN: Traffic violation records
  - PAYMENT: Fine payment transactions
  - POLICE_STATION: Police station details
  - VIOLATION_TYPE: Types of traffic violations

- **Supabase Integration**: Secondary database for real-time features
  - Vehicle ownership history
  - Image storage (vehicle and violation images)
  - Real-time notifications

## Prerequisites

- Python 3.8+
- MySQL 8.0+
- CUDA-capable GPU (recommended for YOLOv8)
- Supabase account
- Web camera or image input device

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd traffic-fine-system
```

2. Create and activate virtual environment:
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
FLASK_SECRET_KEY=your_secret_key
YOLO_MODEL_PATH=models/license_plate_detection.pt
```

5. Initialize the database:
```bash
python database/setup_database.py
python database/create_admin.py  # Create admin user
python database/create_police.py  # Create police users
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Access the web interface:
```
http://localhost:5000
```

### User Types and Features

#### Driver Users
- View personal challans
- Pay pending fines
- View vehicle details
- Track payment history
- Update profile information

#### Police Users
- Record new violations
- View all challans
- Generate violation reports
- Manage vehicle records
- Track fine collections

#### Admin Users
- Manage police officers
- View system statistics
- Configure violation types
- Monitor transactions
- Generate reports

## API Endpoints

### Authentication
- POST /login: User login
- POST /register: New user registration
- GET /logout: User logout

### Violations
- POST /record-violation: Record new violation
- GET /view-challans: View challan list
- GET /challan/<id>: Get challan details
- POST /pay-challan/<id>: Process payment

### Vehicles
- GET /vehicles: List registered vehicles
- POST /vehicles: Register new vehicle
- GET /vehicle/<id>: Get vehicle details

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black .
flake8 .
```

### Database Maintenance
```bash
python database/clear_violations.py  # Reset violation types
python database/test_connection.py   # Test database connection
```

## Security Features

- Password hashing using bcrypt
- JWT-based authentication
- Role-based access control
- Secure file uploads
- Input validation and sanitization
- CSRF protection
- Rate limiting

## Troubleshooting

### Common Issues
1. Database Connection:
   - Verify MySQL credentials
   - Check database service status
   - Ensure proper permissions

2. Image Detection:
   - Verify CUDA installation
   - Check model path
   - Ensure sufficient lighting

3. Payment Processing:
   - Verify payment gateway configuration
   - Check transaction logs
   - Monitor payment status

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
- EasyOCR for text recognition
- Flask for web framework
- Supabase for real-time features
- Bootstrap for UI components
- MySQL for database management 