import os
import pyodbc
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

# Explicitly load the .env file from the project directory
load_dotenv()


print("DEBUG CHECK --> Server:", os.getenv('DB_SERVER'))
print("DEBUG CHECK --> User:", os.getenv('DB_USER'))
print("DEBUG CHECK --> Password Loaded?:", "YES" if os.getenv('DB_PASSWORD') else "NO")

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key')

def get_db_connection():
    server = os.getenv('DB_SERVER')
    port = os.getenv('DB_PORT')
    database = os.getenv('DB_NAME')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    
    connection_string = (
    f"Driver={{MariaDB Unicode}};"
    f"Server={os.getenv('DB_SERVER')};"
    f"Port={os.getenv('DB_PORT')};"
    f"Database={os.getenv('DB_NAME')};"
    f"User={os.getenv('DB_USER')};"
    f"Password={os.getenv('DB_PASSWORD')};"
    f"Option=3;"
)
    connection = pyodbc.connect(connection_string)
    return connection

@app.route('/')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) AS count FROM vehicles")
    vehicle_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) AS count FROM customer")
    customer_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) AS count FROM mechanic")
    mechanic_count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    metrics = {
        'vehicles': vehicle_count,
        'customers': customer_count,
        'mechanics': mechanic_count
    }
    
    return render_template('dashboard.html', entity=None, metrics=metrics)

@app.route('/manage/<entity>')
def manage(entity):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    data = []
    extra_data = {}
    
    try:
        if entity == 'customer':
            cursor.execute("SELECT * FROM customer")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        elif entity == 'company':
            cursor.execute("SELECT * FROM company")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        elif entity == 'vehicle':
            cursor.execute("SELECT * FROM vehicles")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.execute("SELECT company_id FROM company")
            comp_cols = [col[0] for col in cursor.description]
            extra_data['companies'] = [dict(zip(comp_cols, row)) for row in cursor.fetchall()]
        elif entity == 'mechanic':
            cursor.execute("SELECT * FROM mechanic")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        elif entity == 'service':
            cursor.execute("SELECT * FROM service")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.execute("SELECT customer_id FROM customer")
            cust_cols = [col[0] for col in cursor.description]
            extra_data['customers'] = [dict(zip(cust_cols, row)) for row in cursor.fetchall()]
        elif entity == 'part':
            cursor.execute("SELECT * FROM spare_parts")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        elif entity == 'maintenance':
            cursor.execute("SELECT * FROM maintenance")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.execute("SELECT company_id FROM company")
            comp_cols = [col[0] for col in cursor.description]
            extra_data['companies'] = [dict(zip(comp_cols, row)) for row in cursor.fetchall()]
        elif entity == 'warranty':
            cursor.execute("SELECT * FROM warranty")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.execute("SELECT license_number FROM vehicles")
            veh_cols = [col[0] for col in cursor.description]
            extra_data['vehicles'] = [dict(zip(veh_cols, row)) for row in cursor.fetchall()]
        elif entity == 'fuel':
            cursor.execute("SELECT * FROM fuel")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        elif entity == 'availability':
            cursor.execute("SELECT * FROM availability")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.execute("SELECT mechanic_id FROM mechanic")
            mech_cols = [col[0] for col in cursor.description]
            extra_data['mechanics'] = [dict(zip(mech_cols, row)) for row in cursor.fetchall()]
            cursor.execute("SELECT spare_part_id FROM spare_parts")
            part_cols = [col[0] for col in cursor.description]
            extra_data['parts'] = [dict(zip(part_cols, row)) for row in cursor.fetchall()]
        elif entity == 'vehicle_requirements':
            cursor.execute("SELECT * FROM vehicle_requirements")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.execute("SELECT license_number FROM vehicles")
            veh_cols = [col[0] for col in cursor.description]
            extra_data['vehicles'] = [dict(zip(veh_cols, row)) for row in cursor.fetchall()]
        elif entity == 'service_requirements':
            cursor.execute("SELECT * FROM service_requirements")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.execute("SELECT service_id FROM service")
            serv_cols = [col[0] for col in cursor.description]
            extra_data['services'] = [dict(zip(serv_cols, row)) for row in cursor.fetchall()]
            cursor.execute("SELECT mechanic_id FROM mechanic")
            mech_cols = [col[0] for col in cursor.description]
            extra_data['mechanics'] = [dict(zip(mech_cols, row)) for row in cursor.fetchall()]
            cursor.execute("SELECT spare_part_id FROM spare_parts")
            part_cols = [col[0] for col in cursor.description]
            extra_data['parts'] = [dict(zip(part_cols, row)) for row in cursor.fetchall()]
    except Exception as e:
        flash(f"Error loading data: {e}", "error")
    finally:
        cursor.close()
        conn.close()
        
    return render_template('dashboard.html', entity=entity, data=data, extra_data=extra_data)

# --- ADD ROUTES ---

@app.route('/add_customer', methods=['POST'])
def add_customer():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO customer (customer_id, firstname, middlename, lastname, phone_number) VALUES (?, ?, ?, ?, ?)",
                       (request.form['customer_id'], request.form['firstname'], request.form['middlename'], request.form['lastname'], request.form['phone_number']))
        conn.commit()
        flash("Customer added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='customer'))

@app.route('/add_company', methods=['POST'])
def add_company():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO company (company_id, name, area, city, state) VALUES (?, ?, ?, ?, ?)",
                       (request.form['company_id'], request.form['name'], request.form['area'], request.form['city'], request.form['state']))
        conn.commit()
        flash("Company added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='company'))

@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO vehicles (license_number, company_id, service_id, fuel_id, model, mfd_date) VALUES (?, ?, ?, ?, ?, ?)",
                       (request.form['license_number'], request.form['company_id'], request.form['service_id'], request.form['fuel_id'], request.form['model'], request.form['mfd_date']))
        conn.commit()
        flash("Vehicle added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='vehicle'))

@app.route('/add_mechanic', methods=['POST'])
def add_mechanic():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO mechanic (mechanic_id, name, skill_level, service_id) VALUES (?, ?, ?, ?)",
                       (request.form['mechanic_id'], request.form['name'], request.form['skill_level'], request.form['service_id']))
        conn.commit()
        flash("Mechanic added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='mechanic'))

@app.route('/add_service', methods=['POST'])
def add_service():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO service (service_id, customer_id, category, cost) VALUES (?, ?, ?, ?)",
                       (request.form['service_id'], request.form['customer_id'], request.form['category'], request.form['cost']))
        conn.commit()
        flash("Service added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='service'))

@app.route('/add_part', methods=['POST'])
def add_part():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO spare_parts (spare_part_id, service_id, name, qty) VALUES (?, ?, ?, ?)",
                       (request.form['spare_part_id'], request.form['service_id'], request.form['name'], request.form['qty']))
        conn.commit()
        flash("Spare Part added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='part'))

@app.route('/add_maintenance', methods=['POST'])
def add_maintenance():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO maintenance (mlogno, companyid, date, description) VALUES (?, ?, ?, ?)",
                       (request.form['mlogno'], request.form['companyid'], request.form['date'], request.form['description']))
        conn.commit()
        flash("Maintenance record added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='maintenance'))

@app.route('/add_warranty', methods=['POST'])
def add_warranty():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO warranty (warranty_id, license_number, type, exp_date) VALUES (?, ?, ?, ?)",
                       (request.form['warranty_id'], request.form['license_number'], request.form['type'], request.form['exp_date']))
        conn.commit()
        flash("Warranty added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='warranty'))

@app.route('/eer')
def eer_diagram():
    return render_template('eer.html')

@app.route('/add_fuel', methods=['POST'])
def add_fuel():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO fuel (fuel_id, type, price, qty) VALUES (?, ?, ?, ?)",
                       (request.form['fuel_id'], request.form['type'], request.form['price'], request.form['qty']))
        conn.commit()
        flash("Fuel record added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='fuel'))

@app.route('/add_availability', methods=['POST'])
def add_availability():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO availability (mechanic_id, spare_part_id, availability) VALUES (?, ?, ?)",
                       (request.form['mechanic_id'], request.form['spare_part_id'], request.form['availability']))
        conn.commit()
        flash("Availability record added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='availability'))

@app.route('/add_vehicle_requirements', methods=['POST'])
def add_vehicle_requirements():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO vehicle_requirements (license_number, service_id, fuel_id) VALUES (?, ?, ?)",
                       (request.form['license_number'], request.form['service_id'], request.form['fuel_id']))
        conn.commit()
        flash("Vehicle requirement added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='vehicle_requirements'))

@app.route('/add_service_requirements', methods=['POST'])
def add_service_requirements():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO service_requirements (service_id, mechanic_id, spare_part_id) VALUES (?, ?, ?)",
                       (request.form['service_id'], request.form['mechanic_id'], request.form['spare_part_id']))
        conn.commit()
        flash("Service requirement added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='service_requirements'))

# --- EDIT ROUTES ---

@app.route('/edit_customer', methods=['POST'])
def edit_customer():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE customer SET firstname = ?, middlename = ?, lastname = ?, phone_number = ? WHERE customer_id = ?",
                       (request.form['firstname'], request.form['middlename'], request.form['lastname'], request.form['phone_number'], request.form['customer_id']))
        conn.commit()
        flash("Customer updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='customer'))

@app.route('/edit_company', methods=['POST'])
def edit_company():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE company SET name = ?, area = ?, city = ?, state = ? WHERE company_id = ?",
                       (request.form['name'], request.form['area'], request.form['city'], request.form['state'], request.form['company_id']))
        conn.commit()
        flash("Company updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='company'))

@app.route('/edit_vehicle', methods=['POST'])
def edit_vehicle():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE vehicles SET company_id = ?, service_id = ?, fuel_id = ?, model = ?, mfd_date = ? WHERE license_number = ?",
                       (request.form['company_id'], request.form['service_id'], request.form['fuel_id'], request.form['model'], request.form['mfd_date'], request.form['license_number']))
        conn.commit()
        flash("Vehicle updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='vehicle'))

@app.route('/edit_mechanic', methods=['POST'])
def edit_mechanic():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE mechanic SET name = ?, skill_level = ?, service_id = ? WHERE mechanic_id = ?",
                       (request.form['name'], request.form['skill_level'], request.form['service_id'], request.form['mechanic_id']))
        conn.commit()
        flash("Mechanic updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='mechanic'))

@app.route('/edit_service', methods=['POST'])
def edit_service():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE service SET customer_id = ?, category = ?, cost = ? WHERE service_id = ?",
                       (request.form['customer_id'], request.form['category'], request.form['cost'], request.form['service_id']))
        conn.commit()
        flash("Service updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='service'))

@app.route('/edit_part', methods=['POST'])
def edit_part():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE spare_parts SET service_id = ?, name = ?, qty = ? WHERE spare_part_id = ?",
                       (request.form['service_id'], request.form['name'], request.form['qty'], request.form['spare_part_id']))
        conn.commit()
        flash("Spare Part updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='part'))

@app.route('/edit_maintenance', methods=['POST'])
def edit_maintenance():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE maintenance SET companyid = ?, date = ?, description = ? WHERE mlogno = ?",
                       (request.form['companyid'], request.form['date'], request.form['description'], request.form['mlogno']))
        conn.commit()
        flash("Maintenance record updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='maintenance'))

@app.route('/edit_warranty', methods=['POST'])
def edit_warranty():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE warranty SET license_number = ?, type = ?, exp_date = ? WHERE warranty_id = ?",
                       (request.form['license_number'], request.form['type'], request.form['exp_date'], request.form['warranty_id']))
        conn.commit()
        flash("Warranty updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='warranty'))

@app.route('/edit_fuel', methods=['POST'])
def edit_fuel():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE fuel SET type = ?, price = ?, qty = ? WHERE fuel_id = ?",
                       (request.form['type'], request.form['price'], request.form['qty'], request.form['fuel_id']))
        conn.commit()
        flash("Fuel record updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='fuel'))

@app.route('/edit_availability', methods=['POST'])
def edit_availability():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE availability SET availability = ? WHERE mechanic_id = ? AND spare_part_id = ?",
                       (request.form['availability'], request.form['mechanic_id'], request.form['spare_part_id']))
        conn.commit()
        flash("Availability record updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='availability'))

@app.route('/edit_vehicle_requirements', methods=['POST'])
def edit_vehicle_requirements():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE vehicle_requirements SET service_id = ?, fuel_id = ? WHERE license_number = ?",
                       (request.form['service_id'], request.form['fuel_id'], request.form['license_number']))
        conn.commit()
        flash("Vehicle requirement updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='vehicle_requirements'))

@app.route('/edit_service_requirements', methods=['POST'])
def edit_service_requirements():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE service_requirements SET spare_part_id = ? WHERE service_id = ? AND mechanic_id = ?",
                       (request.form['spare_part_id'], request.form['service_id'], request.form['mechanic_id']))
        conn.commit()
        flash("Service requirement updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='service_requirements'))

# --- DELETE ROUTES ---

@app.route('/delete_customer/<customer_id>')
def delete_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM customer WHERE customer_id = ?", (customer_id,))
        conn.commit()
        flash("Customer deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='customer'))

@app.route('/delete_company/<company_id>')
def delete_company(company_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM company WHERE company_id = ?", (company_id,))
        conn.commit()
        flash("Company deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='company'))

@app.route('/delete_vehicle/<license_number>')
def delete_vehicle(license_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM vehicles WHERE license_number = ?", (license_number,))
        conn.commit()
        flash("Vehicle deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='vehicle'))

@app.route('/delete_mechanic/<mechanic_id>')
def delete_mechanic(mechanic_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM mechanic WHERE mechanic_id = ?", (mechanic_id,))
        conn.commit()
        flash("Mechanic deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='mechanic'))

@app.route('/delete_service/<service_id>')
def delete_service(service_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM service WHERE service_id = ?", (service_id,))
        conn.commit()
        flash("Service deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='service'))

@app.route('/delete_part/<part_id>')
def delete_part(part_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM spare_parts WHERE spare_part_id = ?", (part_id,))
        conn.commit()
        flash("Spare part deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='part'))

@app.route('/delete_maintenance/<mlogno>')
def delete_maintenance(mlogno):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM maintenance WHERE mlogno = ?", (mlogno,))
        conn.commit()
        flash("Maintenance record deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='maintenance'))

@app.route('/delete_warranty/<warranty_id>')
def delete_warranty(warranty_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM warranty WHERE warranty_id = ?", (warranty_id,))
        conn.commit()
        flash("Warranty deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='warranty'))

@app.route('/delete_fuel/<fuel_id>')
def delete_fuel(fuel_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM fuel WHERE fuel_id = ?", (fuel_id,))
        conn.commit()
        flash("Fuel record deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='fuel'))

@app.route('/delete_availability/<mechanic_id>')
def delete_availability(mechanic_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM availability WHERE mechanic_id = ?", (mechanic_id,))
        conn.commit()
        flash("Availability record deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='availability'))

@app.route('/delete_vehicle_requirements/<license_number>')
def delete_vehicle_requirements(license_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM vehicle_requirements WHERE license_number = ?", (license_number,))
        conn.commit()
        flash("Vehicle requirement deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='vehicle_requirements'))

@app.route('/delete_service_requirements/<service_id>')
def delete_service_requirements(service_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM service_requirements WHERE service_id = ?", (service_id,))
        conn.commit()
        flash("Service requirement deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='service_requirements'))

@app.route('/query_window', methods=['GET', 'POST'])
def query_window():
    result = None
    columns = None
    query = ""
    error = None
    
    if request.method == 'POST':
        query = request.form.get('query')
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            if query.strip().lower().startswith("select"):
                rows = cursor.fetchall()
                if rows:
                    columns = [col[0] for col in cursor.description]
                    result = [dict(zip(columns, row)) for row in rows]
                else:
                    result = []
            else:
                conn.commit()
                result = "Query executed successfully. Affected rows: " + str(cursor.rowcount)
        except Exception as e:
            error = str(e)
        finally:
            cursor.close()
            conn.close()
            
    return render_template('query.html', result=result, columns=columns, query=query, error=error)

if __name__ == '__main__':
    app.run(debug=True, port=5000)