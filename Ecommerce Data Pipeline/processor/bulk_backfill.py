import os
import sys
import pandas as pd
import mysql.connector
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path to import local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generator.base_generator import EcommerceDataGenerator
from processor.loader import PostgresLoader

load_dotenv()

class BulkBackfiller:
    def __init__(self):
        self.mysql_conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', 'password'),
            database=os.getenv('MYSQL_DATABASE', 'ecommerce'),
            port=int(os.getenv('MYSQL_PORT', 3306))
        )
        self.mysql_cursor = self.mysql_conn.cursor()
        
        self.pg_loader = PostgresLoader(os.getenv('POSTGRES_DSN'))
        self.pg_loader.connect()
        self.gen = EcommerceDataGenerator()
        self.gen._init_base(200, 500)

    def init_schemas(self):
        print("Initializing database schemas...")
        # MySQL Schema
        with open('sql/schema.sql', 'r') as f:
            for stmt in f.read().split(';'):
                if stmt.strip():
                    try:
                        self.mysql_cursor.execute(stmt)
                    except Exception as e:
                        print(f"Warning: MySQL initialization error: {e}")
        self.mysql_conn.commit()

        # Postgres Schema (OLAP)
        with open('sql/olap_schema.sql', 'r') as f:
            # Postgres loader has its own cursor
            self.pg_loader.cursor.execute(f.read())
        self.pg_loader.commit()
        print("Schemas initialized.")

    def load_mysql(self, entity, rows):
        if not rows:
            return
            
        fields = list(rows[0].keys())
        placeholders = ", ".join(["%s"] * len(fields))
        
        if entity in ("customers", "products"):
            pk = "cid" if entity == "customers" else "pid"
            update_cols = ", ".join([f'{c}=VALUES({c})' for c in fields if c != pk])
            sql = f"INSERT INTO {entity} ({','.join(fields)}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_cols}"
        else:
            sql = f"INSERT IGNORE INTO {entity} ({','.join(fields)}) VALUES ({placeholders})"
        
        data = [tuple(row[f] for f in fields) for row in rows]
        self.mysql_cursor.executemany(sql, data)
        self.mysql_conn.commit()

    def run_backfill(self, days=730):
        self.init_schemas()
        start_date = datetime.now().date() - timedelta(days=days)
        print(f"Starting {days}-day Unified Bulk Backfill...")
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            if i % 30 == 0:
                print(f"--- Processing {current_date} ({i}/{days}) ---")
            
            day_data = self.gen.generate_day(current_date, num_orders=100)
            
            # 1. Load MySQL
            for entity, rows in day_data.items():
                self.load_mysql(entity, rows)
            
            # 2. Load Postgres (using our optimized loader logic)
            for entity, rows in day_data.items():
                for row in rows:
                    self.pg_loader.load(entity, row)
            
            # Commit after each day for safety
            self.pg_loader.commit()

        print("Unified Backfill Complete!")

    def close(self):
        self.mysql_cursor.close()
        self.mysql_conn.close()
        self.pg_loader.close()

if __name__ == "__main__":
    backfiller = BulkBackfiller()
    try:
        # Check if user passed days as argument
        days_to_run = int(sys.argv[1]) if len(sys.argv) > 1 else 730
        backfiller.run_backfill(days=days_to_run)
    finally:
        backfiller.close()
