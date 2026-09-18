SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS service_requirements;
DROP TABLE IF EXISTS vehicle_requirements;
DROP TABLE IF EXISTS availability;
DROP TABLE IF EXISTS warranty;
DROP TABLE IF EXISTS spare_parts;
DROP TABLE IF EXISTS mechanic;
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS service;
DROP TABLE IF EXISTS fuel;
DROP TABLE IF EXISTS vehicles;
DROP TABLE IF EXISTS maintenance;
DROP TABLE IF EXISTS company;

CREATE TABLE company (
    company_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    area VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100)
);

CREATE TABLE maintenance (
    mlogno VARCHAR(50) PRIMARY KEY,
    companyid VARCHAR(50),
    date DATE,
    description TEXT,
    FOREIGN KEY (companyid) REFERENCES company(company_id) ON DELETE CASCADE
);

CREATE TABLE fuel (
    fuel_id VARCHAR(50) PRIMARY KEY,
    type VARCHAR(50),
    price DECIMAL(10,2),
    qty FLOAT
);

CREATE TABLE customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    firstname VARCHAR(50),
    middlename VARCHAR(50),
    lastname VARCHAR(50),
    phone_number VARCHAR(20)
);

CREATE TABLE service (
    service_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    category VARCHAR(50),
    cost DECIMAL(10,2),
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON DELETE SET NULL
);

CREATE TABLE vehicles (
    license_number VARCHAR(50) PRIMARY KEY,
    company_id VARCHAR(50),
    service_id VARCHAR(50),
    fuel_id VARCHAR(50),
    model VARCHAR(100),
    mfd_date DATE,
    FOREIGN KEY (company_id) REFERENCES company(company_id) ON DELETE SET NULL,
    FOREIGN KEY (service_id) REFERENCES service(service_id) ON DELETE SET NULL,
    FOREIGN KEY (fuel_id) REFERENCES fuel(fuel_id) ON DELETE SET NULL
);

CREATE TABLE mechanic (
    mechanic_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    skill_level VARCHAR(50),
    service_id VARCHAR(50),
    FOREIGN KEY (service_id) REFERENCES service(service_id) ON DELETE SET NULL
);

CREATE TABLE spare_parts (
    spare_part_id VARCHAR(50) PRIMARY KEY,
    service_id VARCHAR(50),
    name VARCHAR(100),
    qty INT,
    FOREIGN KEY (service_id) REFERENCES service(service_id) ON DELETE SET NULL
);

CREATE TABLE availability (
    mechanic_id VARCHAR(50),
    spare_part_id VARCHAR(50),
    availability VARCHAR(50),
    PRIMARY KEY (mechanic_id, spare_part_id),
    FOREIGN KEY (mechanic_id) REFERENCES mechanic(mechanic_id) ON DELETE CASCADE,
    FOREIGN KEY (spare_part_id) REFERENCES spare_parts(spare_part_id) ON DELETE CASCADE
);

CREATE TABLE warranty (
    warranty_id VARCHAR(50) PRIMARY KEY,
    license_number VARCHAR(50),
    type VARCHAR(50),
    exp_date DATE,
    FOREIGN KEY (license_number) REFERENCES vehicles(license_number) ON DELETE CASCADE
);

CREATE TABLE vehicle_requirements (
    license_number VARCHAR(50) PRIMARY KEY,
    service_id VARCHAR(50),
    fuel_id VARCHAR(50),
    FOREIGN KEY (license_number) REFERENCES vehicles(license_number) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES service(service_id) ON DELETE SET NULL,
    FOREIGN KEY (fuel_id) REFERENCES fuel(fuel_id) ON DELETE SET NULL
);

CREATE TABLE service_requirements (
    service_id VARCHAR(50),
    mechanic_id VARCHAR(50),
    spare_part_id VARCHAR(50),
    PRIMARY KEY (service_id, mechanic_id, spare_part_id),
    FOREIGN KEY (service_id) REFERENCES service(service_id) ON DELETE CASCADE,
    FOREIGN KEY (mechanic_id) REFERENCES mechanic(mechanic_id) ON DELETE CASCADE,
    FOREIGN KEY (spare_part_id) REFERENCES spare_parts(spare_part_id) ON DELETE CASCADE
);

SET FOREIGN_KEY_CHECKS = 1;