import logging
import psycopg2
from datetime import datetime

logger = logging.getLogger(__name__)

class PostgresLoader:    
    def __init__(self, dsn):
        self.dsn = dsn
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = psycopg2.connect(self.dsn)
        self.conn.autocommit = False
        self.cursor = self.conn.cursor()

    def load(self, entity_type, data):
        handlers = {'customer': self.handle_customer,'product': self.handle_product,
                    'order': self.handle_order,'payment': self.handle_payment}
        handler = handlers.get(entity_type)
        if handler:
            handler(data)

    def _populate_dim_date(self, date_obj):
        date_id = int(date_obj.strftime('%Y%m%d'))
        self.cursor.execute("SELECT 1 FROM dim_date WHERE date_id = %s", (date_id,))
        if not self.cursor.fetchone():
            self.cursor.execute("""INSERT INTO dim_date (date_id, full_date, day, month, month_name, quarter, year, week_of_year, is_weekend)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",(date_id, date_obj.date() if hasattr(date_obj, 'date') else date_obj, date_obj.day, date_obj.month,
                 date_obj.strftime('%B'), (date_obj.month - 1) // 3 + 1,date_obj.year, date_obj.isocalendar()[1], date_obj.weekday() >= 5))
        return date_id

    def handle_customer(self, data):
        cid = data.get('cid')
        self.cursor.execute("SELECT customer_sk, name, email, address FROM dim_customer WHERE cid = %s AND is_current = TRUE", (cid,))
        row = self.cursor.fetchone()

        if not row:
            self.cursor.execute("""INSERT INTO dim_customer (cid, name, email, country, gender, dob, address)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                (cid, data.get('name'), data.get('email'), data.get('country'), data.get('gender'), data.get('dob'), data.get('address')))
        else:
            sk, old_name, old_email, old_address = row
            if data.get('name') != old_name or data.get('email') != old_email or data.get('address') != old_address:
                self.cursor.execute("UPDATE dim_customer SET is_current = FALSE, effective_end_date = CURRENT_TIMESTAMP WHERE customer_sk = %s", (sk,))
                self.cursor.execute("""INSERT INTO dim_customer (cid, name, email, country, gender, dob, address)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                    (cid, data.get('name'), data.get('email'), data.get('country'), data.get('gender'), data.get('dob'), data.get('address')))

    def handle_product(self, data):
        pid = data.get('pid')
        self.cursor.execute("SELECT product_sk, pname, price, brand, supplier FROM dim_product WHERE pid = %s AND is_current = TRUE", (pid,))
        row = self.cursor.fetchone()

        if not row:
            self.cursor.execute("INSERT INTO dim_product (pid, pname, category, price, brand, supplier) VALUES (%s, %s, %s, %s, %s, %s)",
                                (pid, data.get('pname'), data.get('category'), data.get('price'), data.get('brand'), data.get('supplier')))
        else:
            sk, old_pname, old_price, old_brand, old_supplier = row
            if data.get('pname') != old_pname or data.get('price') != float(old_price) or data.get('brand') != old_brand or data.get('supplier') != old_supplier:
                self.cursor.execute("UPDATE dim_product SET is_current = FALSE, effective_end_date = CURRENT_TIMESTAMP WHERE product_sk = %s", (sk,))
                self.cursor.execute("INSERT INTO dim_product (pid, pname, category, price, brand, supplier) VALUES (%s, %s, %s, %s, %s, %s)",
                                    (pid, data.get('pname'), data.get('category'), data.get('price'), data.get('brand'), data.get('supplier')))

    def handle_order(self, data):
        cid, pid = data.get('cid'), data.get('pid')
        self.cursor.execute("SELECT customer_sk FROM dim_customer WHERE cid = %s AND is_current = TRUE", (cid,))
        c_res = self.cursor.fetchone()
        self.cursor.execute("SELECT product_sk, price FROM dim_product WHERE pid = %s AND is_current = TRUE", (pid,))
        p_res = self.cursor.fetchone()

        if c_res and p_res:
            c_sk, p_sk, price = c_res[0], p_res[0], p_res[1]
            date_id = self._populate_dim_date(data.get('order_date'))
            self.cursor.execute("""
                INSERT INTO fact_sales (o_id, customer_sk, product_sk, date_id, quantity, unit_price, discount, total_amount)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (data.get('oid'), c_sk, p_sk, date_id, data.get('quantity'), price, data.get('discount'), float(price) * data.get('quantity') - data.get('discount')))

    def handle_payment(self, data):
        oid = data.get('oid')
        self.cursor.execute("SELECT customer_sk, date_id FROM fact_sales WHERE o_id = %s LIMIT 1", (oid,))
        res = self.cursor.fetchone()
        if not res:
            logger.warning(f"Skipping payment for Order {oid}: Order not found in fact_sales.")
            return

        c_sk, date_id = res
        method = data.get('method_payment')
        self.cursor.execute("SELECT payment_method_id FROM dim_payment WHERE method_name = %s", (method,))
        pm_res = self.cursor.fetchone()
        if not pm_res:
            self.cursor.execute("INSERT INTO dim_payment (method_name, provider) VALUES (%s, %s) RETURNING payment_method_id", (method, data.get('provider', 'Default')))
            pm_row = self.cursor.fetchone()
            if not pm_row:
                logger.error(f"Failed to retrieve payment_method_id for {method}")
                return
            pm_id = pm_row[0]
        else:
            pm_id = pm_res[0]

        self.cursor.execute("""INSERT INTO fact_payment (pay_id, o_id, customer_sk, date_id, payment_method_id, amount, payment_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""", (data.get('payid'), oid, c_sk, date_id, pm_id, data.get('amount'), data.get('payment_status')))
        self.cursor.execute("UPDATE fact_sales SET payment_method_id = %s, order_status = %s WHERE o_id = %s", (pm_id, data.get('order_status'), oid))

    def log_reconciliation(self, topic, partition, offset, payload_id, operation, status, error_msg=None):
        try:
            self.cursor.execute("""INSERT INTO reconciliation_log (topic, kafka_partition, kafka_offset, payload_id, operation, status, error_message)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""", (topic, partition, offset, payload_id, operation, status, error_msg))
        except Exception as e:
            logger.error(f"Failed to log reconciliation: {e}")

    def commit(self):
        if self.conn: 
            self.conn.commit()

    def rollback(self):
        if self.conn: 
            self.conn.rollback()

    def close(self):
        if self.cursor: 
            self.cursor.close()
        if self.conn: 
            self.conn.close()
        logger.info("Postgres connection closed.")
