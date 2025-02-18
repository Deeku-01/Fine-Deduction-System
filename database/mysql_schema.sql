-- Create database
CREATE DATABASE IF NOT EXISTS traffic_fine_system;
USE traffic_fine_system;

-- Create USER table
CREATE TABLE IF NOT EXISTS USER (
    user_id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    l_no VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    user_type ENUM('driver', 'admin') NOT NULL DEFAULT 'driver',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create POLICE table
CREATE TABLE IF NOT EXISTS POLICE (
    police_id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    badge_number VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    rank VARCHAR(50) NOT NULL,
    station VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create POLICE_STATION table
CREATE TABLE IF NOT EXISTS POLICE_STATION (
    station_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(255) NOT NULL,
    contact_no VARCHAR(20)
);

-- Create STATION_ASSIGNMENT table
CREATE TABLE IF NOT EXISTS STATION_ASSIGNMENT (
    assignment_id VARCHAR(36) PRIMARY KEY,
    police_id VARCHAR(36),
    station_id VARCHAR(36),
    start_date DATE NOT NULL,
    end_date DATE,
    FOREIGN KEY (police_id) REFERENCES POLICE(police_id),
    FOREIGN KEY (station_id) REFERENCES POLICE_STATION(station_id)
);

-- Create VEHICLE table
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
);

-- Create VIOLATION_TYPE table
CREATE TABLE IF NOT EXISTS VIOLATION_TYPE (
    type_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    base_fine_amt DECIMAL(10,2) NOT NULL,
    description TEXT
);

-- Create CHALLAN table
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
    payment_date TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES VEHICLE(vehicle_id),
    FOREIGN KEY (issued_by) REFERENCES POLICE(police_id),
    FOREIGN KEY (violation_type) REFERENCES VIOLATION_TYPE(type_id)
);

-- Create PAYMENT table
CREATE TABLE IF NOT EXISTS PAYMENT (
    payment_id VARCHAR(36) PRIMARY KEY,
    challan_id VARCHAR(36),
    amt DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),
    transaction_id VARCHAR(100),
    status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (challan_id) REFERENCES CHALLAN(challan_id)
); 