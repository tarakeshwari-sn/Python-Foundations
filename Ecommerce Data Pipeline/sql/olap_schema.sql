CREATE TABLE IF NOT EXISTS dim_customer (
    customer_sk SERIAL PRIMARY KEY, -- Surrogate Key
    cid VARCHAR(36),                -- Business Key (UUID)
    name VARCHAR(255),
    dob DATE,
    country VARCHAR(100),
    gender VARCHAR(20),
    address TEXT,
    email VARCHAR(255),
    effective_start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_end_date TIMESTAMP,
    is_current BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_sk SERIAL PRIMARY KEY,  -- Surrogate Key
    pid VARCHAR(36),                -- Business Key (UUID)
    pname VARCHAR(255),
    category VARCHAR(100),
    price DECIMAL(10, 2),
    brand VARCHAR(100),
    supplier VARCHAR(100),
    effective_start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_end_date TIMESTAMP,
    is_current BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id INT PRIMARY KEY,
    full_date DATE,
    day INT,
    month INT,
    month_name VARCHAR(20),
    quarter INT,
    year INT,
    week_of_year INT,
    is_weekend BOOLEAN
);

CREATE TABLE IF NOT EXISTS dim_payment (
    payment_method_id SERIAL PRIMARY KEY,
    method_name VARCHAR(50),
    provider VARCHAR(50)
);

-- Fact Tables
CREATE TABLE IF NOT EXISTS fact_sales (
    sales_id SERIAL PRIMARY KEY,
    o_id VARCHAR(36),
    customer_sk INT REFERENCES dim_customer(customer_sk),
    product_sk INT REFERENCES dim_product(product_sk),
    date_id INT REFERENCES dim_date(date_id),
    payment_method_id INT REFERENCES dim_payment(payment_method_id),
    quantity INT,
    unit_price DECIMAL(10, 2),
    discount DECIMAL(10, 2),
    total_amount DECIMAL(12, 2)
);

CREATE TABLE IF NOT EXISTS fact_payment (
    payment_id SERIAL PRIMARY KEY,
    o_id VARCHAR(36),
    customer_sk INT REFERENCES dim_customer(customer_sk),
    date_id INT REFERENCES dim_date(date_id),
    payment_method_id INT REFERENCES dim_payment(payment_method_id),
    amount DECIMAL(12, 2),
    payment_status VARCHAR(50)
);
