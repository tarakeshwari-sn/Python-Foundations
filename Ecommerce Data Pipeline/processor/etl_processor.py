import json
import base64
import logging
from kafka import KafkaConsumer
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, date, timedelta
from run_logger_util import log_to_run_file
import struct
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def to_float(value):
    
    if value is None:
        return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, bytes):
        try:
            return float(int.from_bytes(value, byteorder='big', signed=True)) / 100.0
        except Exception:
            return float(value.decode('utf-8', errors='replace'))
    
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            pass
        try:
            decoded = base64.b64decode(value + '==')
            unscaled = int.from_bytes(decoded, byteorder='big', signed=True)
            return unscaled / 100.0
        except Exception as e:
            raise ValueError(f"Cannot convert '{value}' to float: {e}")
    raise ValueError(f"Unsupported type for to_float: {type(value)} value={value!r}")

def to_date(value):
    
    if value is None:
        return None
    
    if isinstance(value, (date, datetime)):
        return value
    
    if isinstance(value,int):
        if abs(value) < 100_000:
            return date(1970, 1, 1) + timedelta(days=value)
        else:
            return datetime(1970, 1, 1) + timedelta(microseconds=value)
    
    if isinstance(value, str):
        for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S'):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Cannot parse date string: '{value}'")
    raise ValueError(f"Unsupported type for to_date: {type(value)} value={value!r}")

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092').split(',')
POSTGRES_DSN = os.getenv('POSTGRES_DSN', "host=postgres port=5432 dbname=ecommerce_olap user=airflow password=airflow")
TOPIC_PREFIX = os.getenv('TOPIC_PREFIX', "dbserver1.ecommerce")
TOPICS = [f"{TOPIC_PREFIX}.customers",f"{TOPIC_PREFIX}.products",
         f"{TOPIC_PREFIX}.orders",f"{TOPIC_PREFIX}.payments"]

def get_db_connection():
    return psycopg2.connect(POSTGRES_DSN)

def populate_dim_date(cursor, date_obj):
    date_id = int(date_obj.strftime('%Y%m%d'))
    cursor.execute("SELECT 1 FROM dim_date WHERE date_id = %s", (date_id,))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO dim_date (date_id, full_date, day, month, month_name, quarter, year, week_of_year, is_weekend)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
            (date_id, date_obj.date(), date_obj.day, date_obj.month, 
            date_obj.strftime('%B'), (date_obj.month - 1) // 3 + 1, 
            date_obj.year, date_obj.isocalendar()[1], date_obj.weekday() >= 5
        ))
    return date_id

def handle_customer(cursor, payload):
    cid = payload.get('cid')
    name = payload.get('name')
    email = payload.get('email')
    address = payload.get('address')
    
    cursor.execute("SELECT customer_sk, name, email, address FROM dim_customer WHERE cid = %s AND is_current = TRUE", (cid,))
    row = cursor.fetchone()
    
    if not row:
        cursor.execute("""
            INSERT INTO dim_customer (cid, name, email, country, gender, dob, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""", 
            (cid, name, email, payload.get('country'), payload.get('gender'), to_date(payload.get('dob')), address))
    else:
        sk, old_name, old_email, old_address = row
        if name != old_name or email != old_email or address != old_address:
            cursor.execute("UPDATE dim_customer SET is_current = FALSE, effective_end_date = CURRENT_TIMESTAMP WHERE customer_sk = %s", (sk,))
            cursor.execute("""
                INSERT INTO dim_customer (cid, name, email, country, gender, dob, address)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""", 
                (cid, name, email, payload.get('country'), payload.get('gender'), to_date(payload.get('dob')), address))

def handle_product(cursor, payload):
    pid = payload.get('pid')
    pname = payload.get('pname')
    price = to_float(payload.get('price'))
    
    cursor.execute("SELECT product_sk, pname, price FROM dim_product WHERE pid = %s AND is_current = TRUE", (pid,))
    row = cursor.fetchone()
    
    if not row:
        cursor.execute("INSERT INTO dim_product (pid, pname, category, price) VALUES (%s, %s, %s, %s)", 
                       (pid, pname, payload.get('category'), price))
    else:
        sk, old_pname, old_price = row
        if pname != old_pname or price != float(old_price):
            cursor.execute("UPDATE dim_product SET is_current = FALSE, effective_end_date = CURRENT_TIMESTAMP WHERE product_sk = %s", (sk,))
            cursor.execute("INSERT INTO dim_product (pid, pname, category, price) VALUES (%s, %s, %s, %s)", 
                           (pid, pname, payload.get('category'), price))

def handle_order(cursor, payload):
    oid = payload.get('oid')
    cid = payload.get('cid')
    pid = payload.get('pid')
    qty = payload.get('quantity')
    
    # Lookups
    cursor.execute("SELECT customer_sk FROM dim_customer WHERE cid = %s AND is_current = TRUE", (cid,))
    c_res = cursor.fetchone()
    cursor.execute("SELECT product_sk, price FROM dim_product WHERE pid = %s AND is_current = TRUE", (pid,))
    p_res = cursor.fetchone()
    
    if c_res and p_res:
        c_sk = c_res[0]
        p_sk, price = p_res[0], p_res[1]
        date_id = populate_dim_date(cursor, datetime.now()) # Fallback to now for demo
        
        cursor.execute("""
            INSERT INTO fact_sales (o_id, customer_sk, product_sk, date_id, quantity, unit_price, total_amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (oid, c_sk, p_sk, date_id, qty, price, float(price)*qty))

def handle_payment(cursor, payload):
    oid = payload.get('oid')
    amount = to_float(payload.get('amount'))
    method = payload.get('method_payment')
    status = payload.get('payment_status')
    
    cursor.execute("SELECT customer_sk, date_id FROM fact_sales WHERE o_id = %s LIMIT 1", (oid,))
    res = cursor.fetchone()
    if res:
        c_sk,date_id = res
        cursor.execute("SELECT payment_method_id FROM dim_payment WHERE method_name = %s", (method,))
        pm_res = cursor.fetchone()
        if not pm_res:
            cursor.execute("INSERT INTO dim_payment (method_name, provider) VALUES (%s, %s) RETURNING payment_method_id", (method, 'Default'))
            pm_id = cursor.fetchone()[0]
        else:
            pm_id = pm_res[0]
        
        cursor.execute("""INSERT INTO fact_payment (o_id, customer_sk, date_id, payment_method_id, amount, payment_status)
        VALUES (%s, %s, %s, %s, %s, %s)""",(oid, c_sk, date_id, pm_id, amount, status))
        logger.info(f"Payment for Order {oid} processed into fact_payment.")
    else:
        logger.warning(f"Skipping payment for Order {oid}: Order not found in fact_sales yet.")

def process_message(cursor, topic, full_msg):
    payload = full_msg.get('payload', {})
    after = payload.get('after')
    op = payload.get('op') # 'c' = create, 'u' = update, 'r' = read/snapshot
    
    if not after: 
        return
    
    op_desc = "CREATED" if op in ['c', 'r'] else "UPDATED"
    
    if 'customers' in topic:
        handle_customer(cursor, after)
        logger.info(f"Customer {after.get('cid')} {op_desc}")
    elif 'products' in topic:
        handle_product(cursor, after)
        logger.info(f"Product {after.get('pid')} {op_desc}")
    elif 'orders' in topic:
        handle_order(cursor, after)
    elif 'payments' in topic:
        handle_payment(cursor, after)

def main(batch_mode=False, timeout_ms=5000, **kwargs):
    run_id = kwargs.get('run_id')
    task_id = kwargs.get('ti', {}).task_id if kwargs.get('ti') else 'run_etl_processor'

    def log_msg(msg, level='info'):
        if level == 'info': 
            logger.info(msg)
        elif level == 'error': 
            logger.error(msg)
        if run_id:
            log_to_run_file(run_id, task_id, msg)

    group_id = f'etl_processor_group_{run_id}' if run_id else 'etl_processor_group_default'
    log_msg(f"Listening to topics: {TOPICS}")
    log_msg(f"Starting Multi-Topic ETL Processor (Group: {group_id})...")
    
    consumer = KafkaConsumer(*TOPICS, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')), 
        auto_offset_reset='earliest',
        enable_auto_commit=True, group_id=group_id,
        consumer_timeout_ms=timeout_ms if batch_mode else -1)

    conn = get_db_connection(); 
    conn.autocommit = True; 
    cursor = conn.cursor()
    
    message_count = 0
    failed_count = 0
    try:
        for message in consumer:
            message_count += 1
            if message_count % 10 == 0:
                log_msg(f"Processed {message_count} messages...")
            try:
                process_message(cursor, message.topic, message.value)
            except Exception as e:
                failed_count += 1
                log_msg(f"Skipping message {message_count} on topic '{message.topic}' due to error: {e}", level='error')
    
    except Exception as e:
        log_msg(f"Fatal error in consumer loop: {e}", level='error')
    
    finally:
        if message_count == 0:
            log_msg("No messages found in topics during this window.", level='warning')
        log_msg(f"ETL session finished. Total messages: {message_count}, Failed: {failed_count}")
        cursor.close(); conn.close()

if __name__ == "__main__":
    main()
