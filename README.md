FleetDB - Fleet Management Relational Database System

Deployed Link

https://fleet-management-2.onrender.com/


Team Members

1.	Dhyanam Amit Shah – 25BCE1085
2.	P. Anvitha Reddy – 25BCE1090
3.	A. Nikhitha – 25BCE1095


Project Overview

FleetDB is a Python-based Fleet Management System developed as a comprehensive DBMS project. The system combines a MySQL relational database with a modern, responsive Flask web application to manage transport companies, commercial vehicles, mechanics, spare parts, and maintenance logs.
The project demonstrates the complete database development lifecycle, from conceptual EER design and relational normalization to dynamic SQL execution, backend routing, and interactive frontend integration with Natural Language Processing (NLP) capabilities.


Objectives

The main objectives of the project are:
•	Design and implement a highly normalized relational database for a logistics and fleet maintenance domain.
•	Convert conceptual EER designs into normalized relational tables (1NF, 2NF, 3NF).
•	Maintain strict data integrity using primary keys, foreign keys, and unique constraints.
•	Implement complex SQL queries for data insertion, retrieval, updating, and deletion (CRUD).
•	Develop a custom Natural Language-to-SQL conversion engine to make database querying accessible.
•	Connect the Python web application to the database using PyODBC.
•	Develop a clean, modal-driven, user-friendly HTML/CSS/JS frontend with dynamic dark/light theming.
•	Provide real-time dashboard statistics and a live EER diagram visualizer.


Technology Stack

Component	Technology
Programming Language	Python 3.11
Frontend	HTML5 with embedded CSS3, JavaScript, Jinja2, Tailwind-inspired CSS
Backend Framework	Flask 3.0.2
Database	MariaDB / MySQL
Database Programming	SQL
Connectivity	PyODBC 5.1.0, unixodbc
Visualization	Mermaid.js (EER), FontAwesome 6.5.1
Deployment	Docker, Gunicorn 21.2.0, render


Development Methodology

The project was developed in the following stages:
Step 1 : Requirement Analysis
The fleet management domain was analyzed to identify core entities and operations. Key functional areas included: Customer management, Company logistics, Vehicle tracking, Mechanic assignments, Service logging, Parts inventory, Warranty tracking, and Fuel management.

Step 2 : EER and Relational Design
Entities and relationships were mapped using an EER model. Primary keys were assigned for unique identification, and associative (bridge) tables were designed to handle many-to-many relationships (e.g., mechanics to spare parts).

Step 3 : Normalization
The schema was strictly normalized to the 3rd Normal Form (3NF) to eliminate data anomalies. Multi-valued attributes and composite relationships were broken down into dedicated relation tables.

Step 4 : Database Implementation
The normalized schema was implemented in MariaDB/MySQL. 12 core tables were created with precise data types and referential constraints.

Step 5 : SQL & Backend Development
Raw SQL queries were integrated into Python using pyodbc. The backend was structured using Flask routes to handle GET and POST requests for dynamic data rendering and mutations.

Step 6 : Frontend Development
A responsive UI was built using Jinja2 templates. Operations were encapsulated in modal windows to prevent page reloads, and a custom JavaScript search filter was implemented for all data tables.

Step 7 : Advanced Features Integration
A live Mermaid.js EER diagram was embedded, and a custom Natural Language-to-SQL parser was written in JavaScript to allow users to query the database using plain English.

Step 8 : Containerization & Testing
The application was packaged into a Docker container with OS-level ODBC drivers to guarantee environment consistency.


Database Design

The final database contains 12 relational tables covering the major fleet entities and relationships.
Core Entities

•	Company (Client Organizations)
o	Register new B2B transport companies and logistics clients.
o	Track multi-state locations by storing specific branch areas and cities.
o	Act as the primary anchor to query all vehicles owned by a specific corporate client.
•	Customer (Individual Contacts)
o	Store personal contact details (first name, last name, phone number) for individual clients or company representatives.
o	Link specific service requests and invoices directly to the authorizing individual.
•	Vehicles (Fleet Assets)
o	Register new trucks or cars into the system with their unique license plate numbers as the primary key.
o	Track the age of the fleet by monitoring manufacturing dates.
o	Reassign vehicles to different corporate clients (company_id) if ownership changes.
•	Mechanic (Service Staff)
o	Onboard new service personnel and categorize them by their specific skill levels.
o	Query staff rosters to find qualified personnel for specific mechanical issues.
o	Track which services each mechanic is actively assigned to.

Operational Entities

•	Service (Categories & Costs)
o	Build a standardized catalog of available repair and maintenance operations (e.g., transmission rebuild, oil change).
o	Track and update the base financial cost for each service category.
o	Link specific service tickets back to the requesting customer.
•	Spare_parts (Inventory Control)
o	Monitor real-time stock levels of physical components.
o	Run low-stock threshold queries (e.g., identifying parts where quantity is less than 5) to trigger reordering.
o	Map specific parts to the exact services that require them.
•	Maintenance (Historical Logs)
o	Create immutable historical records of all maintenance events performed for a company.
o	Store detailed text descriptions of the work completed and the exact date it occurred.
o	Generate audit trails to see how often a company requires fleet repairs.
•	Warranty (Coverage Tracking)
o	Log expiration dates and coverage types for newly purchased vehicles.
o	Query the database to identify which vehicles have warranties expiring in the next 30, 60, or 90 days.
o	Prevent out-of-pocket billing for services covered under an active warranty linked to a license number.

•	Fuel (Consumption & Pricing)
o	Track different fuel types (e.g., Diesel, Petrol, EV charging) used across the fleet.
o	Monitor fluctuating fuel prices and total quantities consumed.
o	Analyze operational costs by linking fuel usage back to specific vehicles.

Associative (Bridge) Entities

•	Availability (Mechanic & Part Mapping)
o	Track exactly which mechanic currently holds or has access to specific spare parts.
o	Determine if a repair can proceed by cross-referencing a mechanic's schedule with the physical availability of the required part.
•	Vehicle_requirements (Vehicle Needs)
o	Resolve the many-to-many relationship between vehicles, their required services, and their required fuel.
o	Identify exactly what type of fuel a specific truck needs before dispatching it.
o	Log ongoing or pending service requirements for a specific license plate.
•	Service_requirements (Service Execution)
o	Act as the master dispatch table for a repair job.
o	Link a scheduled service to the exact mechanic assigned to perform it.
o	Reserve the specific spare parts needed from inventory for that exact service ticket.


SQL Implementation

Standard SQL is used extensively throughout the backend for:
•	Data retrieval (SELECT with JOIN operations for the NLP query engine).
•	Data insertion (INSERT INTO parameterized queries to prevent SQL injection).
•	Data updates (UPDATE ... SET for editing records).
•	Data deletion (DELETE FROM with cascading considerations).
•	Aggregate calculations (COUNT, AVG for dashboard metrics).
•	Schema introspection (SHOW TABLES, DESCRIBE for the query window).

Custom Logic & Integrations

Rather than relying purely on database-side PL/SQL, FleetDB utilizes application-side processing for advanced features:
•	Natural Language to SQL Parser: A custom module that interprets user inputs like "show low stock parts" and translates them into SELECT spare_part_id, name, qty FROM spare_parts WHERE qty < 5;.
•	Foreign Key Auto-Population: When adding a new Vehicle, the backend dynamically queries the company table to populate the UI dropdown, ensuring referential integrity before the INSERT statement is even constructed.
•	Live Schema Mapping: The /eer endpoint generates a live Mermaid.js diagram that perfectly maps to the current constraints of the SQL database.


Backend Architecture

The backend operates on a streamlined MVC-inspired architecture:
Web Browser (Jinja2 / JS)    Flask Route Controllers (app.py)    DB Connection Manager (get_db_connection)    PyODBC Driver / unixodbc    MariaDB / MySQL Database

•	Controllers: Flask routes (/add_customer, /edit_vehicle, etc.) handle request parsing, SQL execution, and flash messaging.
•	Connection Management: .env variables securely configure the ODBC connection string.

To secure PyODBC connection using environment variables:

connection_string = (
    f"Driver={{MariaDB Unicode}};"
    f"Server={os.getenv('DB_SERVER')};"
    f"Port={os.getenv('DB_PORT')};"
    f"Database={os.getenv('DB_NAME')};"
    f"User={os.getenv('DB_USER')};"
    f"Password={os.getenv('DB_PASSWORD')};"
)
conn = pyodbc.connect(connection_string)


Frontend Architecture

The frontend is implemented using HTML5 and Jinja2 templates, styled with custom CSS variables to support dynamic themes.
•	Layout: A persistent sidebar navigation with a responsive main content area.
•	Modals: Instead of separate pages, CRUD operations utilize dynamic overlay modals (addModal, editModal) injected with context-specific data.
•	Client-Side Filtering: JavaScript functions filter table rows instantly without requiring a database SELECT query for basic searches.
•	Theming: A dark/light mode toggle saves user preference to localStorage.


Functional Modules

•	Customer & Company Management: View, add, update, and delete business entities.
•	Vehicle & Fleet Management: Track vehicles, view manufacturing dates, and assign them to corporate entities.
•	Service & Mechanic Management: Register mechanics, define skill levels, and map them to service categories.
•	Inventory Tracking (Spare Parts & Fuel): Monitor stock quantities and fuel pricing.
•	Logs & Records (Maintenance & Warranty): Track historical maintenance events and monitor active warranties based on vehicle license numbers.
•	Requirements Mapping: Manage the complex many-to-many relationships defining what vehicles need which services.


Dashboard

The main dashboard provides a summarized telemetry view of the fleet system. It retrieves and displays:
•	Total active vehicles.
•	Total registered B2B customers.
•	On-duty mechanics.
•	Database cluster connection status.
These metrics are dynamically queried via aggregate SQL functions (SELECT COUNT(*)) upon page load to ensure real-time accuracy.


SQL Query Module

The application includes an interactive, browser-based IDE for SQL execution.
The workflow is:
User enters Natural Language or Raw SQL    Flask /query_window endpoint    PyODBC Cursor Execution    Dynamic Column Extraction (cursor.description)    Jinja2 Table Rendering

This module allows administrators to run complex JOIN or GROUP BY queries that fall outside standard CRUD operations.


CRUD Workflow

A typical Database update follows this secure flow:
User clicks "Edit Vehicle"
     ↓
JavaScript populates modal with row data
     ↓
User submits form
     ↓
Flask route (/edit_vehicle) intercepts POST data
     ↓
Parameterized SQL UPDATE is formulated
     ↓
PyODBC executes query safely
     ↓
Flash message generated (Success/Error)
     ↓
Page reloads with updated Database view




Validation and Data Integrity

•	Application Level: HTML5 required attributes and <select> dropdowns ensure users can only submit valid formatted data and existing Foreign Keys.

•	Backend Level: try/except blocks in Python catch database anomalies and gracefully flash errors to the UI instead of crashing the server.

•	Database Level: MariaDB enforces PRIMARY KEY uniqueness, FOREIGN KEY referential constraints, and strict data typing (e.g., DECIMAL(10,2) for costs).


Project Structure


FleetDB/
│
├── app.py                  # Main Flask application and route definitions
├── schema.sql              # Raw SQL queries for 3NF table creation and testing
├── requirements.txt        # Python package dependencies
├── .env                    # Database connection credentials
├── Dockerfile              # Containerization and ODBC setup instructions
├── Procfile                # Gunicorn deployment configuration
│
└── templates/
    ├── dashboard.html      # Main interface, metrics, and all CRUD modals
    ├── eer.html            # Mermaid.js schema visualizer
    └── query.html          # Interactive SQL editor and NLP module16. Installation and Setup

Prerequisites

•	Python 3.11+

•	MariaDB or MySQL Server

•	ODBC Drivers (unixodbc, odbc-mariadb)



Database Setup

1.	Start your database server.
2.	Create a database named fleetdb.
3.	Configure your local .env file:

Code snippet:
SECRET_KEY=super_secret_key
DB_SERVER=localhost
DB_PORT=3306
DB_NAME=fleetdb
DB_USER=root
DB_PASSWORD=your_password


Running the Application

Cloud Deployment (Render & Docker) The application is deployed live as a fully containerized continuous web service.
•	Web Host: Render (Docker Web Service)
•	Database Host: Aiven (Managed MySQL Cluster)
•	Deployment Workflow: Pushing commits to the GitHub repository automatically triggers Render to build a new Docker container.
•	Driver Configuration: The production environment utilizes the odbc-mariadb Debian package and MariaDB Unicode driver to maintain a highly stable, Linux-native PyODBC connection to the remote Aiven database cluster.


Testing

The system was tested across multiple vectors:
•	Database Testing: Direct SQL insertions to verify constraint rejections and cascading behaviors.
•	Backend Testing: Form submission handling, parameterized query safety, and pyodbc exception catching.
•	Frontend Testing: Modal state management, dark mode persistence, dynamic dropdown population, and responsive mobile layouts.
•	NLP Testing: Ensuring plain English text successfully parsed into valid SQL queries mapped to the exact schema aliases.


Contribution

•	Database Design: Conceptual modeling, normalization to 3NF, schema creation.
•	Backend Development: Flask routing, PyODBC integration, exception handling.
•	Frontend Development: CSS variable theming, Jinja2 templating, JavaScript modal logic, Mermaid.js integration.
•	Advanced Features: Development of the Natural Language SQL parser and the interactive query environment.


Conclusion

FleetDB successfully demonstrates the creation of a modern, full-stack database application.
The project thoroughly covers the DBMS lifecycle:
Domain Analysis
       ↓
Relational Modeling & Normalization
       ↓
Database Initialization (MariaDB)
       ↓
Backend Application Logic (Python/Flask)
       ↓
Database Connectivity (PyODBC)
       ↓
Frontend UI Implementation (HTML/JS)
       ↓
Advanced Querying & NLP
       ↓
Containerized Deployment

The final system provides an elegant, highly structured environment to manage complex logistical data, proving the efficacy of normalized relational databases paired with dynamic web frameworks.

