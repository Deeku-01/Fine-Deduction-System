from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
import requests

from src.database.mysql_connection import get_db_cursor
from src.database.supabase_connection import SupabaseConnection
from src.detection.license_plate_detector import LicensePlateDetector

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('API_SECRET_KEY', 'your-secret-key')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'static/uploads')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize services
detector = LicensePlateDetector()
supabase = SupabaseConnection()

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['user_id']
        self.email = user_data['email']
        self.name = user_data['name']
        self.user_type = user_data['user_type']
        self.l_no = user_data['l_no']
        self.badge_number = None
        self.police_rank = None
        self.station_id = None
        
        # If user is police, get additional details
        if self.user_type == 'police':
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT badge_number, police_rank, station_id 
                    FROM POLICE 
                    WHERE police_id = %s
                """, (self.id,))
                police_data = cursor.fetchone()
                if police_data:
                    self.badge_number = police_data['badge_number']
                    self.police_rank = police_data['police_rank']
                    self.station_id = police_data['station_id']

@login_manager.user_loader
def load_user(user_id):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM USER WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()
        return User(user_data) if user_data else None

@app.route('/')
def index():
    if current_user.is_authenticated:
        with get_db_cursor() as cursor:
            if current_user.user_type in ['admin', 'police']:
                # Get statistics for admin/police
                cursor.execute("SELECT COUNT(*) as total FROM challan WHERE status = 'pending'")
                pending_challans = cursor.fetchone()['total']
                
                cursor.execute("SELECT COUNT(*) as total FROM challan WHERE status = 'paid'")
                paid_challans = cursor.fetchone()['total']
                
                cursor.execute("SELECT SUM(fine_amt) as total FROM challan WHERE status = 'paid'")
                total_collection = cursor.fetchone()['total'] or 0
                
                return render_template('dashboard.html',
                                    pending_challans=pending_challans,
                                    paid_challans=paid_challans,
                                    total_collection=total_collection,
                                    user_type=current_user.user_type)
            else:
                # Get statistics for regular users
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_challans,
                        COUNT(CASE WHEN c.status = 'pending' THEN 1 END) as pending_challans,
                        COUNT(CASE WHEN c.status = 'paid' THEN 1 END) as paid_challans,
                        SUM(CASE WHEN c.status = 'paid' THEN c.fine_amt ELSE 0 END) as total_paid,
                        SUM(CASE WHEN c.status = 'pending' THEN c.fine_amt ELSE 0 END) as pending_amount
                    FROM vehicle v
                    LEFT JOIN challan c ON v.vehicle_id = c.vehicle_id
                    WHERE v.owner_id = %s OR v.reg_number = %s
                """, (current_user.id, current_user.l_no))
                stats = cursor.fetchone()
                
                return render_template('dashboard.html',
                                    user_stats=stats,
                                    user_type=current_user.user_type)
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM USER WHERE email = %s", (email,))
            user_data = cursor.fetchone()
            
            if user_data and check_password_hash(user_data['password'], password):
                user = User(user_data)
                login_user(user)
                flash('Logged in successfully!', 'success')
                return redirect(url_for('index'))
            
        flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        phone = request.form.get('phone')
        l_no = request.form.get('l_no')
        
        with get_db_cursor() as cursor:
            # Check if email exists
            cursor.execute("SELECT * FROM USER WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email already registered', 'danger')
                return redirect(url_for('register'))
            
            # Create new user
            user_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO USER (user_id, email, password, name, phone, l_no)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                email,
                generate_password_hash(password),
                name,
                phone,
                l_no
            ))
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
            
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/api/detect-plate', methods=['POST'])
@login_required
def detect_plate():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image uploaded'})
        
    image = request.files['image']
    if image.filename == '':
        return jsonify({'success': False, 'error': 'No image selected'})
        
    try:
        # Save image temporarily
        filename = secure_filename(f"temp_{uuid.uuid4()}.jpg")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)
        
        # Detect license plate
        plate_img, confidence, bbox = detector.detect_license_plate(filepath)
        
        if plate_img is None:
            os.remove(filepath)
            return jsonify({
                'success': False,
                'error': 'No license plate detected in the image. Please ensure the image contains a clear view of the license plate.'
            })
            
        # Process plate image with OCR
        processed_plate = detector.preprocess_plate_image(plate_img)
        if processed_plate is None:
            os.remove(filepath)
            return jsonify({
                'success': False,
                'error': 'Failed to process the detected license plate region. Please try with a clearer image.'
            })
            
        plate_text = detector.read_plate_text(processed_plate)
        
        # Clean up temporary file
        os.remove(filepath)
        
        if not plate_text:
            return jsonify({
                'success': False,
                'error': 'License plate detected but text could not be read. Please ensure the plate is clearly visible and well-lit.',
                'confidence': confidence
            })
        
        return jsonify({
            'success': True,
            'plate_number': plate_text,
            'confidence': confidence
        })
        
    except Exception as e:
        # Clean up in case of error
        if os.path.exists(filepath):
            os.remove(filepath)
        print(f"Error in detect_plate: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while processing the image. Please try again with a different image.'
        })

@app.route('/record-violation', methods=['GET', 'POST'])
@login_required
def record_violation():
    if current_user.user_type not in ['admin', 'police']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        try:
            # Handle image upload
            if 'image' not in request.files:
                return jsonify({'success': False, 'error': 'No image uploaded'})
                
            image = request.files['image']
            if image.filename == '':
                return jsonify({'success': False, 'error': 'No image selected'})
                
            # Save image and process
            filename = secure_filename(f"violation_{uuid.uuid4()}.jpg")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(filepath)
            
            # Initialize variables
            plate_img = None
            confidence = 0
            reg_number = request.form.get('reg_number')
            
            # Process image with license plate detection only if no manual entry
            if not reg_number:
                plate_img, confidence, bbox = detector.detect_license_plate(filepath)
                if plate_img is not None:
                    processed_plate = detector.preprocess_plate_image(plate_img)
                    plate_text = detector.read_plate_text(processed_plate)
                    reg_number = plate_text
            
            if not reg_number:
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({'success': False, 'error': 'No registration number detected or provided'})
            
            # Upload to Supabase
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_name = f"violations/{timestamp}_{uuid.uuid4()}.jpg"
            supabase.upload_image("challan-images", filepath, image_name)
            image_url = supabase.get_image_url("challan-images", image_name)
            
            # Database transaction
            with get_db_cursor() as cursor:
                # Check if vehicle exists
                cursor.execute("""
                    SELECT v.vehicle_id, v.owner_id, v.reg_number, u.user_id 
                    FROM vehicle v 
                    LEFT JOIN USER u ON v.reg_number = u.l_no 
                    WHERE v.reg_number = %s
                """, (reg_number,))
                vehicle = cursor.fetchone()
                
                vehicle_id = None
                if not vehicle:
                    # Create new vehicle record
                    vehicle_id = str(uuid.uuid4())
                    cursor.execute("""
                        INSERT INTO vehicle (
                            vehicle_id, reg_number, vehicle_type,
                            owner_id, created_at, is_active
                        ) VALUES (%s, %s, %s, %s, NOW(), TRUE)
                    """, (
                        vehicle_id,
                        reg_number,
                        request.form.get('vehicle_type', 'Unknown'),
                        None  # Owner will be updated later if found
                    ))
                    print(f"Created new vehicle record for {reg_number}")  # Debug log
                else:
                    vehicle_id = vehicle['vehicle_id']
                    print(f"Found existing vehicle: {vehicle}")  # Debug log
                
                # Get violation type details
                cursor.execute("""
                    SELECT base_fine_amt 
                    FROM violation_type 
                    WHERE type_id = %s
                """, (request.form.get('violation_type'),))
                violation = cursor.fetchone()
                if not violation:
                    raise Exception('Invalid violation type')
                
                # Create challan record
                challan_id = str(uuid.uuid4())
                challan_no = f"CHAL_{timestamp}"
                cursor.execute("""
                    INSERT INTO challan (
                        challan_id, challan_no, vehicle_id, issued_by,
                        violation_type, fine_amt, location, description,
                        image_url, status, issue_date
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', NOW())
                """, (
                    challan_id,
                    challan_no,
                    vehicle_id,
                    current_user.id,
                    request.form.get('violation_type'),
                    violation['base_fine_amt'],
                    request.form.get('location'),
                    request.form.get('description'),
                    image_url
                ))
                
                # Verify challan was created
                cursor.execute("""
                    SELECT * FROM challan WHERE challan_id = %s
                """, (challan_id,))
                new_challan = cursor.fetchone()
                if not new_challan:
                    raise Exception("Challan creation failed")
                print(f"Created new challan: {new_challan}")  # Debug log
            
            # Clean up
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return jsonify({
                'success': True,
                'challan_id': challan_id,
                'challan_no': challan_no,
                'plate_number': reg_number,
                'confidence': confidence
            })
            
        except Exception as e:
            print(f"Error recording violation: {str(e)}")  # Server-side logging
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'success': False, 'error': str(e)})
    
    # GET request - show form
    with get_db_cursor() as cursor:
        # Get violation types with DISTINCT to ensure uniqueness
        cursor.execute("""
            SELECT DISTINCT type_id, name, base_fine_amt 
            FROM violation_type 
            ORDER BY name ASC
        """)
        violation_types = cursor.fetchall()
        
        # Get police stations
        if current_user.user_type == 'police':
            cursor.execute("""
                SELECT station_id, name, location 
                FROM police_station 
                WHERE station_id = %s
            """, (current_user.station_id,))
        else:
            cursor.execute("""
                SELECT station_id, name, location 
                FROM police_station 
                ORDER BY name
            """)
        police_stations = cursor.fetchall()
        
        return render_template('record_violation.html',
                             violation_types=violation_types,
                             police_stations=police_stations,
                             current_user=current_user)

@app.route('/view-challans')
@login_required
def view_challans():
    try:
        with get_db_cursor() as cursor:
            if current_user.user_type == 'driver':
                # Get user's challans with vehicle and violation details
                cursor.execute("""
                    SELECT 
                        c.*,
                        v.reg_number,
                        v.vehicle_type,
                        vt.name as violation_name,
                        vt.base_fine_amt,
                        p.name as officer_name,
                        p.badge_number,
                        p.police_rank,
                        ps.name as station_name,
                        pm.payment_id,
                        pm.payment_method,
                        pm.transaction_id,
                        pm.created_at as payment_date
                    FROM vehicle v 
                    LEFT JOIN challan c ON v.vehicle_id = c.vehicle_id
                    LEFT JOIN violation_type vt ON c.violation_type = vt.type_id
                    LEFT JOIN POLICE p ON c.issued_by = p.police_id
                    LEFT JOIN police_station ps ON p.station_id = ps.station_id
                    LEFT JOIN payment pm ON c.challan_id = pm.challan_id
                    WHERE v.reg_number = %s
                       OR v.owner_id = %s 
                    ORDER BY c.issue_date DESC
                """, (current_user.l_no, current_user.id))
            else:
                # Get all challans for admin/police with additional details
                cursor.execute("""
                    SELECT 
                        c.*,
                        v.reg_number,
                        v.vehicle_type,
                        vt.name as violation_name,
                        vt.base_fine_amt,
                        p.name as officer_name,
                        p.badge_number,
                        p.police_rank,
                        ps.name as station_name,
                        pm.payment_id,
                        pm.payment_method,
                        pm.transaction_id,
                        pm.created_at as payment_date,
                        u.name as owner_name
                    FROM challan c
                    JOIN vehicle v ON c.vehicle_id = v.vehicle_id
                    JOIN violation_type vt ON c.violation_type = vt.type_id
                    LEFT JOIN POLICE p ON c.issued_by = p.police_id
                    LEFT JOIN police_station ps ON p.station_id = ps.station_id
                    LEFT JOIN payment pm ON c.challan_id = pm.challan_id
                    LEFT JOIN USER u ON v.owner_id = u.user_id
                    ORDER BY c.issue_date DESC
                """)
            
            challans = cursor.fetchall()
            print(f"Found {len(challans)} challans")  # Debug log
            
            # Debug: Print first challan details
            if challans:
                print("First challan details:", challans[0])
            
            return render_template('view_challans.html', challans=challans)
            
    except Exception as e:
        print(f"Error in view_challans: {str(e)}")  # Debug log
        flash('Error loading challans', 'danger')
        return redirect(url_for('index'))

@app.route('/pay-challan/<challan_id>', methods=['POST'])
@login_required
def pay_challan(challan_id):
    try:
        with get_db_cursor() as cursor:
            # Get challan details
            cursor.execute("""
                SELECT c.*, v.owner_id, v.reg_number, vt.name as violation_name
                FROM challan c
                JOIN vehicle v ON c.vehicle_id = v.vehicle_id
                JOIN violation_type vt ON c.violation_type = vt.type_id
                WHERE c.challan_id = %s
            """, (challan_id,))
            
            challan = cursor.fetchone()
            
            if not challan:
                return jsonify({'error': 'Challan not found'}), 404
                
            if challan['owner_id'] != current_user.id and current_user.user_type not in ['admin', 'police']:
                return jsonify({'error': 'Unauthorized'}), 403
                
            if challan['status'] != 'pending':
                return jsonify({'error': 'Challan is not pending'}), 400
                
            # Process payment
            payment_id = str(uuid.uuid4())
            payment_method = request.form.get('payment_method', 'online')
            transaction_id = f"TXN_{uuid.uuid4()}"
            
            # Create payment record
            cursor.execute("""
                INSERT INTO payment (
                    payment_id, challan_id, amt, payment_method,
                    transaction_id, status, created_at
                ) VALUES (%s, %s, %s, %s, %s, 'completed', NOW())
            """, (
                payment_id,
                challan_id,
                challan['fine_amt'],
                payment_method,
                transaction_id
            ))
            
            # Update challan status
            cursor.execute("""
                UPDATE challan
                SET status = 'paid', payment_date = NOW()
                WHERE challan_id = %s
            """, (challan_id,))
            
            return jsonify({
                'success': True,
                'message': 'Payment processed successfully',
                'payment_id': payment_id,
                'transaction_id': transaction_id
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile')
@login_required
def profile():
    try:
        with get_db_cursor() as cursor:
            if current_user.user_type == 'police':
                # Get police officer details
                cursor.execute("""
                    SELECT 
                        p.*,
                        ps.name as station_name,
                        ps.location as station_location
                    FROM POLICE p
                    LEFT JOIN police_station ps ON p.station_id = ps.station_id
                    WHERE p.police_id = %s
                """, (current_user.id,))
                police_data = cursor.fetchone()
                
                # Get total challans issued
                cursor.execute("""
                    SELECT COUNT(*) as total_challans,
                           COUNT(CASE WHEN status = 'paid' THEN 1 END) as paid_challans,
                           SUM(CASE WHEN status = 'paid' THEN fine_amt ELSE 0 END) as total_collection
                    FROM challan
                    WHERE issued_by = %s
                """, (current_user.id,))
                stats = cursor.fetchone()
                
                return render_template('profile.html', 
                                    user=current_user,
                                    police_data=police_data,
                                    stats=stats)
            else:
                # Get user's vehicles
                cursor.execute("""
                    SELECT v.* 
                    FROM vehicle v
                    WHERE v.owner_id = %s OR v.reg_number = %s
                """, (current_user.id, current_user.l_no))
                vehicles = cursor.fetchall()
                
                # Get challan statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_challans,
                        COUNT(CASE WHEN c.status = 'pending' THEN 1 END) as pending_challans,
                        COUNT(CASE WHEN c.status = 'paid' THEN 1 END) as paid_challans,
                        SUM(CASE WHEN c.status = 'paid' THEN c.fine_amt ELSE 0 END) as total_paid,
                        SUM(CASE WHEN c.status = 'pending' THEN c.fine_amt ELSE 0 END) as total_pending
                    FROM vehicle v
                    LEFT JOIN challan c ON v.vehicle_id = c.vehicle_id
                    WHERE v.owner_id = %s OR v.reg_number = %s
                """, (current_user.id, current_user.l_no))
                stats = cursor.fetchone()
                
                return render_template('profile.html', 
                                    user=current_user,
                                    vehicles=vehicles,
                                    stats=stats)
                
    except Exception as e:
        print(f"Error in profile: {str(e)}")
        flash('Error loading profile data', 'danger')
        return render_template('profile.html', user=current_user)

if __name__ == '__main__':
    app.run(debug=True) 