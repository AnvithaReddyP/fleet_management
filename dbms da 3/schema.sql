-- =========================================================
-- CockroachDB / PostgreSQL Schema for Fleet Management System
-- =========================================================

-- Drop existing tables with CASCADE to cleanly drop dependent foreign keys
DROP TABLE IF EXISTS service_requirements CASCADE;
DROP TABLE IF EXISTS vehicle_requirements CASCADE;
DROP TABLE IF EXISTS availability CASCADE;
DROP TABLE IF EXISTS warranty CASCADE;
DROP TABLE IF EXISTS spare_parts CASCADE;
DROP TABLE IF EXISTS mechanic CASCADE;
DROP TABLE IF EXISTS maintenance CASCADE;
DROP TABLE IF EXISTS vehicles CASCADE;
DROP TABLE IF EXISTS service CASCADE;
DROP TABLE IF EXISTS customer CASCADE;
DROP TABLE IF EXISTS fuel CASCADE;
DROP TABLE IF EXISTS company CASCADE;

-- 1. Company Table
CREATE TABLE company (
    company_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    area VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100)
);

-- 2. Customer Table
CREATE TABLE customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    firstname VARCHAR(50) NOT NULL,
    middlename VARCHAR(50),
    lastname VARCHAR(50) NOT NULL,
    phone_number VARCHAR(20)
);

-- 3. Service Catalog Table
CREATE TABLE service (
    service_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    category VARCHAR(50) NOT NULL,
    cost DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON DELETE SET NULL
);

-- 4. Fuel Table
CREATE TABLE fuel (
    fuel_id VARCHAR(50) PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    qty FLOAT NOT NULL
);

-- 5. Vehicles Table
CREATE TABLE vehicles (
    license_number VARCHAR(50) PRIMARY KEY,
    company_id VARCHAR(50),
    service_id VARCHAR(50),
    fuel_id VARCHAR(50),
    model VARCHAR(100) NOT NULL,
    mfd_date DATE,
    FOREIGN KEY (company_id) REFERENCES company(company_id) ON DELETE SET NULL,
    FOREIGN KEY (service_id) REFERENCES service(service_id) ON DELETE SET NULL,
    FOREIGN KEY (fuel_id) REFERENCES fuel(fuel_id) ON DELETE SET NULL
);

-- 6. Mechanic Table
CREATE TABLE mechanic (
    mechanic_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    skill_level VARCHAR(50),
    service_id VARCHAR(50),
    FOREIGN KEY (service_id) REFERENCES service(service_id) ON DELETE SET NULL
);

-- 7. Spare Parts Table
CREATE TABLE spare_parts (
    spare_part_id VARCHAR(50) PRIMARY KEY,
    service_id VARCHAR(50),
    name VARCHAR(100) NOT NULL,
    qty INT NOT NULL DEFAULT 0,
    FOREIGN KEY (service_id) REFERENCES service(service_id) ON DELETE SET NULL
);

-- 8. Maintenance Logs Table
CREATE TABLE maintenance (
    mlogno VARCHAR(50) PRIMARY KEY,
    companyid VARCHAR(50),
    date DATE,
    description TEXT,
    FOREIGN KEY (companyid) REFERENCES company(company_id) ON DELETE CASCADE
);

-- 9. Warranty Table
CREATE TABLE warranty (
    warranty_id VARCHAR(50) PRIMARY KEY,
    license_number VARCHAR(50),
    type VARCHAR(50),
    exp_date DATE,
    FOREIGN KEY (license_number) REFERENCES vehicles(license_number) ON DELETE CASCADE
);

-- 10. Availability (Bridge Table: Mechanics & Spare Parts)
CREATE TABLE availability (
    mechanic_id VARCHAR(50),
    spare_part_id VARCHAR(50),
    availability VARCHAR(50),
    PRIMARY KEY (mechanic_id, spare_part_id),
    FOREIGN KEY (mechanic_id) REFERENCES mechanic(mechanic_id) ON DELETE CASCADE,
    FOREIGN KEY (spare_part_id) REFERENCES spare_parts(spare_part_id) ON DELETE CASCADE
);

-- 11. Vehicle Requirements Table
CREATE TABLE vehicle_requirements (
    license_number VARCHAR(50) PRIMARY KEY,
    service_id VARCHAR(50),
    fuel_id VARCHAR(50),
    FOREIGN KEY (license_number) REFERENCES vehicles(license_number) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES service(service_id) ON DELETE SET NULL,
    FOREIGN KEY (fuel_id) REFERENCES fuel(fuel_id) ON DELETE SET NULL
);

-- 12. Service Requirements (Bridge Table: Services, Mechanics, & Spare Parts)
CREATE TABLE service_requirements (
    service_id VARCHAR(50),
    mechanic_id VARCHAR(50),
    spare_part_id VARCHAR(50),
    PRIMARY KEY (service_id, mechanic_id, spare_part_id),
    FOREIGN KEY (service_id) REFERENCES service(service_id) ON DELETE CASCADE,
    FOREIGN KEY (mechanic_id) REFERENCES mechanic(mechanic_id) ON DELETE CASCADE,
    FOREIGN KEY (spare_part_id) REFERENCES spare_parts(spare_part_id) ON DELETE CASCADE
);