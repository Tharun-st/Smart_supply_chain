"""
Intelligent Supply Chain Management System
Database Model & Connector Layer

Handles dual database connectivity:
  - Primary: MySQL 8.0 via mysql-connector-python
  - Fallback / Zero-Configuration: SQLite (supply_chain.db)

Automatically seeds realistic academic demo data (Suppliers, Warehouses, Products,
Inventory, Delivery Locations, Routes, Orders, and Algorithm Logs).
"""

import os
import sqlite3
import mysql.connector
from mysql.connector import Error as MySQLError
from config import Config
from typing import List, Dict, Any, Optional, Tuple
from werkzeug.security import generate_password_hash, check_password_hash

class Database:
    """Manages database connection and query execution."""
    _instance = None

    def __init__(self):
        self.engine = "sqlite"  # 'mysql' or 'sqlite'
        self.mysql_config = {
            "host": Config.MYSQL_HOST,
            "port": Config.MYSQL_PORT,
            "user": Config.MYSQL_USER,
            "password": Config.MYSQL_PASSWORD,
            "database": Config.MYSQL_DB,
            "autocommit": True
        }
        self.sqlite_path = Config.SQLITE_PATH
        os.makedirs(os.path.dirname(self.sqlite_path), exist_ok=True)
        self._test_and_initialize()

    def _test_and_initialize(self):
        """Attempts to connect to MySQL; if unavailable or unauthenticated, initializes SQLite."""
        try:
            # First try without database to check server auth & create database if needed
            test_conn = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                connect_timeout=3
            )
            cursor = test_conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.close()
            test_conn.close()

            # Now connect to specific database
            conn = mysql.connector.connect(**self.mysql_config)
            conn.close()
            self.engine = "mysql"
            print("[Database] Successfully connected to MySQL 8.0 server!")
            self._create_mysql_tables()
        except (MySQLError, Exception) as e:
            self.engine = "sqlite"
            print(f"[Database] MySQL not reachable ({e}). Activating embedded SQLite engine for zero-downtime demonstration.")
            self._create_sqlite_tables()

        self._seed_demo_data_if_empty()

    def get_connection(self):
        """Returns an active database connection."""
        if self.engine == "mysql":
            return mysql.connector.connect(**self.mysql_config)
        else:
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row
            return conn

    def execute_query(self, query: str, params: tuple = (), fetch: str = "all") -> Any:
        """
        Executes a SQL query with parameter binding.
        Adapts query syntax between MySQL and SQLite where appropriate.
        """
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True) if self.engine == "mysql" else conn.cursor()

        # Parameter placeholder translation (%s for MySQL, ? for SQLite)
        if self.engine == "sqlite":
            query = query.replace("%s", "?")
            # Replace MySQL specific syntax if any
            query = query.replace("ON DUPLICATE KEY UPDATE", "--")

        try:
            cursor.execute(query, params)
            if fetch == "all":
                if self.engine == "mysql":
                    result = cursor.fetchall()
                else:
                    rows = cursor.fetchall()
                    result = [dict(row) for row in rows]
                return result
            elif fetch == "one":
                if self.engine == "mysql":
                    row = cursor.fetchone()
                else:
                    r = cursor.fetchone()
                    row = dict(r) if r else None
                return row
            elif fetch == "insert":
                last_id = cursor.lastrowid
                if self.engine == "sqlite":
                    conn.commit()
                return last_id
            else:
                if self.engine == "sqlite":
                    conn.commit()
                return cursor.rowcount
        except Exception as err:
            print(f"[Database Error] Query: {query} | Params: {params} | Error: {err}")
            raise err
        finally:
            cursor.close()
            conn.close()

    def _create_sqlite_tables(self):
        """Creates tables in SQLite with full schema integrity."""
        conn = sqlite3.connect(self.sqlite_path)
        cur = conn.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'logistics_manager',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            contact_person TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            category TEXT,
            reliability_score REAL DEFAULT 95.0,
            avg_delivery_time_days REAL DEFAULT 3.0,
            status TEXT DEFAULT 'ACTIVE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS warehouses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            warehouse_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            city TEXT,
            capacity INTEGER NOT NULL DEFAULT 10000,
            lat REAL NOT NULL DEFAULT 0.0,
            lng REAL NOT NULL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            supplier_id INTEGER,
            price REAL NOT NULL DEFAULT 0.0,
            unit TEXT DEFAULT 'units',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers (id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            warehouse_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            reserved_quantity INTEGER NOT NULL DEFAULT 0,
            reorder_level INTEGER NOT NULL DEFAULT 50,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(product_id, warehouse_id),
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
            FOREIGN KEY (warehouse_id) REFERENCES warehouses (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS delivery_locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hub_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            pin_code TEXT,
            lat REAL NOT NULL DEFAULT 0.0,
            lng REAL NOT NULL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL,
            source_id INTEGER NOT NULL,
            destination_type TEXT NOT NULL,
            destination_id INTEGER NOT NULL,
            distance_km REAL NOT NULL,
            transit_time_hrs REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            customer_phone TEXT,
            customer_email TEXT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            priority INTEGER DEFAULT 2,
            delivery_location_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'PENDING_IN_QUEUE',
            assigned_warehouse_id INTEGER NULL,
            distance_km REAL NULL,
            estimated_cost REAL NULL,
            queue_position INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP NULL,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (delivery_location_id) REFERENCES delivery_locations (id),
            FOREIGN KEY (assigned_warehouse_id) REFERENCES warehouses (id)
        );

        CREATE TABLE IF NOT EXISTS algorithm_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            algorithm_name TEXT NOT NULL,
            data_structure_used TEXT NOT NULL,
            input_summary TEXT NOT NULL,
            output_summary TEXT NOT NULL,
            time_complexity TEXT,
            execution_steps_count INTEGER DEFAULT 1,
            execution_time_ms REAL DEFAULT 0.0,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        for col_stmt in [
            "ALTER TABLE suppliers ADD COLUMN reliability_score REAL DEFAULT 95.0",
            "ALTER TABLE suppliers ADD COLUMN avg_delivery_time_days REAL DEFAULT 3.0",
            "ALTER TABLE suppliers ADD COLUMN status TEXT DEFAULT 'ACTIVE'",
            "ALTER TABLE inventory ADD COLUMN reserved_quantity INTEGER DEFAULT 0",
            "ALTER TABLE orders ADD COLUMN priority INTEGER DEFAULT 2"
        ]:
            try:
                conn.execute(col_stmt)
            except Exception:
                pass
        conn.commit()
        conn.close()

    def _create_mysql_tables(self):
        """Creates tables in MySQL."""
        schema_path = os.path.join(os.path.dirname(__file__), "..", "database", "schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                sql_content = f.read()
            statements = sql_content.split(";")
            conn = self.get_connection()
            cursor = conn.cursor()
            for stmt in statements:
                stmt_clean = stmt.strip()
                if stmt_clean and not stmt_clean.lower().startswith("drop database") and not stmt_clean.lower().startswith("create database") and not stmt_clean.lower().startswith("use "):
                    try:
                        cursor.execute(stmt_clean)
                    except Exception as e:
                        pass
            cursor.close()
            conn.close()

    def _seed_demo_data_if_empty(self):
        """Populates realistic academic demo data if database is empty."""
        # Ensure users exist
        try:
            u_res = self.execute_query("SELECT COUNT(*) as cnt FROM users", fetch="one")
            if not u_res or u_res.get("cnt", 0) == 0:
                self.execute_query(
                    """INSERT INTO users (username, email, password_hash, full_name, role)
                       VALUES (%s, %s, %s, %s, %s)""",
                    ("admin", "admin@iscs.college.edu", generate_password_hash("admin123"), "Logistics Evaluator (Admin)", "admin"),
                    fetch="none"
                )
                self.execute_query(
                    """INSERT INTO users (username, email, password_hash, full_name, role)
                       VALUES (%s, %s, %s, %s, %s)""",
                    ("evaluator", "evaluator@university.edu", generate_password_hash("eval2026"), "Academic Evaluator", "student"),
                    fetch="none"
                )
        except Exception as ue:
            print(f"[Database] Error checking/seeding users: {ue}")

        count_res = self.execute_query("SELECT COUNT(*) as cnt FROM suppliers", fetch="one")
        cnt = count_res["cnt"] if count_res else 0
        if cnt > 0:
            return  # Already populated

        print("[Database] Seeding realistic sample supply chain data...")

        # 1. Seed Suppliers (8 Suppliers)
        suppliers_data = [
            ("SUP-01", "Global Microchips Ltd", "Arthur Hayes", "arthur@globalchips.io", "+91 98765 43210", "Tech Industrial Zone, Phase 1, Bengaluru", "Semiconductors", 98.5, 2.5),
            ("SUP-02", "Northern Steel & Alloys", "Vikram Rathore", "vikram@northernsteel.com", "+91 98111 22334", "Plot 44, Industrial Corridor, Jamshedpur", "Raw Metals", 94.0, 4.0),
            ("SUP-03", "EcoPackaging Solutions", "Ananya Sharma", "ananya@ecopack.co", "+91 97222 33445", "Green Park Logistics Park, Gurugram", "Packaging", 92.0, 3.2),
            ("SUP-04", "Precision Optics Works", "David Zhang", "david@precisionoptics.org", "+91 96333 44556", "Electronic City, Hosur Road, Bengaluru", "Optics & Sensors", 97.0, 2.8),
            ("SUP-05", "Summit Chemicals Corp", "Kavita Nair", "kavita@summitchem.com", "+91 95444 55667", "MIDC Industrial Estate, Navi Mumbai", "Industrial Chemicals", 89.5, 5.1),
            ("SUP-06", "Velocity Auto Components", "Rajesh Khanna", "rajesh@velocityparts.in", "+91 94555 66778", "Auto Hub, Chakan MIDC, Pune", "Automotive Parts", 96.0, 2.1),
            ("SUP-07", "Quantum Battery Systems", "Meera Sen", "meera@quantumbatt.com", "+91 93666 77889", "Hi-Tech Park, Gachibowli, Hyderabad", "Power Storage", 95.5, 3.0),
            ("SUP-08", "Apex Composite Polymers", "Siddharth Verma", "sid@apexpolymers.com", "+91 92777 88990", "GIDC Sector 28, Gandhinagar", "Polymers & Plastics", 91.0, 4.5)
        ]
        for s in suppliers_data:
            self.execute_query(
                "INSERT INTO suppliers (supplier_code, name, contact_person, email, phone, address, category, reliability_score, avg_delivery_time_days) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                s, fetch="none"
            )

        # 2. Seed Warehouses (5 Warehouses)
        warehouses_data = [
            ("WH-DEL", "North Regional Mega-Hub", "National Highway 48, Manesar", "Delhi NCR", 45000, 28.3537, 76.9405),
            ("WH-BOM", "West Coastal Logistics Center", "Bhiwandi Cargo Complex", "Mumbai", 50000, 19.2967, 73.0631),
            ("WH-BLR", "South Tech Fulfillment Center", "Peenya Industrial Hub", "Bengaluru", 40000, 13.0285, 77.5197),
            ("WH-CCU", "East Bengal Gateway Warehouse", "Dankuni Logistics Park", "Kolkata", 35000, 22.6844, 88.2917),
            ("WH-NAG", "Central Bharat Consolidation Node", "MIHAN SEZ Center", "Nagpur", 60000, 21.0560, 79.0322)
        ]
        for w in warehouses_data:
            self.execute_query(
                "INSERT INTO warehouses (warehouse_code, name, location, city, capacity, lat, lng) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                w, fetch="none"
            )

        # 3. Seed Products (15 Products)
        products_data = [
            ("PRD-101", "ARM Cortex Microcontroller MCU-X4", "Semiconductors", 1, 850.00, "units"),
            ("PRD-102", "High-Torque Stepper Motor NEMA-23", "Automotive Parts", 6, 2400.00, "units"),
            ("PRD-103", "Lithium Iron Phosphate Battery Pack 48V", "Power Storage", 7, 18500.00, "units"),
            ("PRD-104", "Industrial Grade Cold-Rolled Steel Sheet", "Raw Metals", 2, 4500.00, "rolls"),
            ("PRD-105", "Biodegradable Corrugated Shipping Box L", "Packaging", 3, 45.00, "boxes"),
            ("PRD-106", "Optical Infrared Proximity Sensor V2", "Optics & Sensors", 4, 620.00, "units"),
            ("PRD-107", "Thermally Conductive Epoxy Resin 5L", "Industrial Chemicals", 5, 3200.00, "cans"),
            ("PRD-108", "Reinforced Polycarbonate Resin Pellets", "Polymers & Plastics", 8, 180.00, "kg"),
            ("PRD-109", "Ceramic Dielectric Capacitor Tray (100x)", "Semiconductors", 1, 350.00, "trays"),
            ("PRD-110", "Solid State Drive Industrial 1TB NVMe", "Semiconductors", 1, 6800.00, "units"),
            ("PRD-111", "Fiber Optic Transceiver Module 10Gbps", "Optics & Sensors", 4, 1450.00, "units"),
            ("PRD-112", "Anti-Static Bubble Wrap Roll 100m", "Packaging", 3, 850.00, "rolls"),
            ("PRD-113", "Anodized Aluminum Framing Extrusion 2m", "Raw Metals", 2, 1100.00, "bars"),
            ("PRD-114", "Deep-Cycle Solar Inverter Unit 5kVA", "Power Storage", 7, 34000.00, "units"),
            ("PRD-115", "Silicone Thermal Paste Syringe (50g)", "Industrial Chemicals", 5, 290.00, "tubes")
        ]
        for p in products_data:
            self.execute_query(
                "INSERT INTO products (product_code, name, category, supplier_id, price, unit) VALUES (%s, %s, %s, %s, %s, %s)",
                p, fetch="none"
            )

        # 4. Seed Delivery Locations (10 Customer Hubs)
        locations_data = [
            ("HUB-PUN", "Pune Smart Logistics Terminal", "Pune", "Maharashtra", "411001", 18.5204, 73.8567),
            ("HUB-MAA", "Chennai Harbor Distribution Node", "Chennai", "Tamil Nadu", "600001", 13.0827, 80.2707),
            ("HUB-AMD", "Ahmedabad Cargo Express Hub", "Ahmedabad", "Gujarat", "380001", 23.0225, 72.5714),
            ("HUB-HYD", "Hyderabad Cyber Gateway Hub", "Hyderabad", "Telangana", "500001", 17.3850, 78.4867),
            ("HUB-JAI", "Jaipur Pink City Terminal", "Jaipur", "Rajasthan", "302001", 26.9124, 75.7873),
            ("HUB-IXC", "Chandigarh Northern Transit Hub", "Chandigarh", "Punjab", "160017", 30.7333, 76.7794),
            ("HUB-LKO", "Lucknow Awadh Freight Terminal", "Lucknow", "Uttar Pradesh", "226001", 26.8467, 80.9462),
            ("HUB-STV", "Surat Diamond Coast Depot", "Surat", "Gujarat", "395003", 21.1702, 72.8311),
            ("HUB-IDR", "Indore Malwa Logistics Facility", "Indore", "Madhya Pradesh", "452001", 22.7196, 75.8577),
            ("HUB-BBI", "Bhubaneswar Kalinga Depot", "Bhubaneswar", "Odisha", "751001", 20.2961, 85.8245)
        ]
        for l in locations_data:
            self.execute_query(
                "INSERT INTO delivery_locations (hub_code, name, city, state, pin_code, lat, lng) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                l, fetch="none"
            )

        # 5. Seed Inventory across Warehouses
        # Multiple warehouses stock each product with varying quantities for greedy algorithm demonstration
        inventory_data = [
            # Product 1 (ARM MCU)
            (1, 1, 450, 50),   # WH-DEL: 450
            (1, 2, 280, 50),   # WH-BOM: 280
            (1, 3, 620, 50),   # WH-BLR: 620
            (1, 5, 120, 50),   # WH-NAG: 120
            # Product 2 (Stepper Motor)
            (2, 2, 180, 30),   # WH-BOM: 180
            (2, 3, 240, 30),   # WH-BLR: 240
            (2, 5, 90, 30),    # WH-NAG: 90
            # Product 3 (LiFePO4 Battery)
            (3, 1, 65, 15),    # WH-DEL: 65
            (3, 3, 140, 20),   # WH-BLR: 140
            (3, 5, 80, 15),    # WH-NAG: 80
            # Product 4 (Steel Sheet)
            (4, 4, 300, 50),   # WH-CCU: 300
            (4, 5, 210, 40),   # WH-NAG: 210
            (4, 1, 110, 30),   # WH-DEL: 110
            # Product 5 (Corrugated Box)
            (5, 1, 2500, 500), # WH-DEL: 2500
            (5, 2, 1800, 400), # WH-BOM: 1800
            (5, 3, 3200, 500), # WH-BLR: 3200
            (5, 4, 1400, 300), # WH-CCU: 1400
            (5, 5, 4000, 600), # WH-NAG: 4000
            # Product 6 (Infrared Proximity Sensor)
            (6, 2, 320, 50),
            (6, 3, 580, 60),
            (6, 1, 210, 40),
            # Product 7 (Epoxy Resin)
            (7, 2, 150, 25),
            (7, 5, 95, 20),
            # Product 10 (SSD NVMe)
            (10, 1, 140, 20),
            (10, 3, 220, 30),
            (10, 2, 85, 15),
            # Product 14 (Solar Inverter)
            (14, 3, 45, 10),
            (14, 5, 30, 8),
            (14, 1, 25, 5)
        ]
        for inv in inventory_data:
            self.execute_query(
                "INSERT INTO inventory (product_id, warehouse_id, quantity, reorder_level) VALUES (%s, %s, %s, %s)",
                inv, fetch="none"
            )

        # 6. Seed Routes (Adjacency Graph Connections with realistic road distances in KM)
        routes_data = [
            # Inter-warehouse backbone
            ("warehouse", 1, "warehouse", 2, 1410.0, 24.0), # DEL - BOM
            ("warehouse", 1, "warehouse", 4, 1530.0, 26.0), # DEL - CCU
            ("warehouse", 1, "warehouse", 5, 1080.0, 18.0), # DEL - NAG
            ("warehouse", 2, "warehouse", 3, 980.0, 16.0),  # BOM - BLR
            ("warehouse", 2, "warehouse", 5, 820.0, 14.0),  # BOM - NAG
            ("warehouse", 3, "warehouse", 5, 1090.0, 18.0), # BLR - NAG
            ("warehouse", 4, "warehouse", 5, 970.0, 17.0),  # CCU - NAG
            # Warehouse to Customer Delivery Hubs
            ("warehouse", 2, "delivery_location", 1, 150.0, 3.5),   # BOM -> Pune (150 km)
            ("warehouse", 5, "delivery_location", 1, 710.0, 12.0),  # NAG -> Pune (710 km)
            ("warehouse", 3, "delivery_location", 2, 350.0, 6.0),   # BLR -> Chennai (350 km)
            ("warehouse", 2, "delivery_location", 3, 530.0, 9.0),   # BOM -> Ahmedabad (530 km)
            ("warehouse", 1, "delivery_location", 3, 940.0, 16.0),  # DEL -> Ahmedabad (940 km)
            ("warehouse", 3, "delivery_location", 4, 570.0, 9.5),   # BLR -> Hyderabad (570 km)
            ("warehouse", 5, "delivery_location", 4, 500.0, 8.5),   # NAG -> Hyderabad (500 km)
            ("warehouse", 1, "delivery_location", 5, 270.0, 4.5),   # DEL -> Jaipur (270 km)
            ("warehouse", 1, "delivery_location", 6, 250.0, 4.0),   # DEL -> Chandigarh (250 km)
            ("warehouse", 1, "delivery_location", 7, 550.0, 9.0),   # DEL -> Lucknow (550 km)
            ("warehouse", 2, "delivery_location", 8, 280.0, 5.0),   # BOM -> Surat (280 km)
            ("warehouse", 5, "delivery_location", 9, 440.0, 7.5),   # NAG -> Indore (440 km)
            ("warehouse", 2, "delivery_location", 9, 580.0, 10.0),  # BOM -> Indore (580 km)
            ("warehouse", 4, "delivery_location", 10, 440.0, 7.5),  # CCU -> Bhubaneswar (440 km)
            ("warehouse", 5, "delivery_location", 10, 830.0, 14.0)  # NAG -> Bhubaneswar (830 km)
        ]
        for r in routes_data:
            self.execute_query(
                "INSERT INTO routes (source_type, source_id, destination_type, destination_id, distance_km, transit_time_hrs) VALUES (%s, %s, %s, %s, %s, %s)",
                r, fetch="none"
            )

        # 7. Seed Initial Customer Orders (20 orders: 10 processed, 10 pending in FIFO Queue)
        orders_data = [
            # Processed Orders (10 orders)
            ("ORD-2026-001", "Tesla Energy India", "+91 99000 11111", "procure@tesla.in", 3, 20, 1, "DELIVERED", 3, 980.0, 17790.0, 0, 1),
            ("ORD-2026-002", "Tata Motors Chakan Plant", "+91 99000 22222", "supply@tatamotors.com", 2, 50, 1, "DELIVERED", 2, 150.0, 2850.0, 0, 1),
            ("ORD-2026-003", "Bharat Electronics Ltd", "+91 99000 33333", "orders@bel-india.in", 1, 100, 4, "DISPATCHED", 3, 570.0, 10410.0, 0, 2),
            ("ORD-2026-004", "Jaipur Robotics Academy", "+91 99000 44444", "lab@jaipurrobotics.edu", 6, 25, 5, "DISPATCHED", 1, 270.0, 5010.0, 0, 2),
            ("ORD-2026-005", "Chandigarh Aero Systems", "+91 99000 55555", "purchasing@chdaero.co", 10, 15, 6, "DISPATCHED", 1, 250.0, 4650.0, 0, 3),
            ("ORD-2026-006", "L&T Heavy Engineering", "+91 99000 66666", "procure@lnt.com", 4, 30, 8, "DELIVERED", 2, 280.0, 5190.0, 0, 1),
            ("ORD-2026-007", "Godrej Aerospace", "+91 99000 77777", "supply@godrej.com", 11, 40, 2, "DELIVERED", 3, 350.0, 6450.0, 0, 2),
            ("ORD-2026-008", "Infosys Campus Logistics", "+91 99000 88888", "campusops@infosys.com", 5, 200, 3, "DISPATCHED", 2, 530.0, 9690.0, 0, 3),
            ("ORD-2026-009", "Wipro Infrastructure", "+91 99000 99999", "admin@wipro.com", 7, 20, 9, "DISPATCHED", 5, 440.0, 8070.0, 0, 2),
            ("ORD-2026-010", "Reliance Jio Fiber Hub", "+91 98111 00000", "network@jio.com", 11, 60, 10, "DELIVERED", 4, 440.0, 8070.0, 0, 1),
            # Pending Orders currently in FIFO Queue (10 orders)
            ("ORD-2026-011", "Ather Mobility R&D", "+91 98888 12345", "supply@ather.com", 1, 80, 1, "PENDING_IN_QUEUE", None, None, None, 1, 1),
            ("ORD-2026-012", "Chennai Port Logistics Ltd", "+91 97777 23456", "ops@chennaiport.gov.in", 5, 500, 2, "PENDING_IN_QUEUE", None, None, None, 2, 3),
            ("ORD-2026-013", "Ahmedabad Automation Corp", "+91 96666 34567", "orders@ahmedabad-auto.in", 2, 35, 3, "PENDING_IN_QUEUE", None, None, None, 3, 2),
            ("ORD-2026-014", "Hyderabad Space Tech Hub", "+91 95555 45678", "procurement@spacetech.org", 6, 40, 4, "PENDING_IN_QUEUE", None, None, None, 4, 1),
            ("ORD-2026-015", "Indore MedTech Solutions", "+91 94444 56789", "medtech@indoresolutions.com", 7, 30, 9, "PENDING_IN_QUEUE", None, None, None, 5, 2),
            ("ORD-2026-016", "Mahindra Electric Vehicles", "+91 93333 67890", "evsupply@mahindra.com", 3, 15, 1, "PENDING_IN_QUEUE", None, None, None, 6, 1),
            ("ORD-2026-017", "Bhubaneswar Smart City Project", "+91 92222 78901", "iot@smartbbsr.gov.in", 6, 50, 10, "PENDING_IN_QUEUE", None, None, None, 7, 2),
            ("ORD-2026-018", "Surat Solar Microgrid", "+91 91111 89012", "solar@suratsolar.org", 14, 8, 8, "PENDING_IN_QUEUE", None, None, None, 8, 3),
            ("ORD-2026-019", "Lucknow Metro Rail Corp", "+91 90000 90123", "procure@lmrc.in", 4, 45, 7, "PENDING_IN_QUEUE", None, None, None, 9, 2),
            ("ORD-2026-020", "Punjab Agro Tech Logistics", "+91 98999 01234", "tech@punjabagro.gov.in", 10, 25, 6, "PENDING_IN_QUEUE", None, None, None, 10, 3)
        ]
        for o in orders_data:
            self.execute_query(
                """INSERT INTO orders 
                   (order_number, customer_name, customer_phone, customer_email, product_id, quantity, delivery_location_id, status, assigned_warehouse_id, distance_km, estimated_cost, queue_position, priority) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                o, fetch="none"
            )

        # 8. Seed Algorithm Logs
        logs_data = [
            ("Greedy Nearest Warehouse", "Array/List Candidates", "Order ORD-2026-002 for Stepper Motor (50 units) to Pune", "Selected WH-BOM (150 km, stock: 180) over WH-NAG (710 km)", "O(W)", 4, 1.25),
            ("Binary Search", "Sorted Integer Keys", "Search for Product ID 105 in 15 records", "Found at Index 4 after 3 comparisons (low: 0, mid: 7, high: 14 -> low: 0, mid: 3 -> mid: 4)", "O(log n)", 3, 0.42),
            ("Breadth-First Search", "Adjacency List Graph + FIFO Queue", "Network Traversal from WH-DEL", "Visited 15 locations across 3 levels (Level 0: WH-DEL, Level 1: BOM, CCU, NAG, Jaipur, Chandigarh, Lucknow)", "O(V + E)", 15, 2.10)
        ]
        for log in logs_data:
            self.execute_query(
                """INSERT INTO algorithm_logs 
                   (algorithm_name, data_structure_used, input_summary, output_summary, time_complexity, execution_steps_count, execution_time_ms) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                log, fetch="none"
            )

        # 9. Seed Default Users
        try:
            users_count = self.execute_query("SELECT COUNT(*) as cnt FROM users", fetch="one")
            if not users_count or users_count.get("cnt", 0) == 0:
                self.execute_query(
                    """INSERT INTO users (username, email, password_hash, full_name, role)
                       VALUES (%s, %s, %s, %s, %s)""",
                    ("admin", "admin@iscs.college.edu", generate_password_hash("admin123"), "Logistics Evaluator (Admin)", "admin"),
                    fetch="none"
                )
                self.execute_query(
                    """INSERT INTO users (username, email, password_hash, full_name, role)
                       VALUES (%s, %s, %s, %s, %s)""",
                    ("evaluator", "evaluator@university.edu", generate_password_hash("eval2026"), "Academic Evaluator", "student"),
                    fetch="none"
                )
        except Exception as e:
            print(f"[Database] Notice seeding users: {e}")

        print("[Database] Seed completed successfully with 8 suppliers, 5 warehouses, 15 products, 10 hubs, 10 orders, and users!")

    def authenticate_user(self, username_or_email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticates a user against hashed password in database."""
        try:
            user = self.execute_query(
                "SELECT * FROM users WHERE username = %s OR email = %s",
                (username_or_email, username_or_email),
                fetch="one"
            )
            if user and check_password_hash(user["password_hash"], password):
                return {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "full_name": user.get("full_name", user["username"]),
                    "role": user.get("role", "logistics_manager"),
                    "created_at": str(user.get("created_at", ""))
                }
        except Exception as err:
            print(f"[Database Auth Error] {err}")
        return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Fetches user details by user ID without exposing password hash."""
        try:
            user = self.execute_query("SELECT id, username, email, full_name, role, created_at FROM users WHERE id = %s", (user_id,), fetch="one")
            return user
        except Exception:
            return None

    def change_user_password(self, user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Validates old password and securely updates to new hashed password."""
        try:
            user = self.execute_query("SELECT * FROM users WHERE id = %s", (user_id,), fetch="one")
            if not user:
                return False, "User account not found."
            if not check_password_hash(user["password_hash"], old_password):
                return False, "Current password is incorrect."
            if len(new_password) < 6:
                return False, "New password must be at least 6 characters."

            new_hash = generate_password_hash(new_password)
            self.execute_query("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user_id), fetch="none")
            return True, "Password updated successfully!"
        except Exception as e:
            return False, f"Error updating password: {str(e)}"

    def reset_demo_data(self):
        """Clears all tables and reseeds standard demo records."""
        tables = [
            "algorithm_logs", "orders", "routes", "inventory", 
            "delivery_locations", "products", "warehouses", "suppliers", "users"
        ]
        for t in tables:
            try:
                self.execute_query(f"DELETE FROM {t}", fetch="none")
            except Exception as e:
                pass
        self._seed_demo_data_if_empty()
        return True

# Global singleton database instance
db = Database()


