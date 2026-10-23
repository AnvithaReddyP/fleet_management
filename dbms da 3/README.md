# FleetDB – Fleet Management Relational Database System

## Project Overview
FleetDB is a Python-based Fleet Management System developed as a comprehensive DBMS project. The system combines a modern, distributed CockroachDB (PostgreSQL wire-compatible) relational database with a responsive Flask web application to manage transport companies, commercial vehicles, mechanics, spare parts, and maintenance logs. 

The project demonstrates the complete database development lifecycle, from conceptual EER design and relational normalization to dynamic SQL execution, backend routing, and interactive frontend integration with Natural Language Processing (NLP) capabilities.

## Objectives
* Design and implement a highly normalized relational database for a logistics and fleet maintenance domain.
* Convert conceptual EER designs into normalized relational tables (1NF, 2NF, 3NF).
* Maintain strict data integrity using primary keys, foreign keys, and unique constraints.
* Implement complex SQL queries for data insertion, retrieval, updating, and deletion (CRUD).
* Develop a custom Natural Language-to-SQL conversion engine to make database querying accessible.
* Connect the Python web application to CockroachDB using `psycopg2`.
* Develop a clean, modal-driven, user-friendly HTML/CSS/JS frontend with dynamic dark/light theming.
* Provide real-time dashboard statistics and a live EER diagram visualizer.

## Technology Stack

| Component | Technology | Programming Language |
| :--- | :--- | :--- |
| **Frontend** | HTML5, embedded CSS3, JavaScript, Jinja2, Tailwind-inspired CSS | HTML/JS/CSS |
| **Backend Framework** | Flask 3.0.2 | Python 3.11 / 3.12 |
| **Database** | CockroachDB (Distributed SQL / Cloud & Local) | SQL (PostgreSQL compatible) |
| **Connectivity** | psycopg2-binary | Python |
| **Visualization** | Mermaid.js (EER), FontAwesome 6.5.1 | JavaScript |
| **Deployment** | Docker, Gunicorn 21.2.0, Render | - |

## Development Methodology
1. **Requirement Analysis:** The fleet management domain was analyzed to identify core entities and operations: Customer management, Company logistics, Vehicle tracking, Mechanic assignments, Service logging, Parts inventory, Warranty tracking, and Fuel management.
2. **EER and Relational Design:** Entities and relationships were mapped using an EER model. Primary keys were assigned, and associative (bridge) tables were designed to handle many-to-many relationships.
3. **Normalization:** The schema was strictly normalized to the 3rd Normal Form (3NF) to eliminate data anomalies. Multi-valued attributes and composite relationships were broken down.
4. **Database Implementation:** The normalized schema was implemented in CockroachDB. 12 core tables were created with precise data types and referential constraints.
5. **SQL & Backend Development:** Raw SQL queries were integrated into Python using `psycopg2`. Flask routes handle GET and POST requests for dynamic data rendering and mutations.
6. **Frontend Development:** A responsive UI was built using Jinja2. Operations were encapsulated in modal windows to prevent page reloads, and custom JS search filters were implemented.
7. **Advanced Features Integration:** Embedded a live Mermaid.js EER diagram and built a custom Natural Language-to-SQL parser in JavaScript for plain-English database querying.
8. **Containerization & Testing:** Packaged into a lightweight Docker container optimized for CockroachDB connectivity.

## Database Design
The final database contains 12 relational tables covering major fleet entities:

### Core Entities
* **Company:** Register B2B transport companies, track multi-state locations, and anchor vehicles to corporate clients.
* **Customer:** Store personal contact details and link specific service requests/invoices directly to authorizing individuals.
* **Vehicles:** Register fleet assets with unique license plates (Primary Key), track manufacturing dates, and reassign ownership.
* **Mechanic:** Onboard service personnel, categorize by skill level, query rosters, and track active assignments.

### Operational Entities
* **Service:** Standardized catalog of repair operations, tracking base costs, and linking tickets to customers.
* **Spare_parts:** Monitor real-time stock levels, run low-stock threshold queries (`qty < 5`), and map parts to required services.
* **Maintenance:** Immutable historical records of maintenance events, text descriptions of work, and audit trails.
* **Warranty:** Log expiration dates and coverage types, query expiring warranties (30/60/90 days), and prevent out-of-pocket billing.
* **Fuel:** Track fuel types (Diesel, Petrol, EV), monitor prices/quantities, and analyze operational costs per vehicle.

### Associative (Bridge) Entities
* **Availability:** Track which mechanic currently holds specific spare parts to determine if repairs can proceed.
* **Vehicle_requirements:** Resolve many-to-many relationships between vehicles, required services, and fuel types.
* **Service_requirements:** Master dispatch table linking scheduled services to assigned mechanics and reserved spare parts.

## Backend Architecture
The backend operates on a streamlined MVC-inspired architecture:
`Web Browser` → `Flask Routes (app.py)` → `DB Connection Manager` → `psycopg2-binary` → `CockroachDB Cluster`

* **Custom NLP Parser:** Translates inputs like *"show low stock parts"* into `SELECT spare_part_id, name, qty FROM spare_parts WHERE qty < 5;`.
* **Foreign Key Auto-Population:** Dynamically queries tables to populate UI dropdowns, ensuring referential integrity before INSERT statements are constructed.
* **Live Schema Mapping:** The `/eer` endpoint generates a live Mermaid.js diagram mapped to current SQL constraints.

## Frontend Architecture
* **Layout:** Persistent sidebar navigation with a responsive main content area.
* **Modals:** CRUD operations utilize dynamic overlay modals injected with context-specific data.
* **Client-Side Filtering:** JavaScript filters table rows instantly without requiring a database `SELECT` query.
* **Theming:** Dark/light mode toggle saves user preference to `localStorage`.

## Dashboard & CRUD Workflow
The main dashboard provides real-time telemetry (active vehicles, B2B customers, on-duty mechanics, connection status) via aggregate SQL functions (`SELECT COUNT(*)`). 

**Typical CRUD Flow:**
User clicks "Edit Vehicle" → JS populates modal → User submits form → Flask route intercepts POST → Parameterized SQL `UPDATE` formulated → `psycopg2` executes safely → Flash message generated → Page reloads.

## Validation and Data Integrity
* **Application Level:** HTML5 required attributes and dropdowns ensure users can only submit valid formatted data and existing Foreign Keys.
* **Backend Level:** `try/except` blocks in Python catch database anomalies and gracefully flash errors to the UI instead of crashing the server.
* **Database Level:** CockroachDB enforces PRIMARY KEY uniqueness, FOREIGN KEY referential constraints, and strict data typing (e.g., DECIMAL(10,2) for costs).

## Project Structure
```text
FleetDB/
├── app.py               # Main Flask application and route definitions
├── schema.sql           # Raw SQL queries for 3NF table creation and testing
├── requirements.txt     # Python package dependencies
├── .env                 # Database connection credentials
├── Dockerfile           # Containerization setup instructions
├── Procfile             # Gunicorn deployment configuration
└── templates/
    ├── dashboard.html   # Main interface, metrics, and all CRUD modals
    ├── eer.html         # Mermaid.js schema visualizer
    └── query.html       # Interactive SQL editor and NLP module
