create database sales;
use sales;

SELECT DATABASE();

CREATE TABLE dim_customer (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(20),
    gender VARCHAR(10),
    city VARCHAR(50),
    state VARCHAR(20),
    country VARCHAR(20));

CREATE TABLE dim_product (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    subcategory VARCHAR(50),
    brand VARCHAR(50));

CREATE TABLE dim_date (
    date_id INT PRIMARY KEY,
    full_date DATE,
    day INT,
    month INT,
    quarter INT,
    year INT);

CREATE TABLE dim_store (
    store_id INT PRIMARY KEY,
    store_name VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50));

INSERT INTO dim_customer VALUES (1,'Thansika','F','Palani','TN','India'),
(2,'Tara','F','CBE','TN','India'),(3,'Fathi','F','Ooty','TN','India');

SELECT * FROM dim_customer;

INSERT INTO dim_product VALUES (101,'Chocolate','Sweets','Chilled','Cadbury'),
(102,'Badusha','Sweets','Cold','Krishna'),(103,'Biscuits','Savourites','Normal','Unibic');

SELECT * FROM dim_product;

INSERT INTO dim_date VALUES(1,'2025-02-11',11,2,1,2025),
(2,'2025-02-12',12,2, 1, 2025),(3, '2025-02-13', 13, 2, 1, 2025);

SELECT * FROM dim_date;

INSERT INTO dim_store VALUES (1,'Tara Place','CBE','TN','India'),(2,'A Place','CH','TN','India'),(3,'B Place','MD','TN','India');

SELECT * FROM dim_store;

CREATE TABLE fact_sales (
    sales_id BIGINT PRIMARY KEY,
    date_id INT,
    customer_id INT,
    product_id INT,
    store_id INT,
    quantity INT,
    total_amount DECIMAL(10,2),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
    FOREIGN KEY (store_id) REFERENCES dim_store(store_id));

INSERT INTO fact_sales VALUES(102,1,1,101,1,200,20000.00),(103,2, 2,102,2,50,5000.00),(104,3,3,103,3,100,10000.00);

SELECT * FROM fact_sales;
