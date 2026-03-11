CREATE DATABASE IF NOT EXISTS ecommerce;
USE ecommerce;

CREATE TABLE IF NOT EXISTS customers (
    cid VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255),
    dob DATE,
    country VARCHAR(100),
    gender VARCHAR(20),
    address TEXT,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    pid VARCHAR(36) PRIMARY KEY,
    pname VARCHAR(255),
    category VARCHAR(100),
    price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    oid VARCHAR(36) PRIMARY KEY,
    cid VARCHAR(36),
    pid VARCHAR(36),
    quantity INT,
    order_date DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cid) REFERENCES customers(cid),
    FOREIGN KEY (pid) REFERENCES products(pid)
);

CREATE TABLE IF NOT EXISTS payments (
    payid VARCHAR(36) PRIMARY KEY,
    oid VARCHAR(36),
    amount DECIMAL(12,2),
    method_payment VARCHAR(100),
    payment_status VARCHAR(50),
    order_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (oid) REFERENCES orders(oid)
);

CREATE TABLE IF NOT EXISTS ecommerce_audit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entity_type VARCHAR(50),
    entity_id VARCHAR(36),
    attribute_changed VARCHAR(255),
    old_value VARCHAR(255),
    new_value VARCHAR(255),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(255)
);