import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

def get_db_connection():
    # Connects using environment variables provided by Render/Aiven, falling back to local defaults if testing locally
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "fleet_management"),
        port=int(os.getenv("DB_PORT", 3306))
    )
    return connection

@app.route('/')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch metrics
    cursor.execute("SELECT COUNT(*) AS count FROM vehicle")
    vehicle_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) AS count FROM customer")
    customer_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) AS count FROM mechanic")
    mechanic_count = cursor.fetchone()['count']
    
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
    cursor = conn.cursor(dictionary=True)
    
    data = []
    extra_data = {}
    
    try:
        if entity == 'customer':
            cursor.execute("SELECT * FROM customer")
            data = cursor.fetchall()
        elif entity == 'company':
            cursor.execute("SELECT * FROM company")
            data = cursor.fetchall()
        elif entity == 'vehicle':
            cursor.execute("SELECT * FROM vehicle")
            data = cursor.fetchall()
            cursor.execute("SELECT Company_ID FROM company")
            extra_data['companies'] = cursor.fetchall()
        elif entity == 'mechanic':
            cursor.execute("SELECT * FROM mechanic")
            data = cursor.fetchall()
        elif entity == 'service':
            cursor.execute("SELECT * FROM service")
            data = cursor.fetchall()
            cursor.execute("SELECT License_no FROM vehicle")
            extra_data['vehicles'] = cursor.fetchall()
        elif entity == 'part':
            cursor.execute("SELECT * FROM spare_part")
            data = cursor.fetchall()
        elif entity == 'maintenance':
            cursor.execute("SELECT * FROM maintenance")
            data = cursor.fetchall()
            cursor.execute("SELECT Company_ID FROM company")
            extra_data['companies'] = cursor.fetchall()
        elif entity == 'warranty':
            cursor.execute("SELECT * FROM warranty")
            data = cursor.fetchall()
            cursor.execute("SELECT License_no FROM vehicle")
            extra_data['vehicles'] = cursor.fetchall()
        elif entity == 'fuel':
            cursor.execute("SELECT * FROM fuel")
            data = cursor.fetchall()
            cursor.execute("SELECT License_no FROM vehicle")
            extra_data['vehicles'] = cursor.fetchall()
        elif entity == 'availability':
            cursor.execute("SELECT * FROM availability")
            data = cursor.fetchall()
            cursor.execute("SELECT Mechanic_ID FROM mechanic")
            extra_data['mechanics'] = cursor.fetchall()
            cursor.execute("SELECT Part_ID FROM spare_part")
            extra_data['parts'] = cursor.fetchall()
        elif entity == 'vehicle_requirements':
            cursor.execute("SELECT * FROM vehicle_requirements")
            data = cursor.fetchall()
            cursor.execute("SELECT License_no FROM vehicle")
            extra_data['vehicles'] = cursor.fetchall()
        elif entity == 'service_requirements':
            cursor.execute("SELECT * FROM service_requirements")
            data = cursor.fetchall()
            cursor.execute("SELECT Service_ID FROM service")
            extra_data['services'] = cursor.fetchall()
            cursor.execute("SELECT Mechanic_ID FROM mechanic")
            extra_data['mechanics'] = cursor.fetchall()
            cursor.execute("SELECT Part_ID FROM spare_part")
            extra_data['parts'] = cursor.fetchall()
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
        cursor.execute("INSERT INTO customer (Customer_ID, First_Name, Last_Name, Ph_no) VALUES (%s, %s, %s, %s)",
                       (request.form['customer_id'], request.form['first_name'], request.form['last_name'], request.form['phone']))
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
        cursor.execute("INSERT INTO company (Company_ID, Location, Area, City, State) VALUES (%s, %s, %s, %s, %s)",
                       (request.form['company_id'], request.form['location'], request.form['area'], request.form['city'], request.form['state']))
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
        cursor.execute("INSERT INTO vehicle (License_no, Model, Mfd_Date, Company_ID) VALUES (%s, %s, %s, %s)",
                       (request.form['license_no'], request.form['model'], request.form['mfd_date'], request.form['company_id']))
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
        availability = 1 if 'availability' in request.form else 0
        cursor.execute("INSERT INTO mechanic (Mechanic_ID, Mechanic_name, Skill_level, Availability) VALUES (%s, %s, %s, %s)",
                       (request.form['mechanic_id'], request.form['mechanic_name'], request.form['skill_level'], availability))
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
        cursor.execute("INSERT INTO service (Service_ID, Cost, Category, License_no) VALUES (%s, %s, %s, %s)",
                       (request.form['service_id'], request.form['cost'], request.form['category'], request.form['license_no']))
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
        cursor.execute("INSERT INTO spare_part (Part_ID, Name, Quantity) VALUES (%s, %s, %s)",
                       (request.form['part_id'], request.form['name'], request.form['quantity']))
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
        cursor.execute("INSERT INTO maintenance (Maintenance_ID, Description, Maintenance_logo, Company_ID) VALUES (%s, %s, %s, %s)",
                       (request.form['maintenance_id'], request.form['description'], request.form['logo'], request.form['company_id']))
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
        cursor.execute("INSERT INTO warranty (Warranty_ID, Type, Expiration_date, License_no) VALUES (%s, %s, %s, %s)",
                       (request.form['warranty_id'], request.form['type'], request.form['exp_date'], request.form['license_no']))
        conn.commit()
        flash("Warranty added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='warranty'))

@app.route('/add_fuel', methods=['POST'])
def add_fuel():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO fuel (Fuel_ID, Type, Price, Total_price, License_no) VALUES (%s, %s, %s, %s, %s)",
                       (request.form['fuel_id'], request.form['type'], request.form['price'], request.form['total_price'], request.form['license_no']))
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
        cursor.execute("INSERT INTO availability (Mechanic_ID, Spare_Part_ID, Availability) VALUES (%s, %s, %s)",
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
        cursor.execute("INSERT INTO vehicle_requirements (License_no, Service_ID, Fuel_ID) VALUES (%s, %s, %s)",
                       (request.form['license_no'], request.form['service_id'], request.form['fuel_id']))
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
        cursor.execute("INSERT INTO service_requirements (Service_ID, Mechanic_ID, Spare_Part_ID) VALUES (%s, %s, %s)",
                       (request.form['service_id'], request.form['mechanic_id'], request.form['spare_part_id']))
        conn.commit()
        flash("Service requirement added successfully!", "success")
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
        cursor.execute("DELETE FROM customer WHERE Customer_ID = %s", (customer_id,))
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
        cursor.execute("DELETE FROM company WHERE Company_ID = %s", (company_id,))
        conn.commit()
        flash("Company deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='company'))

@app.route('/delete_vehicle/<license_no>')
def delete_vehicle(license_no):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM vehicle WHERE License_no = %s", (license_no,))
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
        cursor.execute("DELETE FROM mechanic WHERE Mechanic_ID = %s", (mechanic_id,))
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
        cursor.execute("DELETE FROM service WHERE Service_ID = %s", (service_id,))
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
        cursor.execute("DELETE FROM spare_part WHERE Part_ID = %s", (part_id,))
        conn.commit()
        flash("Spare part deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='part'))

@app.route('/delete_maintenance/<maintenance_id>')
def delete_maintenance(maintenance_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM maintenance WHERE Maintenance_ID = %s", (maintenance_id,))
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
        cursor.execute("DELETE FROM warranty WHERE Warranty_ID = %s", (warranty_id,))
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
        cursor.execute("DELETE FROM fuel WHERE Fuel_ID = %s", (fuel_id,))
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
        cursor.execute("DELETE FROM availability WHERE Mechanic_ID = %s", (mechanic_id,))
        conn.commit()
        flash("Availability record deleted successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage', entity='availability'))

@app.route('/delete_vehicle_requirements/<license_no>')
def delete_vehicle_requirements(license_no):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM vehicle_requirements WHERE License_no = %s", (license_no,))
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
        cursor.execute("DELETE FROM service_requirements WHERE Service_ID = %s", (service_id,))
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
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query)
            if query.strip().lower().startswith("select"):
                result = cursor.fetchall()
                if result:
                    columns = result[0].keys()
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