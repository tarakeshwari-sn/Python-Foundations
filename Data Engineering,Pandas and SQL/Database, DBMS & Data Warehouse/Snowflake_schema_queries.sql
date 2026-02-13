create database sales1;
use sales1;

create table dim_country (country_id INT PRIMARY KEY,country_name VARCHAR(50));

create table dim_state (
    state_id INT PRIMARY KEY,
    state_name VARCHAR(50),
    country_id INT,FOREIGN KEY (country_id) REFERENCES dim_country(country_id));

create table dim_city (
    city_id INT PRIMARY KEY,city_name VARCHAR(50),
    state_id INT,FOREIGN KEY (state_id) REFERENCES dim_state(state_id));

create table dim_customer (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(20),
    gender VARCHAR(10),
    city_id INT,
    FOREIGN KEY (city_id) REFERENCES dim_city(city_id));

create table dim_category (category_id INT PRIMARY KEY,category_name VARCHAR(50));

create table dim_subcategory (
    subcategory_id INT PRIMARY KEY,
    subcategory_name VARCHAR(50),
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES dim_category(category_id));

create table dim_brand (brand_id INT PRIMARY KEY,brand_name VARCHAR(50));

create table dim_product (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    subcategory_id INT,
    brand_id INT,
    FOREIGN KEY (subcategory_id) REFERENCES dim_subcategory(subcategory_id),
    FOREIGN KEY (brand_id) REFERENCES dim_brand(brand_id));

create table dim_year (year_id INT PRIMARY KEY,year INT);

create table dim_quarter (
    quarter_id INT PRIMARY KEY,
    quarter INT,
    year_id INT,
    FOREIGN KEY (year_id) REFERENCES dim_year(year_id));

create table dim_month (
    month_id INT PRIMARY KEY,
    month INT,
    quarter_id INT,
    FOREIGN KEY (quarter_id) REFERENCES dim_quarter(quarter_id));

create table dim_day (
    day_id INT PRIMARY KEY,
    day INT,
    month_id INT,
    FOREIGN KEY (month_id) REFERENCES dim_month(month_id));

create table dim_date (
    date_id INT PRIMARY KEY,
    full_date DATE,
    day_id INT,
    FOREIGN KEY (day_id) REFERENCES dim_day(day_id));

create table dim_store (
    store_id INT PRIMARY KEY,
    store_name VARCHAR(100),
    city_id INT,
    FOREIGN KEY (city_id) REFERENCES dim_city(city_id));

create table fact_sales (
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

insert into dim_country VALUES (1,'India');
insert into dim_state VALUES (1,'TN',1);
insert into dim_city VALUES (1,'Palani',1),(2,'CBE',1),(3,'Ooty',1),(4,'CH',1),(5,'MD',1);
insert into dim_customer VALUES (1,'Thansika','F',1),(2,'Tara','F',2),(3,'Fathi','F',3);

insert into dim_category VALUES (1,'Sweets'),(2,'Savourites');
insert into dim_subcategory VALUES (1,'Chilled',1),(2,'Cold',1),(3,'Normal',2);
insert into dim_brand VALUES (1,'Cadbury'),(2,'Krishna'),(3,'Unibic');
insert into dim_product VALUES (101,'Chocolate',1,1),(102,'Badusha',2,2),(103,'Biscuits',3,3);

insert into dim_year VALUES (1,2025);
insert into dim_quarter VALUES (1,1,1);
insert into dim_month VALUES (1,2,1);
insert into dim_day VALUES (1,11,1),(2,12,1),(3,13,1);
insert into dim_date VALUES (1,'2025-02-11',1),(2,'2025-02-12',2),(3,'2025-02-13',3);

insert into dim_store VALUES (1,'Tara Place',2),(2,'A Place',4),(3,'B Place',5);

insert into fact_sales VALUES (102,1,1,101,1,200,20000.00),(103,2,2,102,2,50,5000.00),(104,3,3,103,3,100,10000.00);
select * from fact_sales;
