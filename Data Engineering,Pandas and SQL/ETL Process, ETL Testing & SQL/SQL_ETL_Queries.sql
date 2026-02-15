create database airbnb1;
use airbnb1;
create table airbnb_stage (
    `Unnamed: 0` INT,
    `index` INT,
    `id` BIGINT,
    `NAME` TEXT,
    `host id` BIGINT,
    `host_identity_verified` VARCHAR(50),
    `host name` VARCHAR(255),
    `neighbourhood group` VARCHAR(100),
    `neighbourhood` VARCHAR(100),
    `lat` VARCHAR(50),
    `long` VARCHAR(50),
    `country` VARCHAR(100),
    `country code` VARCHAR(10),
    `instant_bookable` VARCHAR(10),
    `cancellation_policy` VARCHAR(50),
    `room type` VARCHAR(100),
    `Construction year` VARCHAR(20),
    `price` VARCHAR(20),
    `service fee` VARCHAR(20),
    `minimum nights` VARCHAR(20),
    `number of reviews` VARCHAR(20));

SET GLOBAL local_infile = 1;

LOAD DATA LOCAL INFILE 'C:/Users/Tarakeshwari/OneDrive/Desktop/Python-Foundations/Data Engineering,Pandas and SQL/Data Manipulation and Quality/Airbnb_Open_Data_Cleaned.csv'
INTO TABLE airbnb_stage
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

select * from airbnb_stage;

update airbnb_stage SET host_identity_verified = 'unconfirmed' 
where host_identity_verified IS NULL OR host_identity_verified='' and id IS NOT NULL ;

select * from airbnb_stage;

update airbnb_stage SET price=REPLACE(REPLACE(REPLACE(price,'$',''),',',''),' ','');
select * from airbnb_stage;

update airbnb_stage SET `service fee` = REPLACE(REPLACE(REPLACE(`service fee`,'$',''),',',''),' ','');

select * from airbnb_stage;

update airbnb_stage SET `service fee`= 0 where `service fee` IS NULL OR `service fee`='' and id IS NOT NULL ;
select * from airbnb_stage;

delete from airbnb_stage where price IS NULL OR price='';
select COUNT(*) AS empty_rows from airbnb_stage where price IS NULL OR price='';

select COUNT(*) as empty_rows FROM airbnb_stage where `name` IS NULL OR `name`= '';

update airbnb_stage SET instant_bookable='False' WHERE instant_bookable IS NULL OR instant_bookable='' and id IS NOT NULL ;
update airbnb_stage SET `country code`='US' WHERE `country code` IS NULL OR `country code`='' and id IS NOT NULL ;
update airbnb_stage SET `country`='United States' WHERE `country` IS NULL OR `country`='' and id IS NOT NULL ;
update airbnb_stage SET `cancellation_policy`='flexible' WHERE `cancellation_policy` IS NULL OR `cancellation_policy`='' and id IS NOT NULL ;
update airbnb_stage SET `name`='Standard apartment' WHERE `name` IS NULL OR `name`='';
delete from airbnb_stage where id IN (SELECT id FROM (SELECT id FROM airbnb_stage GROUP BY id HAVING COUNT(*) > 1) AS subquery);

desc airbnb_stage;
alter table airbnb_stage drop `index`;
alter table airbnb_stage drop `Unnamed: 0`;

select DISTINCT `Construction year`
from airbnb_stage
order by `Construction year` + 0;

create table airbnb_data (
    `id` BIGINT PRIMARY KEY,
    `NAME` TEXT,
    `host id` BIGINT,
    `host_identity_verified` VARCHAR(50),
    `host name` VARCHAR(255),
    `neighbourhood group` VARCHAR(100),
    `neighbourhood` VARCHAR(100),
    `lat` DECIMAL(10,7),
    `long` DECIMAL(10,7),
    `country` VARCHAR(100),
    `country code` VARCHAR(10),
    `instant_bookable` VARCHAR(10),
    `cancellation_policy` VARCHAR(50),
    `room type` VARCHAR(100),
    `Construction year` INT,
    `price` DECIMAL(10,2) NOT NULL,
    `service fee` DECIMAL(10,2) NOT NULL,
    `minimum nights` INT,
    `number of reviews` INT);
    
select
    `Construction year`, `Construction year` + 0 AS year_int,
    `minimum nights`, `minimum nights` + 0 AS nights_int,
    `number of reviews`, `number of reviews` + 0 AS reviews_int
from airbnb_stage
LIMIT 10;

select id, price,`service fee`, lat, `long`
from airbnb_stage WHERE price = '' OR `service fee` = '' OR lat = '' OR `long` = '';

insert into airbnb_data
SELECT
    `id`,
    `NAME`,
    `host id`,
    `host_identity_verified`,
    `host name`,
    `neighbourhood group`,
    `neighbourhood`,
    CAST(`lat` AS DECIMAL(10,7)),
    CAST(`long` AS DECIMAL(10,7)),
    `country`,
    `country code`,
    `instant_bookable`,
    `cancellation_policy`,
    `room type`,
    `Construction year` + 0,   
    CAST(`price` AS DECIMAL(10,2)),
    CAST(`service fee` AS DECIMAL(10,2)),
    `minimum nights` + 0,
    `number of reviews` + 0
FROM airbnb_stage;
