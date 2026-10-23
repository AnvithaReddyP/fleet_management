import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_connection():
    db_url = os.getenv('DATABASE_URL') or os.getenv('COCKROACH_URL') or os.getenv('DB_URI')
    if db_url:
        if 'sslmode=verify-full' in db_url and 'sslrootcert=' not in db_url:
            try:
                import certifi
                db_url += f"&sslrootcert={certifi.where()}"
            except ImportError:
                db_url = db_url.replace('sslmode=verify-full', 'sslmode=require')
        print("Connecting to CockroachDB cluster...")
        return psycopg2.connect(db_url)
    
    host = os.getenv('DB_HOST') or os.getenv('DB_SERVER', 'localhost')
    port = int(os.getenv('DB_PORT', 26257))
    database = os.getenv('DB_NAME', 'defaultdb')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    sslmode = os.getenv('DB_SSLMODE', 'require')
    
    print(f"Connecting to CockroachDB at {host}:{port}/{database} as {user}...")
    conn_params = {
        'host': host,
        'port': port,
        'dbname': database,
        'user': user,
    }
    if password:
        conn_params['password'] = password
    if sslmode:
        conn_params['sslmode'] = sslmode
    if sslmode == 'verify-full':
        try:
            import certifi
            conn_params['sslrootcert'] = certifi.where()
        except ImportError:
            conn_params['sslmode'] = 'require'
        
    return psycopg2.connect(**conn_params)

def init_schema(conn):
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    with conn.cursor() as cursor:
        print("Executing schema.sql on CockroachDB...")
        cursor.execute(schema_sql)
    conn.commit()
    print("Schema created successfully!")

def seed_sample_data(conn):
    with conn.cursor() as cur:
        print("Seeding sample fleet management data...")
        
        # 1. Company
        companies = [
            ('CMP01', 'Apex Logistics Corp', 'Industrial Park', 'Austin', 'Texas'),
            ('CMP02', 'Blue Horizon Express', 'Harbor Zone', 'Seattle', 'Washington'),
            ('CMP03', 'Metro Freight Systems', 'Downtown West', 'Chicago', 'Illinois'),
            ('CMP04', 'Vanguard Transport', 'South Hub', 'Atlanta', 'Georgia'),
        ]
        for c in companies:
            cur.execute("""
                INSERT INTO company (company_id, name, area, city, state)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (company_id) DO NOTHING;
            """, c)

        # 2. Customer
        customers = [
            ('CUST01', 'Alice', 'M', 'Johnson', '555-0192'),
            ('CUST02', 'David', 'R', 'Smith', '555-0143'),
            ('CUST03', 'Elena', 'S', 'Rodriguez', '555-0188'),
            ('CUST04', 'Michael', 'B', 'Chen', '555-0177'),
            ('CUST05', 'Sarah', 'K', 'Taylor', '555-0155'),
        ]
        for c in customers:
            cur.execute("""
                INSERT INTO customer (customer_id, firstname, middlename, lastname, phone_number)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (customer_id) DO NOTHING;
            """, c)

        # 3. Fuel
        fuels = [
            ('FUEL01', 'Ultra-Low Sulfur Diesel', 3.85, 5200.0),
            ('FUEL02', 'Premium Gasoline 93', 4.15, 3100.0),
            ('FUEL03', 'Compressed Natural Gas (CNG)', 2.65, 1800.0),
            ('FUEL04', 'EV Commercial Fast Charge', 0.28, 9500.0),
        ]
        for f in fuels:
            cur.execute("""
                INSERT INTO fuel (fuel_id, type, price, qty)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (fuel_id) DO NOTHING;
            """, f)

        # 4. Service
        services = [
            ('SRV01', 'CUST01', 'Full Engine Overhaul', 1850.00),
            ('SRV02', 'CUST02', 'Hydraulic Brake System Inspection', 320.00),
            ('SRV03', 'CUST03', 'Transmission Fluid Flush & Replacement', 450.00),
            ('SRV04', 'CUST04', 'Commercial Alignment & Tire Rotation', 220.00),
            ('SRV05', 'CUST05', 'High-Voltage Battery Diagnostics', 580.00),
        ]
        for s in services:
            cur.execute("""
                INSERT INTO service (service_id, customer_id, category, cost)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (service_id) DO NOTHING;
            """, s)

        # 5. Vehicles
        vehicles = [
            ('TX-8821-HD', 'CMP01', 'SRV01', 'FUEL01', 'Freightliner Cascadia 126', '2021-03-15'),
            ('WA-4412-EX', 'CMP02', 'SRV02', 'FUEL01', 'Kenworth T680', '2022-06-20'),
            ('IL-9903-MF', 'CMP03', 'SRV03', 'FUEL02', 'Ford F-650 Super Duty', '2020-11-05'),
            ('GA-1033-VT', 'CMP04', 'SRV04', 'FUEL03', 'Peterbilt 579 CNG', '2023-01-18'),
            ('TX-3309-EV', 'CMP01', 'SRV05', 'FUEL04', 'Tesla Semi Long Haul', '2023-08-10'),
        ]
        for v in vehicles:
            cur.execute("""
                INSERT INTO vehicles (license_number, company_id, service_id, fuel_id, model, mfd_date)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (license_number) DO NOTHING;
            """, v)

        # 6. Mechanic
        mechanics = [
            ('MECH01', 'Marcus Vance', 'Master Diesel Technician', 'SRV01'),
            ('MECH02', 'Rachel Diaz', 'Brake & Suspension Specialist', 'SRV02'),
            ('MECH03', 'Tariq Al-Mansoor', 'Transmission Specialist', 'SRV03'),
            ('MECH04', 'Jason Miller', 'Fleet Maintenance Tech II', 'SRV04'),
            ('MECH05', 'Maya Lin', 'EV High-Voltage Specialist', 'SRV05'),
        ]
        for m in mechanics:
            cur.execute("""
                INSERT INTO mechanic (mechanic_id, name, skill_level, service_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (mechanic_id) DO NOTHING;
            """, m)

        # 7. Spare Parts
        parts = [
            ('PRT01', 'SRV01', 'Turbocharger Core Assembly', 8),
            ('PRT02', 'SRV02', 'Heavy Duty Ceramic Brake Pads', 34),
            ('PRT03', 'SRV03', 'Synthetic Transmission Fluid (5 Gal)', 22),
            ('PRT04', 'SRV04', 'Tie Rod End Heavy Duty', 15),
            ('PRT05', 'SRV05', 'Thermal Management Coolant Pump', 6),
        ]
        for p in parts:
            cur.execute("""
                INSERT INTO spare_parts (spare_part_id, service_id, name, qty)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (spare_part_id) DO NOTHING;
            """, p)

        # 8. Maintenance Logs
        maintenance_logs = [
            ('LOG-1001', 'CMP01', '2024-01-15', 'Full routine inspection and turbo pressure sensor replacement.'),
            ('LOG-1002', 'CMP02', '2024-02-10', 'Brake pad replacement and brake line bleed test.'),
            ('LOG-1003', 'CMP03', '2024-02-28', 'Transmission diagnostic check and fluid replenishment.'),
            ('LOG-1004', 'CMP04', '2024-03-05', 'Steering gear check and front wheel computerized alignment.'),
        ]
        for ml in maintenance_logs:
            cur.execute("""
                INSERT INTO maintenance (mlogno, companyid, date, description)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (mlogno) DO NOTHING;
            """, ml)

        # 9. Warranty
        warranties = [
            ('WAR01', 'TX-8821-HD', 'Powertrain Extended 500k', '2026-03-15'),
            ('WAR02', 'WA-4412-EX', 'Full Bumper-to-Bumper', '2025-06-20'),
            ('WAR03', 'IL-9903-MF', 'Transmission Specialized', '2024-11-05'),
            ('WAR04', 'TX-3309-EV', 'High-Voltage Battery & Drive Unit', '2031-08-10'),
        ]
        for w in warranties:
            cur.execute("""
                INSERT INTO warranty (warranty_id, license_number, type, exp_date)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (warranty_id) DO NOTHING;
            """, w)

        # 10. Availability
        availabilities = [
            ('MECH01', 'PRT01', 'In Stock & Assigned'),
            ('MECH02', 'PRT02', 'Ready for Installation'),
            ('MECH03', 'PRT03', 'Reserved'),
            ('MECH04', 'PRT04', 'Awaiting Delivery'),
            ('MECH05', 'PRT05', 'In Stock'),
        ]
        for a in availabilities:
            cur.execute("""
                INSERT INTO availability (mechanic_id, spare_part_id, availability)
                VALUES (%s, %s, %s)
                ON CONFLICT (mechanic_id, spare_part_id) DO NOTHING;
            """, a)

        # 11. Vehicle Requirements
        v_reqs = [
            ('TX-8821-HD', 'SRV01', 'FUEL01'),
            ('WA-4412-EX', 'SRV02', 'FUEL01'),
            ('IL-9903-MF', 'SRV03', 'FUEL02'),
            ('GA-1033-VT', 'SRV04', 'FUEL03'),
            ('TX-3309-EV', 'SRV05', 'FUEL04'),
        ]
        for vr in v_reqs:
            cur.execute("""
                INSERT INTO vehicle_requirements (license_number, service_id, fuel_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (license_number) DO NOTHING;
            """, vr)

        # 12. Service Requirements
        s_reqs = [
            ('SRV01', 'MECH01', 'PRT01'),
            ('SRV02', 'MECH02', 'PRT02'),
            ('SRV03', 'MECH03', 'PRT03'),
            ('SRV04', 'MECH04', 'PRT04'),
            ('SRV05', 'MECH05', 'PRT05'),
        ]
        for sr in s_reqs:
            cur.execute("""
                INSERT INTO service_requirements (service_id, mechanic_id, spare_part_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (service_id, mechanic_id, spare_part_id) DO NOTHING;
            """, sr)

    conn.commit()
    print("Sample data seeded successfully!")

if __name__ == '__main__':
    try:
        connection = get_connection()
        print("Connected to CockroachDB successfully!")
        init_schema(connection)
        seed_sample_data(connection)
        connection.close()
        print("\n=== CockroachDB initialization complete! ===")
    except Exception as e:
        print(f"\n[ERROR] Failed to initialize CockroachDB: {e}")
