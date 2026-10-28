-- ====================================================================
-- INTELLIGENT SUPPLY CHAIN OPTIMIZATION SYSTEM
-- Academic Data Structures and Algorithms Project
-- MySQL Database DDL & Realistic Demonstration Seed Data
-- ====================================================================

DROP DATABASE IF EXISTS `intelligent_supply_chain`;
CREATE DATABASE IF NOT EXISTS `intelligent_supply_chain` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `intelligent_supply_chain`;

-- 1. Users Table (Role-based access)
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `email` VARCHAR(100) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `full_name` VARCHAR(100),
    `role` ENUM('admin', 'logistics_manager', 'operator', 'student') DEFAULT 'logistics_manager',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Suppliers Table (Linked List Demonstration)
CREATE TABLE IF NOT EXISTS `suppliers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `supplier_code` VARCHAR(20) UNIQUE NOT NULL,
    `name` VARCHAR(150) NOT NULL,
    `contact_person` VARCHAR(100),
    `email` VARCHAR(100),
    `phone` VARCHAR(30),
    `address` TEXT,
    `category` VARCHAR(50),
    `reliability_score` DECIMAL(4, 2) DEFAULT 95.50,
    `avg_delivery_time_days` DECIMAL(4, 1) DEFAULT 3.5,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Warehouses Table (Graph Vertices & Capacity Allocation)
CREATE TABLE IF NOT EXISTS `warehouses` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `warehouse_code` VARCHAR(20) UNIQUE NOT NULL,
    `name` VARCHAR(150) NOT NULL,
    `location` VARCHAR(100) NOT NULL,
    `city` VARCHAR(80),
    `capacity` INT NOT NULL DEFAULT 40000,
    `lat` DECIMAL(10, 6) NOT NULL DEFAULT 0.000000,
    `lng` DECIMAL(10, 6) NOT NULL DEFAULT 0.000000,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Products Table (Linked List, Searching & Sorting Labs)
CREATE TABLE IF NOT EXISTS `products` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `product_code` VARCHAR(20) UNIQUE NOT NULL,
    `name` VARCHAR(150) NOT NULL,
    `category` VARCHAR(80) NOT NULL,
    `supplier_id` INT,
    `price` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    `unit` VARCHAR(20) DEFAULT 'units',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_prod_supp` FOREIGN KEY (`supplier_id`) 
        REFERENCES `suppliers` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Inventory Table (Binary Search Tree & Dynamic Programming)
CREATE TABLE IF NOT EXISTS `inventory` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `product_id` INT NOT NULL,
    `warehouse_id` INT NOT NULL,
    `quantity` INT NOT NULL DEFAULT 0,
    `reserved_quantity` INT NOT NULL DEFAULT 0,
    `reorder_level` INT NOT NULL DEFAULT 50,
    `last_updated` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_prod_wh` (`product_id`, `warehouse_id`),
    CONSTRAINT `fk_inv_prod` FOREIGN KEY (`product_id`) 
        REFERENCES `products` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_inv_wh` FOREIGN KEY (`warehouse_id`) 
        REFERENCES `warehouses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Delivery Locations (Graph Vertices & Customer Hubs)
CREATE TABLE IF NOT EXISTS `delivery_locations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `hub_code` VARCHAR(20) UNIQUE NOT NULL,
    `name` VARCHAR(150) NOT NULL,
    `city` VARCHAR(80) NOT NULL,
    `state` VARCHAR(80) NOT NULL,
    `pin_code` VARCHAR(15),
    `lat` DECIMAL(10, 6) NOT NULL DEFAULT 0.000000,
    `lng` DECIMAL(10, 6) NOT NULL DEFAULT 0.000000,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. Routes Table (Graph Edges with Weighted Distances)
CREATE TABLE IF NOT EXISTS `routes` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `source_type` ENUM('warehouse', 'supplier', 'delivery_location') NOT NULL,
    `source_id` INT NOT NULL,
    `destination_type` ENUM('warehouse', 'supplier', 'delivery_location') NOT NULL,
    `destination_id` INT NOT NULL,
    `distance_km` DECIMAL(8, 2) NOT NULL,
    `transit_time_hrs` DECIMAL(6, 2) DEFAULT 0.00,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Orders Table (FIFO Queue for Pending & LIFO Stack for Processed)
CREATE TABLE IF NOT EXISTS `orders` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `order_number` VARCHAR(30) UNIQUE NOT NULL,
    `customer_name` VARCHAR(150) NOT NULL,
    `customer_phone` VARCHAR(30),
    `customer_email` VARCHAR(100),
    `product_id` INT NOT NULL,
    `quantity` INT NOT NULL,
    `priority` INT DEFAULT 1,
    `delivery_location_id` INT NOT NULL,
    `status` ENUM('PENDING_IN_QUEUE', 'PROCESSING', 'DISPATCHED', 'DELIVERED', 'CANCELLED') NOT NULL DEFAULT 'PENDING_IN_QUEUE',
    `assigned_warehouse_id` INT NULL,
    `distance_km` DECIMAL(8, 2) NULL,
    `estimated_cost` DECIMAL(10, 2) NULL,
    `queue_position` INT DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `processed_at` TIMESTAMP NULL,
    CONSTRAINT `fk_ord_prod` FOREIGN KEY (`product_id`) 
        REFERENCES `products` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `fk_ord_loc` FOREIGN KEY (`delivery_location_id`) 
        REFERENCES `delivery_locations` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `fk_ord_wh` FOREIGN KEY (`assigned_warehouse_id`) 
        REFERENCES `warehouses` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. Algorithm Execution History (Activity Log & Academic Audit)
CREATE TABLE IF NOT EXISTS `algorithm_execution_history` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `algorithm_name` VARCHAR(80) NOT NULL,
    `data_structure_used` VARCHAR(80) NOT NULL,
    `input_summary` TEXT NOT NULL,
    `output_summary` TEXT NOT NULL,
    `time_complexity` VARCHAR(50),
    `execution_steps_count` INT DEFAULT 1,
    `execution_time_ms` DECIMAL(8, 4) DEFAULT 0.0000,
    `executed_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ====================================================================
-- SEED DATA
-- ====================================================================

-- 1. Suppliers (8 Suppliers)
INSERT INTO `suppliers` (`supplier_code`, `name`, `contact_person`, `email`, `phone`, `address`, `category`, `reliability_score`, `avg_delivery_time_days`) VALUES
('SUP-01', 'Global Microchips Ltd', 'Arthur Hayes', 'arthur@globalchips.io', '+91 98765 43210', 'Tech Industrial Zone, Phase 1, Bengaluru', 'Semiconductors', 98.4, 2.1),
('SUP-02', 'Northern Steel & Alloys', 'Vikram Rathore', 'vikram@northernsteel.com', '+91 98111 22334', 'Plot 44, Industrial Corridor, Jamshedpur', 'Raw Metals', 96.0, 4.0),
('SUP-03', 'EcoPackaging Solutions', 'Ananya Sharma', 'ananya@ecopack.co', '+91 97222 33445', 'Green Park Logistics Park, Gurugram', 'Packaging', 94.2, 1.8),
('SUP-04', 'Precision Optics Works', 'David Zhang', 'david@precisionoptics.org', '+91 96333 44556', 'Electronic City, Hosur Road, Bengaluru', 'Optics & Sensors', 99.1, 3.2),
('SUP-05', 'Summit Chemicals Corp', 'Kavita Nair', 'kavita@summitchem.com', '+91 95444 55667', 'MIDC Industrial Estate, Navi Mumbai', 'Industrial Chemicals', 92.5, 5.0),
('SUP-06', 'Velocity Auto Components', 'Rajesh Khanna', 'rajesh@velocityparts.in', '+91 94555 66778', 'Auto Hub, Chakan MIDC, Pune', 'Automotive Parts', 95.8, 2.5),
('SUP-07', 'Quantum Battery Systems', 'Meera Sen', 'meera@quantumbatt.com', '+91 93666 77889', 'Hi-Tech Park, Gachibowli, Hyderabad', 'Power Storage', 97.6, 3.0),
('SUP-08', 'Apex Composite Polymers', 'Siddharth Verma', 'sid@apexpolymers.com', '+91 92777 88990', 'GIDC Sector 28, Gandhinagar', 'Polymers & Plastics', 93.0, 4.5);

-- 2. Warehouses (5 Warehouses)
INSERT INTO `warehouses` (`warehouse_code`, `name`, `location`, `city`, `capacity`, `lat`, `lng`) VALUES
('WH-DEL', 'North Regional Mega-Hub', 'National Highway 48, Manesar', 'Delhi NCR', 45000, 28.3537, 76.9405),
('WH-BOM', 'West Coastal Logistics Center', 'Bhiwandi Cargo Complex', 'Mumbai', 50000, 19.2967, 73.0631),
('WH-BLR', 'South Tech Fulfillment Center', 'Peenya Industrial Hub', 'Bengaluru', 40000, 13.0285, 77.5197),
('WH-CCU', 'East Bengal Gateway Warehouse', 'Dankuni Logistics Park', 'Kolkata', 35000, 22.6844, 88.2917),
('WH-NAG', 'Central Bharat Consolidation Node', 'MIHAN SEZ Center', 'Nagpur', 60000, 21.0560, 79.0322);

-- 3. Products (15 Products)
INSERT INTO `products` (`product_code`, `name`, `category`, `supplier_id`, `price`, `unit`) VALUES
('PRD-101', 'ARM Cortex Microcontroller MCU-X4', 'Semiconductors', 1, 850.00, 'units'),
('PRD-102', 'High-Torque Stepper Motor NEMA-23', 'Automotive Parts', 6, 2400.00, 'units'),
('PRD-103', 'Lithium Iron Phosphate Battery Pack 48V', 'Power Storage', 7, 18500.00, 'units'),
('PRD-104', 'Industrial Grade Cold-Rolled Steel Sheet', 'Raw Metals', 2, 4500.00, 'rolls'),
('PRD-105', 'Biodegradable Corrugated Shipping Box L', 'Packaging', 3, 45.00, 'boxes'),
('PRD-106', 'Optical Infrared Proximity Sensor V2', 'Optics & Sensors', 4, 620.00, 'units'),
('PRD-107', 'Thermally Conductive Epoxy Resin 5L', 'Industrial Chemicals', 5, 3200.00, 'cans'),
('PRD-108', 'Reinforced Polycarbonate Resin Pellets', 'Polymers & Plastics', 8, 180.00, 'kg'),
('PRD-109', 'Ceramic Dielectric Capacitor Tray (100x)', 'Semiconductors', 1, 350.00, 'trays'),
('PRD-110', 'Solid State Drive Industrial 1TB NVMe', 'Semiconductors', 1, 6800.00, 'units'),
('PRD-111', 'Fiber Optic Transceiver Module 10Gbps', 'Optics & Sensors', 4, 1450.00, 'units'),
('PRD-112', 'Anti-Static Bubble Wrap Roll 100m', 'Packaging', 3, 850.00, 'rolls'),
('PRD-113', 'Anodized Aluminum Framing Extrusion 2m', 'Raw Metals', 2, 1100.00, 'bars'),
('PRD-114', 'Deep-Cycle Solar Inverter Unit 5kVA', 'Power Storage', 7, 34000.00, 'units'),
('PRD-115', 'Silicone Thermal Paste Syringe (50g)', 'Industrial Chemicals', 5, 290.00, 'tubes');

-- 4. Delivery Locations (10 Customer Hubs)
INSERT INTO `delivery_locations` (`hub_code`, `name`, `city`, `state`, `pin_code`, `lat`, `lng`) VALUES
('HUB-PUN', 'Pune Smart Logistics Terminal', 'Pune', 'Maharashtra', '411001', 18.5204, 73.8567),
('HUB-MAA', 'Chennai Harbor Distribution Node', 'Chennai', 'Tamil Nadu', '600001', 13.0827, 80.2707),
('HUB-AMD', 'Ahmedabad Cargo Express Hub', 'Ahmedabad', 'Gujarat', '380001', 23.0225, 72.5714),
('HUB-HYD', 'Hyderabad Cyber Gateway Hub', 'Hyderabad', 'Telangana', '500001', 17.3850, 78.4867),
('HUB-JAI', 'Jaipur Pink City Terminal', 'Jaipur', 'Rajasthan', '302001', 26.9124, 75.7873),
('HUB-IXC', 'Chandigarh Northern Transit Hub', 'Chandigarh', 'Punjab', '160017', 30.7333, 76.7794),
('HUB-LKO', 'Lucknow Awadh Freight Terminal', 'Lucknow', 'Uttar Pradesh', '226001', 26.8467, 80.9462),
('HUB-STV', 'Surat Diamond Coast Depot', 'Surat', 'Gujarat', '395003', 21.1702, 72.8311),
('HUB-IDR', 'Indore Malwa Logistics Facility', 'Indore', 'Madhya Pradesh', '452001', 22.7196, 75.8577),
('HUB-BBI', 'Bhubaneswar Kalinga Depot', 'Bhubaneswar', 'Odisha', '751001', 20.2961, 85.8245);

-- 5. Inventory Records (20+ Records)
INSERT INTO `inventory` (`product_id`, `warehouse_id`, `quantity`, `reserved_quantity`, `reorder_level`) VALUES
(1, 1, 450, 40, 50),
(1, 2, 280, 20, 50),
(1, 3, 620, 60, 50),
(1, 5, 120, 10, 50),
(2, 2, 180, 15, 30),
(2, 3, 240, 20, 30),
(2, 5, 90, 5, 30),
(3, 1, 65, 10, 15),
(3, 3, 140, 15, 20),
(3, 5, 80, 5, 15),
(4, 4, 300, 25, 50),
(4, 5, 210, 15, 40),
(4, 1, 110, 10, 30),
(5, 1, 2500, 200, 500),
(5, 2, 1800, 150, 400),
(5, 3, 3200, 300, 500),
(5, 4, 1400, 100, 300),
(5, 5, 4000, 350, 600),
(6, 2, 320, 30, 50),
(6, 3, 580, 40, 60),
(6, 1, 210, 20, 40),
(7, 2, 150, 10, 25),
(7, 5, 95, 10, 20),
(10, 1, 140, 15, 20),
(10, 3, 220, 20, 30),
(14, 3, 45, 5, 10);

-- 6. Routes (20 Graph Edge Connections)
INSERT INTO `routes` (`source_type`, `source_id`, `destination_type`, `destination_id`, `distance_km`, `transit_time_hrs`) VALUES
('warehouse', 1, 'warehouse', 2, 1410.0, 24.0),
('warehouse', 1, 'warehouse', 4, 1530.0, 26.0),
('warehouse', 1, 'warehouse', 5, 1080.0, 18.0),
('warehouse', 2, 'warehouse', 3, 980.0, 16.0),
('warehouse', 2, 'warehouse', 5, 820.0, 14.0),
('warehouse', 3, 'warehouse', 5, 1090.0, 18.0),
('warehouse', 4, 'warehouse', 5, 970.0, 17.0),
('warehouse', 2, 'delivery_location', 1, 150.0, 3.5),
('warehouse', 5, 'delivery_location', 1, 710.0, 12.0),
('warehouse', 3, 'delivery_location', 2, 350.0, 6.0),
('warehouse', 2, 'delivery_location', 3, 530.0, 9.0),
('warehouse', 1, 'delivery_location', 3, 940.0, 16.0),
('warehouse', 3, 'delivery_location', 4, 570.0, 9.5),
('warehouse', 5, 'delivery_location', 4, 500.0, 8.5),
('warehouse', 1, 'delivery_location', 5, 270.0, 4.5),
('warehouse', 1, 'delivery_location', 6, 250.0, 4.0),
('warehouse', 1, 'delivery_location', 7, 550.0, 9.0),
('warehouse', 2, 'delivery_location', 8, 280.0, 5.0),
('warehouse', 5, 'delivery_location', 9, 440.0, 7.5),
('warehouse', 2, 'delivery_location', 9, 580.0, 10.0),
('warehouse', 4, 'delivery_location', 10, 440.0, 7.5),
('warehouse', 5, 'delivery_location', 10, 830.0, 14.0);

-- 7. Orders (20 Orders: 10 processed stack, 10 pending queue)
INSERT INTO `orders` (`order_number`, `customer_name`, `customer_phone`, `customer_email`, `product_id`, `quantity`, `delivery_location_id`, `status`, `assigned_warehouse_id`, `distance_km`, `estimated_cost`, `queue_position`) VALUES
('ORD-2026-001', 'Tesla Energy India', '+91 99000 11111', 'procure@tesla.in', 3, 20, 1, 'DELIVERED', 3, 980.0, 17790.0, 0),
('ORD-2026-002', 'Tata Motors Chakan Plant', '+91 99000 22222', 'supply@tatamotors.com', 2, 50, 1, 'DELIVERED', 2, 150.0, 2850.0, 0),
('ORD-2026-003', 'Bharat Electronics Ltd', '+91 99000 33333', 'orders@bel-india.in', 1, 100, 4, 'DISPATCHED', 3, 570.0, 10410.0, 0),
('ORD-2026-004', 'Jaipur Robotics Academy', '+91 99000 44444', 'lab@jaipurrobotics.edu', 6, 25, 5, 'DISPATCHED', 1, 270.0, 5010.0, 0),
('ORD-2026-005', 'Chandigarh Aero Systems', '+91 99000 55555', 'purchasing@chdaero.co', 10, 15, 6, 'DISPATCHED', 1, 250.0, 4650.0, 0),
('ORD-2026-006', 'L&T Heavy Engineering', '+91 99000 66666', 'procure@lnt.com', 4, 30, 8, 'DELIVERED', 2, 280.0, 5190.0, 0),
('ORD-2026-007', 'Godrej Aerospace', '+91 99000 77777', 'supply@godrej.com', 11, 40, 2, 'DELIVERED', 3, 350.0, 6450.0, 0),
('ORD-2026-008', 'Infosys Campus Logistics', '+91 99000 88888', 'campusops@infosys.com', 5, 200, 3, 'DISPATCHED', 2, 530.0, 9690.0, 0),
('ORD-2026-009', 'Wipro Infrastructure', '+91 99000 99999', 'admin@wipro.com', 7, 20, 9, 'DISPATCHED', 5, 440.0, 8070.0, 0),
('ORD-2026-010', 'Reliance Jio Fiber Hub', '+91 98111 00000', 'network@jio.com', 11, 60, 10, 'DELIVERED', 4, 440.0, 8070.0, 0),
('ORD-2026-011', 'Ather Mobility R&D', '+91 98888 12345', 'supply@ather.com', 1, 80, 1, 'PENDING_IN_QUEUE', NULL, NULL, NULL, 1),
('ORD-2026-012', 'Chennai Port Logistics Ltd', '+91 97777 23456', 'ops@chennaiport.gov.in', 5, 500, 2, 'PENDING_IN_QUEUE', NULL, NULL, NULL, 2),
('ORD-2026-013', 'Ahmedabad Automation Corp', '+91 96666 34567', 'orders@ahmedabad-auto.in', 2, 35, 3, 'PENDING_IN_QUEUE', NULL, NULL, NULL, 3),
('ORD-2026-014', 'Hyderabad Space Tech Hub', '+91 95555 45678', 'procurement@spacetech.org', 6, 40, 4, 'PENDING_IN_QUEUE', NULL, NULL, NULL, 4),
('ORD-2026-015', 'Indore MedTech Solutions', '+91 94444 56789', 'medtech@indoresolutions.com', 7, 30, 9, 'PENDING_IN_QUEUE', NULL, NULL, NULL, 5),
('ORD-2026-016', 'Mahindra Electric Vehicles', '+91 93333 67890', 'evsupply@mahindra.com', 3, 15, 1, 'PENDING_IN_QUEUE', NULL, NULL, NULL, 6),
('ORD-2026-017', 'Bhubaneswar Smart City Project', '+91 92222 78901', 'iot@smartbbsr.gov.in', 6, 50, 10, 'PENDING_IN_QUEUE', NULL, NULL, NULL, 7),
('ORD-2026-018', 'Surat Solar Microgrid', '+91 91111 89012', 'solar@suratsolar.org', 14, 8, 8, 'PENDING_IN_QUEUE', NULL, NULL, NULL, 8),
('ORD-2026-019', 'Lucknow Metro Rail Corp', '+91 90000 90123', 'procure@lmrc.in', 4, 45, 7, 'PENDING_IN_QUEUE', NULL, NULL, NULL, 9),
('ORD-2026-020', 'Punjab Agro Tech Logistics', '+91 98999 01234', 'tech@punjabagro.gov.in', 10, 25, 6, 'PENDING_IN_QUEUE', NULL, NULL, NULL, 10);
