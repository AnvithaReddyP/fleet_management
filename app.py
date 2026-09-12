from flask import Flask, render_template, request, redirect, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "fleet_secret_key_123"

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),  # Automatically pulls the hidden password
        database="FleetManagement"
    )

@app.route('/')
def dashboard():
    return render_template('dashboard.html', entity=None)

@app.route('/manage/<entity>')
def manage(entity):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    data = []
    
    try:
        queries = {
            'customer': "SELECT * FROM Customer",
            'company': "SELECT * FROM Company",
            'vehicle': "SELECT * FROM Vehicles",
            'mechanic': "SELECT * FROM Mechanic",
            'service': "SELECT * FROM Service",
            'part': "SELECT * FROM Spare_Part",
            'maintenance': "SELECT * FROM Maintenance",
            'warranty': "SELECT * FROM Vehicle_Warranty",
            'fuel': "SELECT * FROM Fuel"
        }
        if entity in queries:
            cursor.execute(queries[entity])
            data = cursor.fetchall()
    except mysql.connector.Error as e:
        flash(f"Database Error: {e}", "error")
    finally:
        conn.close()
        
    return render_template('dashboard.html', entity=entity, data=data)

# --- EXISTING ROUTES (Customer, Company, Vehicle, Mechanic, Service, Part) ---
@app.route('/add_customer', methods=['POST'])
def add_customer():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Customer (Customer_ID, First_Name, Last_Name, Ph_no) VALUES (%s, %s, %s, %s)", 
                       (request.form['customer_id'], request.form['first_name'], request.form['last_name'], request.form['phone']))
        conn.commit()
    except mysql.connector.Error as e: flash(f"Customer Error: {e}", "error")
    finally: conn.close()
    return redirect('/manage/customer')

@app.route('/delete_customer/<int:id>')
def delete_customer(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Customer WHERE Customer_ID = %s", (id,))
    conn.commit()
    conn.close()
    return redirect('/manage/customer')

@app.route('/add_company', methods=['POST'])
def add_company():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Company (Company_ID, Location, Area, City, State) VALUES (%s, %s, %s, %s, %s)", 
                       (request.form['company_id'], request.form['location'], request.form['area'], request.form['city'], request.form['state']))
        conn.commit()
    except mysql.connector.Error as e: flash(f"Company Error: {e}", "error")
    finally: conn.close()
    return redirect('/manage/company')

@app.route('/delete_company/<int:id>')
def delete_company(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Company WHERE Company_ID = %s", (id,))
    conn.commit()
    conn.close()
    return redirect('/manage/company')

@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Vehicles (License_no, Model, Mfd_Date, Company_ID) VALUES (%s, %s, %s, %s)", 
                       (request.form['license_no'], request.form['model'], request.form['mfd_date'], request.form['company_id']))
        conn.commit()
    except mysql.connector.Error as e: flash(f"Vehicle Error: {e}", "error")
    finally: conn.close()
    return redirect('/manage/vehicle')

@app.route('/delete_vehicle/<string:id>')
def delete_vehicle(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Vehicles WHERE License_no = %s", (id,))
    conn.commit()
    conn.close()
    return redirect('/manage/vehicle')

@app.route('/add_mechanic', methods=['POST'])
def add_mechanic():
    conn = get_db_connection()
    cursor = conn.cursor()
    availability = 1 if request.form.get('availability') == 'on' else 0
    try:
        cursor.execute("INSERT INTO Mechanic (Mechanic_ID, Mechanic_name, Skill_level, Availability) VALUES (%s, %s, %s, %s)", 
                       (request.form['mechanic_id'], request.form['mechanic_name'], request.form['skill_level'], availability))
        conn.commit()
    except mysql.connector.Error as e: flash(f"Mechanic Error: {e}", "error")
    finally: conn.close()
    return redirect('/manage/mechanic')

@app.route('/delete_mechanic/<int:id>')
def delete_mechanic(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Mechanic WHERE Mechanic_ID = %s", (id,))
    conn.commit()
    conn.close()
    return redirect('/manage/mechanic')

@app.route('/add_service', methods=['POST'])
def add_service():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Service (Service_ID, Cost, Category, License_no) VALUES (%s, %s, %s, %s)", 
                       (request.form['service_id'], request.form['cost'], request.form['category'], request.form['license_no']))
        conn.commit()
    except mysql.connector.Error as e: flash(f"Service Error: {e}", "error")
    finally: conn.close()
    return redirect('/manage/service')

@app.route('/delete_service/<int:id>')
def delete_service(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Service WHERE Service_ID = %s", (id,))
    conn.commit()
    conn.close()
    return redirect('/manage/service')

@app.route('/add_part', methods=['POST'])
def add_part():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Spare_Part (Part_ID, Name, Quantity) VALUES (%s, %s, %s)", 
                       (request.form['part_id'], request.form['name'], request.form['quantity']))
        conn.commit()
    except mysql.connector.Error as e: flash(f"Spare Part Error: {e}", "error")
    finally: conn.close()
    return redirect('/manage/part')

@app.route('/delete_part/<int:id>')
def delete_part(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Spare_Part WHERE Part_ID = %s", (id,))
    conn.commit()
    conn.close()
    return redirect('/manage/part')

# --- NEW ROUTES: MAINTENANCE, WARRANTY, FUEL ---
@app.route('/add_maintenance', methods=['POST'])
def add_maintenance():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Maintenance (Maintenance_ID, Description, Maintenance_logo, Company_ID) VALUES (%s, %s, %s, %s)", 
                       (request.form['maintenance_id'], request.form['description'], request.form['logo'], request.form['company_id']))
        conn.commit()
    except mysql.connector.Error as e: flash(f"Maintenance Error: {e}", "error")
    finally: conn.close()
    return redirect('/manage/maintenance')

@app.route('/delete_maintenance/<int:id>')
def delete_maintenance(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Maintenance WHERE Maintenance_ID = %s", (id,))
    conn.commit()
    conn.close()
    return redirect('/manage/maintenance')

@app.route('/add_warranty', methods=['POST'])
def add_warranty():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Vehicle_Warranty (Warranty_ID, Type, Expiration_date, License_no) VALUES (%s, %s, %s, %s)", 
                       (request.form['warranty_id'], request.form['type'], request.form['exp_date'], request.form['license_no']))
        conn.commit()
    except mysql.connector.Error as e: flash(f"Warranty Error: {e}", "error")
    finally: conn.close()
    return redirect('/manage/warranty')

@app.route('/delete_warranty/<int:id>')
def delete_warranty(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Vehicle_Warranty WHERE Warranty_ID = %s", (id,))
    conn.commit()
    conn.close()
    return redirect('/manage/warranty')

@app.route('/add_fuel', methods=['POST'])
def add_fuel():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Fuel (Fuel_ID, Type, Price, Total_price, License_no) VALUES (%s, %s, %s, %s, %s)", 
                       (request.form['fuel_id'], request.form['type'], request.form['price'], request.form['total_price'], request.form['license_no']))
        conn.commit()
    except mysql.connector.Error as e: flash(f"Fuel Error: {e}", "error")
    finally: conn.close()
    return redirect('/manage/fuel')

@app.route('/delete_fuel/<int:id>')
def delete_fuel(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Fuel WHERE Fuel_ID = %s", (id,))
    conn.commit()
    conn.close()
    return redirect('/manage/fuel')

# --- QUERY WINDOW ---
@app.route('/query_window', methods=['GET', 'POST'])
def query_window():
    results, error = None, None
    if request.method == 'POST':
        query = request.form['sql_query']
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
            else:
                conn.commit()
                results = [{"Message": "Query executed successfully."}]
            conn.close()
        except Exception as e:
            error = str(e)
    return render_template('query_window.html', results=results, error=error)

if __name__ == '__main__':
    app.run(debug=True)