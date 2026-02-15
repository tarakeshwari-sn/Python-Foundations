create database airbnb;
use airbnb;

create table airbnb_data (
    `Unnamed: 0` INT,
    `index` INT,
    `id` BIGINT,
    `NAME` TEXT,
    `host id` BIGINT,
    `host_identity_verified` VARCHAR(50),
    `host name` VARCHAR(255),
    `neighbourhood group` VARCHAR(100),
    `neighbourhood` VARCHAR(100),
    `lat` DOUBLE,
    `long` DOUBLE,
    `country` VARCHAR(100),
    `country code` VARCHAR(10),
    `instant_bookable` VARCHAR(10),
    `cancellation_policy` VARCHAR(50),
    `room type` VARCHAR(100),
    `Construction year` DOUBLE,
    `price` VARCHAR(20),
    `service fee` VARCHAR(20),
    `minimum nights` DOUBLE,
    `number of reviews` DOUBLE);

show tables;
SET GLOBAL local_infile = 1;

LOAD DATA LOCAL INFILE 'C:/Users/Tarakeshwari/OneDrive/Desktop/Python-Foundations/Data Engineering,Pandas and SQL/Data Manipulation and Quality/Airbnb_Open_Data_Cleaned.csv'
INTO TABLE airbnb_data
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

select * from airbnb_data;

update airbnb_data SET host_identity_verified = 'unconfirmed' 
where host_identity_verified IS NULL OR host_identity_verified='' and id IS NOT NULL ;

select * from airbnb_data;

update airbnb_data SET price=REPLACE(REPLACE(REPLACE(price,'$',''),',',''),' ','');
select * from airbnb_data;

update airbnb_data SET `service fee` = REPLACE(REPLACE(REPLACE(`service fee`,'$',''),',',''),' ','');
select * from airbnb_data;

update airbnb_data SET `service fee`= 0 
where `service fee` IS NULL OR `service fee`='' and id IS NOT NULL ;
select * from airbnb_data;

delete from airbnb_data where price IS NULL OR price='';
select COUNT(*) AS empty_rows from airbnb_data where price IS NULL OR price='';

select COUNT(*) as empty_rows FROM airbnb_data where `name` IS NULL OR `name`= '';

update airbnb_data SET instant_bookable='False' WHERE instant_bookable IS NULL OR instant_bookable='' and id IS NOT NULL ;
update airbnb_data SET `country code`='US' WHERE `country code` IS NULL OR `country code`='' and id IS NOT NULL ;
update airbnb_data SET `country`='United States' WHERE `country` IS NULL OR `country`='' and id IS NOT NULL ;
update airbnb_data SET `cancellation_policy`='flexible' WHERE `cancellation_policy` IS NULL OR `cancellation_policy`='' and id IS NOT NULL ;
update airbnb_data SET `name`='Standard apartment' WHERE `name` IS NULL OR `name`='';
delete from airbnb_data where id IN (SELECT id FROM (SELECT id FROM airbnb_data GROUP BY id HAVING COUNT(*) > 1) AS subquery);

alter table airbnb_data
modify `Construction year` INT NULL,
modify `minimum nights` INT NULL,
modify `number of reviews` INT NULL,
modify `lat` DECIMAL(10,7) NULL,
modify `long` DECIMAL(10,7) NULL,
modify `price` DECIMAL(10,2) NOT NULL,
modify `service fee` DECIMAL(10,2) NOT NULL;

alter table airbnb_data ADD PRIMARY KEY (id);
desc airbnb_data;
select COUNT(*) AS bad_instant_bookable FROM airbnb_data WHERE instant_bookable IS NULL OR instant_bookable = '';
select COUNT(*) AS bad_country_code FROM airbnb_data WHERE `country code` IS NULL OR `country code` = '';
select COUNT(*) AS bad_country FROM airbnb_data WHERE `country` IS NULL OR `country` = '';
select COUNT(*) AS bad_cancellation_policy FROM airbnb_data WHERE `cancellation_policy` IS NULL OR `cancellation_policy` = '';
select count(*) from airbnb_data;

select id,COUNT(*) AS dup_count FROM airbnb_data GROUP BY id HAVING COUNT(*) > 1;
select neighbourhood,AVG(price) AS avg_price FROM airbnb_data GROUP BY neighbourhood HAVING AVG(price) > 0;
select cancellation_policy,COUNT(*) AS listings FROM airbnb_data GROUP BY cancellation_policy ORDER BY listings DESC;
select id,price,`service fee` FROM airbnb_data WHERE CAST(`service fee` AS UNSIGNED)>CAST(price AS UNSIGNED);

select * from airbnb_data;
