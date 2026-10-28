-- ====================================================================
-- INTELLIGENT SUPPLY CHAIN MANAGEMENT SYSTEM
-- Academic Data Structures and Algorithmic Problem Solving Project
-- MySQL Database Schema
-- ====================================================================

DROP DATABASE IF EXISTS `supply_chain_db`;
CREATE DATABASE IF NOT EXISTS `supply_chain_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `supply_chain_db`;

-- 1. Suppliers Table (Linked List Demonstration)
CREATE TABLE IF NOT EXISTS `suppliers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `supplier_code` VARCHAR(20) UNIQUE NOT NULL,
    `name` VARCHAR(150) NOT NULL,
    `contact_person` VARCHAR(100),
    `email` VARCHAR(100),
    `phone` VARCHAR(30),
    `address` TEXT,
    `category` VARCHAR(50),
    `reliability_score` DECIMAL(5, 2) NOT NULL DEFAULT 95.00,
    `avg_delivery_time_days` DECIMAL(4, 1) NOT NULL DEFAULT 3.0,
    `status` VARCHAR(20) DEFAULT 'ACTIVE',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Warehouses Table (Graph Vertices & Greedy Algorithm Candidates)
CREATE TABLE IF NOT EXISTS `warehouses` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `warehouse_code` VARCHAR(20) UNIQUE NOT NULL,
    `name` VARCHAR(150) NOT NULL,
    `location` VARCHAR(100) NOT NULL,
    `city` VARCHAR(80),
    `capacity` INT NOT NULL DEFAULT 10000,
    `lat` DECIMAL(10, 6) NOT NULL DEFAULT 0.000000,
    `lng` DECIMAL(10, 6) NOT NULL DEFAULT 0.000000,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Products Table (Linked List & Binary Search Demonstration)
CREATE TABLE IF NOT EXISTS `products` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `product_code` VARCHAR(20) UNIQUE NOT NULL,
    `name` VARCHAR(150) NOT NULL,
    `category` VARCHAR(80) NOT NULL,
    `supplier_id` INT,
    `price` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    `unit` VARCHAR(20) DEFAULT 'units',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_product_supplier` FOREIGN KEY (`supplier_id`) 
        REFERENCES `suppliers` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Inventory Table (Binary Search Tree Keyed by Product/Inventory ID)
CREATE TABLE IF NOT EXISTS `inventory` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `product_id` INT NOT NULL,
    `warehouse_id` INT NOT NULL,
    `quantity` INT NOT NULL DEFAULT 0,
    `reserved_quantity` INT NOT NULL DEFAULT 0,
    `reorder_level` INT NOT NULL DEFAULT 50,
    `last_updated` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_product_warehouse` (`product_id`, `warehouse_id`),
    CONSTRAINT `fk_inventory_product` FOREIGN KEY (`product_id`) 
        REFERENCES `products` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_inventory_warehouse` FOREIGN KEY (`warehouse_id`) 
        REFERENCES `warehouses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Delivery Locations Table (Graph Vertices / Customer Hubs)
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

-- 6. Routes Table (Graph Edges with Distance Weights)
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

-- 7. Orders Table (FIFO Queue Demonstration)
CREATE TABLE IF NOT EXISTS `orders` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `order_number` VARCHAR(30) UNIQUE NOT NULL,
    `customer_name` VARCHAR(150) NOT NULL,
    `customer_phone` VARCHAR(30),
    `customer_email` VARCHAR(100),
    `product_id` INT NOT NULL,
    `quantity` INT NOT NULL,
    `priority` INT DEFAULT 2,
    `delivery_location_id` INT NOT NULL,
    `status` ENUM('PENDING_IN_QUEUE', 'PROCESSING', 'DISPATCHED', 'DELIVERED', 'CANCELLED') NOT NULL DEFAULT 'PENDING_IN_QUEUE',
    `assigned_warehouse_id` INT NULL,
    `distance_km` DECIMAL(8, 2) NULL,
    `estimated_cost` DECIMAL(10, 2) NULL,
    `queue_position` INT DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `processed_at` TIMESTAMP NULL,
    CONSTRAINT `fk_order_product` FOREIGN KEY (`product_id`) 
        REFERENCES `products` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `fk_order_delivery_location` FOREIGN KEY (`delivery_location_id`) 
        REFERENCES `delivery_locations` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `fk_order_warehouse` FOREIGN KEY (`assigned_warehouse_id`) 
        REFERENCES `warehouses` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Order Items Table
CREATE TABLE IF NOT EXISTS `order_items` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `order_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    `quantity` INT NOT NULL,
    `unit_price` DECIMAL(10, 2) NOT NULL,
    CONSTRAINT `fk_item_order` FOREIGN KEY (`order_id`) 
        REFERENCES `orders` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_item_product` FOREIGN KEY (`product_id`) 
        REFERENCES `products` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. Algorithm Logs Table (Audits algorithm executions: Greedy, BFS, Binary Search, BST)
CREATE TABLE IF NOT EXISTS `algorithm_logs` (
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
