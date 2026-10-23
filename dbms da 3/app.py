import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from dotenv import load_dotenv

# Explicitly load the .env file from the project directory
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fleet_management_secure_secret_key')

def get_db_connection():
    """
    Connect to CockroachDB using:
    1. DATABASE_URL / COCKROACH_URL (CockroachDB Cloud single connection string)
    2. Or individual variables: DB_HOST (or DB_SERVER), DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DB_SSLMODE
    """
    db_url = os.getenv('DATABASE_URL') or os.getenv('COCKROACH_URL') or os.getenv('DB_URI')
    if db_url:
        if 'sslmode=verify-full' in db_url and 'sslrootcert=' not in db_url:
            try:
                import certifi
                db_url += f"&sslrootcert={certifi.where()}"
            except ImportError:
                db_url = db_url.replace('sslmode=verify-full', 'sslmode=require')
        return psycopg2.connect(db_url)
    
    host = os.getenv('DB_HOST') or os.getenv('DB_SERVER', 'localhost')
    port = int(os.getenv('DB_PORT', 26257))
    database = os.getenv('DB_NAME', 'defaultdb')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    sslmode = os.getenv('DB_SSLMODE', 'require')
    
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

def clean_val(v):
    """
    Convert empty string values to None so SQL foreign keys, dates, and numbers
    insert/update as NULL instead of invalid empty strings in CockroachDB.
    """
    if v is None:
        return None
    if isinstance(v, str):
        v = v.strip()
        return None if v == '' else v
    return v

def clean_params(params):
    return tuple(clean_val(p) for p in params)

# --- DASHBOARD ROUTE ---

@app.route('/')
def dashboard():
    vehicle_count = 0
    customer_count = 0
    mechanic_count = 0
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) AS count FROM vehicles")
        v_row = cursor.fetchone()
        vehicle_count = v_row[0] if v_row else 0
        
        cursor.execute("SELECT COUNT(*) AS count FROM customer")
        c_row = cursor.fetchone()
        customer_count = c_row[0] if c_row else 0
        
        cursor.execute("SELECT COUNT(*) AS count FROM mechanic")
        m_row = cursor.fetchone()
        mechanic_count = m_row[0] if m_row else 0
        
        cursor.close()
    except Exception as e:
        flash(f"CockroachDB Connection Notice: {e}", "error")
    finally:
        if conn:
            conn.close()
            
    metrics = {
        'vehicles': vehicle_count,
        'customers': customer_count,
        'mechanics': mechanic_count
    }
    
    return render_template('dashboard.html', entity=None, metrics=metrics)

# --- MANAGE ROUTE ---

@app.route('/manage/<entity>')
def manage(entity):
    conn = None
    data = []
    extra_data = {}
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if entity == 'customer':
            cursor.execute("SELECT * FROM customer ORDER BY customer_id")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        elif entity == 'company':
            cursor.execute("SELECT * FROM company ORDER BY company_id")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        elif entity == 'vehicle':
            cursor.execute("SELECT * FROM vehicles ORDER BY license_number")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.execute("SELECT company_id FROM company ORDER BY company_id")
            comp_cols = [col[0] for col in cursor.description]
            extra_data['companies'] = [dict(zip(comp_cols, row)) for row in cursor.fetchall()]

            cursor.execute("SELECT service_id, category FROM service ORDER BY service_id")
            srv_cols = [col[0] for col in cursor.description]
            extra_data['services'] = [dict(zip(srv_cols, row)) for row in cursor.fetchall()]

            cursor.execute("SELECT fuel_id, type FROM fuel ORDER BY fuel_id")
            fuel_cols = [col[0] for col in cursor.description]
            extra_data['fuels'] = [dict(zip(fuel_cols, row)) for row in cursor.fetchall()]
        elif entity == 'mechanic':
            cursor.execute("SELECT * FROM mechanic ORDER BY mechanic_id")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.execute("SELECT service_id, category FROM service ORDER BY service_id")
            srv_cols = [col[0] for col in cursor.description]
            extra_data['services'] = [dict(zip(srv_cols, row)) for row in cursor.fetchall()]
        elif entity == 'service':
            cursor.execute("SELECT * FROM service ORDER BY service_id")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.execute("SELECT customer_id FROM customer ORDER BY customer_id")
            cust_cols = [col[0] for col in cursor.description]
            extra_data['customers'] = [dict(zip(cust_cols, row)) for row in cursor.fetchall()]
        elif entity == 'part':
            cursor.execute("SELECT * FROM spare_parts ORDER BY spare_part_id")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.execute("SELECT service_id, category FROM service ORDER BY service_id")
            srv_cols = [col[0] for col in cursor.description]
            extra_data['services'] = [dict(zip(srv_cols, row)) for row in cursor.fetchall()]
        elif entity == 'maintenance':
            cursor.execute("SELECT * FROM maintenance ORDER BY mlogno")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.execute("SELECT company_id FROM company ORDER BY company_id")
            comp_cols = [col[0] for col in cursor.description]
            extra_data['companies'] = [dict(zip(comp_cols, row)) for row in cursor.fetchall()]
        elif entity == 'warranty':
            cursor.execute("SELECT * FROM warranty ORDER BY warranty_id")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.execute("SELECT license_number FROM vehicles ORDER BY license_number")
            veh_cols = [col[0] for col in cursor.description]
            extra_data['vehicles'] = [dict(zip(veh_cols, row)) for row in cursor.fetchall()]
        elif entity == 'fuel':
            cursor.execute("SELECT * FROM fuel ORDER BY fuel_id")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        elif entity == 'availability':
            cursor.execute("SELECT * FROM availability ORDER BY mechanic_id, spare_part_id")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.execute("SELECT mechanic_id FROM mechanic ORDER BY mechanic_id")
            mech_cols = [col[0] for col in cursor.description]
            extra_data['mechanics'] = [dict(zip(mech_cols, row)) for row in cursor.fetchall()]
            
            cursor.execute("SELECT spare_part_id FROM spare_parts ORDER BY spare_part_id")
            part_cols = [col[0] for col in cursor.description]
            extra_data['parts'] = [dict(zip(part_cols, row)) for row in cursor.fetchall()]
        elif entity == 'vehicle_requirements':
            cursor.execute("SELECT * FROM vehicle_requirements ORDER BY license_number")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.execute("SELECT license_number FROM vehicles ORDER BY license_number")
            veh_cols = [col[0] for col in cursor.description]
            extra_data['vehicles'] = [dict(zip(veh_cols, row)) for row in cursor.fetchall()]
        elif entity == 'service_requirements':
            cursor.execute("SELECT * FROM service_requirements ORDER BY service_id, mechanic_id, spare_part_id")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.execute("SELECT service_id FROM service ORDER BY service_id")
            serv_cols = [col[0] for col in cursor.description]
            extra_data['services'] = [dict(zip(serv_cols, row)) for row in cursor.fetchall()]
            
            cursor.execute("SELECT mechanic_id FROM mechanic ORDER BY mechanic_id")
            mech_cols = [col[0] for col in cursor.description]
            extra_data['mechanics'] = [dict(zip(mech_cols, row)) for row in cursor.fetchall()]
            
            cursor.execute("SELECT spare_part_id FROM spare_parts ORDER BY spare_part_id")
            part_cols = [col[0] for col in cursor.description]
            extra_data['parts'] = [dict(zip(part_cols, row)) for row in cursor.fetchall()]
            
        cursor.close()
    except Exception as e:
        flash(f"Error loading data from CockroachDB: {e}", "error")
    finally:
        if conn:
            conn.close()
            
    return render_template('dashboard.html', entity=entity, data=data, extra_data=extra_data)

# --- ADD ROUTES ---

@app.route('/add_customer', methods=['POST'])
def add_customer():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('customer_id'),
            request.form.get('firstname'),
            request.form.get('middlename'),
            request.form.get('lastname'),
            request.form.get('phone_number')
        ))
        cursor.execute(
            "INSERT INTO customer (customer_id, firstname, middlename, lastname, phone_number) VALUES (%s, %s, %s, %s, %s)",
            params
        )
        conn.commit()
        cursor.close()
        flash("Customer added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='customer'))

@app.route('/add_company', methods=['POST'])
def add_company():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('company_id'),
            request.form.get('name'),
            request.form.get('area'),
            request.form.get('city'),
            request.form.get('state')
        ))
        cursor.execute(
            "INSERT INTO company (company_id, name, area, city, state) VALUES (%s, %s, %s, %s, %s)",
            params
        )
        conn.commit()
        cursor.close()
        flash("Company added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='company'))

@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('license_number'),
            request.form.get('company_id'),
            request.form.get('service_id'),
            request.form.get('fuel_id'),
            request.form.get('model'),
            request.form.get('mfd_date')
        ))
        cursor.execute(
            "INSERT INTO vehicles (license_number, company_id, service_id, fuel_id, model, mfd_date) VALUES (%s, %s, %s, %s, %s, %s) RETURNING license_number",
            params
        )
        new_vehicle_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        flash("Vehicle added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='vehicle'))

@app.route('/add_mechanic', methods=['POST'])
def add_mechanic():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('mechanic_id'),
            request.form.get('name'),
            request.form.get('skill_level'),
            request.form.get('service_id')
        ))
        cursor.execute(
            "INSERT INTO mechanic (mechanic_id, name, skill_level, service_id) VALUES (%s, %s, %s, %s)",
            params
        )
        conn.commit()
        cursor.close()
        flash("Mechanic added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='mechanic'))

@app.route('/add_service', methods=['POST'])
def add_service():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('service_id'),
            request.form.get('customer_id'),
            request.form.get('category'),
            request.form.get('cost')
        ))
        cursor.execute(
            "INSERT INTO service (service_id, customer_id, category, cost) VALUES (%s, %s, %s, %s)",
            params
        )
        conn.commit()
        cursor.close()
        flash("Service added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='service'))

@app.route('/add_part', methods=['POST'])
def add_part():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('spare_part_id'),
            request.form.get('service_id'),
            request.form.get('name'),
            request.form.get('qty')
        ))
        cursor.execute(
            "INSERT INTO spare_parts (spare_part_id, service_id, name, qty) VALUES (%s, %s, %s, %s)",
            params
        )
        conn.commit()
        cursor.close()
        flash("Spare Part added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='part'))

@app.route('/add_maintenance', methods=['POST'])
def add_maintenance():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('mlogno'),
            request.form.get('companyid'),
            request.form.get('date'),
            request.form.get('description')
        ))
        cursor.execute(
            "INSERT INTO maintenance (mlogno, companyid, date, description) VALUES (%s, %s, %s, %s)",
            params
        )
        conn.commit()
        cursor.close()
        flash("Maintenance record added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='maintenance'))

@app.route('/add_warranty', methods=['POST'])
def add_warranty():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('warranty_id'),
            request.form.get('license_number'),
            request.form.get('type'),
            request.form.get('exp_date')
        ))
        cursor.execute(
            "INSERT INTO warranty (warranty_id, license_number, type, exp_date) VALUES (%s, %s, %s, %s)",
            params
        )
        conn.commit()
        cursor.close()
        flash("Warranty added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='warranty'))

@app.route('/eer')
def eer_diagram():
    return render_template('eer.html')

@app.route('/add_fuel', methods=['POST'])
def add_fuel():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('fuel_id'),
            request.form.get('type'),
            request.form.get('price'),
            request.form.get('qty')
        ))
        cursor.execute(
            "INSERT INTO fuel (fuel_id, type, price, qty) VALUES (%s, %s, %s, %s)",
            params
        )
        conn.commit()
        cursor.close()
        flash("Fuel record added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='fuel'))

@app.route('/add_availability', methods=['POST'])
def add_availability():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('mechanic_id'),
            request.form.get('spare_part_id'),
            request.form.get('availability')
        ))
        cursor.execute(
            "INSERT INTO availability (mechanic_id, spare_part_id, availability) VALUES (%s, %s, %s)",
            params
        )
        conn.commit()
        cursor.close()
        flash("Availability record added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='availability'))

@app.route('/add_vehicle_requirements', methods=['POST'])
def add_vehicle_requirements():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('license_number'),
            request.form.get('service_id'),
            request.form.get('fuel_id')
        ))
        cursor.execute(
            "INSERT INTO vehicle_requirements (license_number, service_id, fuel_id) VALUES (%s, %s, %s)",
            params
        )
        conn.commit()
        cursor.close()
        flash("Vehicle requirement added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='vehicle_requirements'))

@app.route('/add_service_requirements', methods=['POST'])
def add_service_requirements():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('service_id'),
            request.form.get('mechanic_id'),
            request.form.get('spare_part_id')
        ))
        cursor.execute(
            "INSERT INTO service_requirements (service_id, mechanic_id, spare_part_id) VALUES (%s, %s, %s)",
            params
        )
        conn.commit()
        cursor.close()
        flash("Service requirement added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='service_requirements'))

# --- EDIT ROUTES ---

@app.route('/edit_customer', methods=['POST'])
def edit_customer():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('firstname'),
            request.form.get('middlename'),
            request.form.get('lastname'),
            request.form.get('phone_number'),
            request.form.get('customer_id')
        ))
        cursor.execute(
            "UPDATE customer SET firstname = %s, middlename = %s, lastname = %s, phone_number = %s WHERE customer_id = %s",
            params
        )
        conn.commit()
        cursor.close()
        flash("Customer updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='customer'))

@app.route('/edit_company', methods=['POST'])
def edit_company():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('name'),
            request.form.get('area'),
            request.form.get('city'),
            request.form.get('state'),
            request.form.get('company_id')
        ))
        cursor.execute(
            "UPDATE company SET name = %s, area = %s, city = %s, state = %s WHERE company_id = %s",
            params
        )
        conn.commit()
        cursor.close()
        flash("Company updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='company'))

@app.route('/edit_vehicle', methods=['POST'])
def edit_vehicle():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('company_id'),
            request.form.get('service_id'),
            request.form.get('fuel_id'),
            request.form.get('model'),
            request.form.get('mfd_date'),
            request.form.get('license_number')
        ))
        cursor.execute(
            "UPDATE vehicles SET company_id = %s, service_id = %s, fuel_id = %s, model = %s, mfd_date = %s WHERE license_number = %s",
            params
        )
        conn.commit()
        cursor.close()
        flash("Vehicle updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='vehicle'))

@app.route('/edit_mechanic', methods=['POST'])
def edit_mechanic():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('name'),
            request.form.get('skill_level'),
            request.form.get('service_id'),
            request.form.get('mechanic_id')
        ))
        cursor.execute(
            "UPDATE mechanic SET name = %s, skill_level = %s, service_id = %s WHERE mechanic_id = %s",
            params
        )
        conn.commit()
        cursor.close()
        flash("Mechanic updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='mechanic'))

@app.route('/edit_service', methods=['POST'])
def edit_service():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('customer_id'),
            request.form.get('category'),
            request.form.get('cost'),
            request.form.get('service_id')
        ))
        cursor.execute(
            "UPDATE service SET customer_id = %s, category = %s, cost = %s WHERE service_id = %s",
            params
        )
        conn.commit()
        cursor.close()
        flash("Service updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='service'))

@app.route('/edit_part', methods=['POST'])
def edit_part():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('service_id'),
            request.form.get('name'),
            request.form.get('qty'),
            request.form.get('spare_part_id')
        ))
        cursor.execute(
            "UPDATE spare_parts SET service_id = %s, name = %s, qty = %s WHERE spare_part_id = %s",
            params
        )
        conn.commit()
        cursor.close()
        flash("Spare Part updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='part'))

@app.route('/edit_maintenance', methods=['POST'])
def edit_maintenance():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('companyid'),
            request.form.get('date'),
            request.form.get('description'),
            request.form.get('mlogno')
        ))
        cursor.execute(
            "UPDATE maintenance SET companyid = %s, date = %s, description = %s WHERE mlogno = %s",
            params
        )
        conn.commit()
        cursor.close()
        flash("Maintenance record updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='maintenance'))

@app.route('/edit_warranty', methods=['POST'])
def edit_warranty():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('license_number'),
            request.form.get('type'),
            request.form.get('exp_date'),
            request.form.get('warranty_id')
        ))
        cursor.execute(
            "UPDATE warranty SET license_number = %s, type = %s, exp_date = %s WHERE warranty_id = %s",
            params
        )
        conn.commit()
        cursor.close()
        flash("Warranty updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='warranty'))

@app.route('/edit_fuel', methods=['POST'])
def edit_fuel():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('type'),
            request.form.get('price'),
            request.form.get('qty'),
            request.form.get('fuel_id')
        ))
        cursor.execute(
            "UPDATE fuel SET type = %s, price = %s, qty = %s WHERE fuel_id = %s",
            params
        )
        conn.commit()
        cursor.close()
        flash("Fuel record updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='fuel'))

@app.route('/edit_availability', methods=['POST'])
def edit_availability():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('availability'),
            request.form.get('mechanic_id'),
            request.form.get('spare_part_id')
        ))
        cursor.execute(
            "UPDATE availability SET availability = %s WHERE mechanic_id = %s AND spare_part_id = %s",
            params
        )
        conn.commit()
        cursor.close()
        flash("Availability record updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='availability'))

@app.route('/edit_vehicle_requirements', methods=['POST'])
def edit_vehicle_requirements():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('service_id'),
            request.form.get('fuel_id'),
            request.form.get('license_number')
        ))
        cursor.execute(
            "UPDATE vehicle_requirements SET service_id = %s, fuel_id = %s WHERE license_number = %s",
            params
        )
        conn.commit()
        cursor.close()
        flash("Vehicle requirement updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='vehicle_requirements'))

@app.route('/edit_service_requirements', methods=['POST'])
def edit_service_requirements():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        params = clean_params((
            request.form.get('spare_part_id'),
            request.form.get('service_id'),
            request.form.get('mechanic_id')
        ))
        cursor.execute(
            "UPDATE service_requirements SET spare_part_id = %s WHERE service_id = %s AND mechanic_id = %s",
            params
        )
        conn.commit()
        cursor.close()
        flash("Service requirement updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='service_requirements'))

# --- DELETE ROUTES ---

@app.route('/delete_customer/<customer_id>')
def delete_customer(customer_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customer WHERE customer_id = %s", (customer_id,))
        conn.commit()
        cursor.close()
        flash("Customer deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='customer'))

@app.route('/delete_company/<company_id>')
def delete_company(company_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM company WHERE company_id = %s", (company_id,))
        conn.commit()
        cursor.close()
        flash("Company deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='company'))

@app.route('/delete_vehicle/<license_number>')
def delete_vehicle(license_number):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vehicles WHERE license_number = %s", (license_number,))
        conn.commit()
        cursor.close()
        flash("Vehicle deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='vehicle'))

@app.route('/delete_mechanic/<mechanic_id>')
def delete_mechanic(mechanic_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mechanic WHERE mechanic_id = %s", (mechanic_id,))
        conn.commit()
        cursor.close()
        flash("Mechanic deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='mechanic'))

@app.route('/delete_service/<service_id>')
def delete_service(service_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM service WHERE service_id = %s", (service_id,))
        conn.commit()
        cursor.close()
        flash("Service deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='service'))

@app.route('/delete_part/<part_id>')
def delete_part(part_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM spare_parts WHERE spare_part_id = %s", (part_id,))
        conn.commit()
        cursor.close()
        flash("Spare part deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='part'))

@app.route('/delete_maintenance/<mlogno>')
def delete_maintenance(mlogno):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM maintenance WHERE mlogno = %s", (mlogno,))
        conn.commit()
        cursor.close()
        flash("Maintenance record deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='maintenance'))

@app.route('/delete_warranty/<warranty_id>')
def delete_warranty(warranty_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM warranty WHERE warranty_id = %s", (warranty_id,))
        conn.commit()
        cursor.close()
        flash("Warranty deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='warranty'))

@app.route('/delete_fuel/<fuel_id>')
def delete_fuel(fuel_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM fuel WHERE fuel_id = %s", (fuel_id,))
        conn.commit()
        cursor.close()
        flash("Fuel record deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='fuel'))

@app.route('/delete_availability/<mechanic_id>')
def delete_availability(mechanic_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM availability WHERE mechanic_id = %s", (mechanic_id,))
        conn.commit()
        cursor.close()
        flash("Availability record deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='availability'))

@app.route('/delete_vehicle_requirements/<license_number>')
def delete_vehicle_requirements(license_number):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vehicle_requirements WHERE license_number = %s", (license_number,))
        conn.commit()
        cursor.close()
        flash("Vehicle requirement deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='vehicle_requirements'))

@app.route('/delete_service_requirements/<service_id>')
def delete_service_requirements(service_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM service_requirements WHERE service_id = %s", (service_id,))
        conn.commit()
        cursor.close()
        flash("Service requirement deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('manage', entity='service_requirements'))

# --- QUERY WINDOW ---

@app.route('/query_window', methods=['GET', 'POST'])
def query_window():
    result = None
    columns = None
    query = ""
    error = None
    
    if request.method == 'POST':
        query = request.form.get('query', '')
        if query.strip():
            conn = None
            try:
                conn = get_db_connection()
                conn.autocommit = True
                cursor = conn.cursor()
                cursor.execute(query)
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    result = [dict(zip(columns, row)) for row in rows]
                else:
                    conn.commit()
                    result = f"Query executed successfully. Affected rows: {cursor.rowcount}"
                cursor.close()
            except Exception as e:
                error = str(e)
            finally:
                if conn:
                    conn.close()
            
    return render_template('query.html', result=result, columns=columns, query=query, error=error)
# --- ALERTS API ---

@app.route('/api/alerts')
def get_alerts():
    alerts = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Trigger 1: Low stock spare parts (Qty <= 5)
        cursor.execute("SELECT name, qty FROM spare_parts WHERE qty <= 5")
        for row in cursor.fetchall():
            alerts.append({
                "type": "warning", 
                "icon": "fa-exclamation-triangle",
                "message": f"Low Stock: {row[0]} (Qty: {row[1]})"
            })
            
        # Trigger 2: Warranties expiring in the next 30 days
        cursor.execute("""
            SELECT license_number, exp_date 
            FROM warranty 
            WHERE exp_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
        """)
        for row in cursor.fetchall():
            alerts.append({
                "type": "danger", 
                "icon": "fa-clock",
                "message": f"Expiring Warranty: Vehicle {row[0]} on {row[1]}"
            })
            
        cursor.close()
    except Exception as e:
        print(f"Alerts Error: {e}")
    finally:
        if conn:
            conn.close()
            
    return jsonify(alerts)
if __name__ == '__main__':
    app.run(debug=True, port=5000)