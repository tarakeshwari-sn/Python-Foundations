import os
import shutil
import logging
import pandas as pd
from airflow.providers.mysql.hooks.mysql import MySqlHook
from run_logger_util import log_to_run_file

logger = logging.getLogger("airflow.task")
data_dir = os.getenv("DATA_DIR", "/opt/airflow/data/ecommerce_daily")
processed_dir = os.getenv("PROCESSED_DATA_DIR", "/opt/airflow/data/ecommerce_processed")

def execute_ddl(filepath, **kwargs):
    ti = kwargs.get('ti')
    run_id, task_id = kwargs.get('run_id'), ti.task_id if ti else 'execute_ddl'
    hook = MySqlHook(mysql_conn_id="local_mysql")
    
    def log(msg):
        logger.info(msg)
        if run_id: 
            log_to_run_file(run_id, task_id, msg)
    
    log(f"Executing DDL: {filepath}")
    with open(filepath, "r") as f:
        for i, stmt in enumerate([s.strip() for s in f.read().split("-- split") if s.strip()]):
            log(f"Stmt {i+1}")
            hook.run(stmt)

def load_csv_files(**kwargs):
    ti = kwargs.get('ti')
    run_id, task_id = kwargs.get('run_id'), ti.task_id if ti else 'load_csv'
    hook = MySqlHook(mysql_conn_id="local_mysql")
    os.makedirs(processed_dir, exist_ok=True)
    
    def log(msg):
        logger.info(msg)
        if run_id: log_to_run_file(run_id, task_id, msg)
    
    for entity in ("customers", "products", "orders", "payments"):
        if not os.path.exists(data_dir):
            log(f"Data directory does not exist: {data_dir}")
            break
            
        files = [f for f in os.listdir(data_dir) if f.startswith(entity) and f.endswith(".csv")]
        
        if not files:
            log(f"No CSV for {entity}")
            continue
        
        for fname in files:
            fpath = os.path.join(data_dir, fname)
            log(f"Loading {fname}")
            try:
                # Read CSV only once and handle nulls
                df = pd.read_csv(fpath)
                df = df.where(pd.notnull(df), None).drop_duplicates()
                
                fields = list(df.columns)
                placeholders = ", ".join(["%s"]*len(fields))
                
                if entity in ("customers", "products"):
                    pk = "cid" if entity == "customers" else "pid"
                    update_cols = ", ".join([f'{c}=VALUES({c})' for c in fields if c!=pk])
                    sql = f"INSERT INTO {entity} ({','.join(fields)}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_cols}"
                else: 
                    sql = f"INSERT IGNORE INTO {entity} ({','.join(fields)}) VALUES ({placeholders})"
                
                # Execute in batch if possible (though hook.run might already be efficient)
                for row in df.values.tolist(): 
                    hook.run(sql, parameters=tuple(row))
                
                shutil.move(fpath, os.path.join(processed_dir, fname))
            except Exception as e:
                log(f"Error loading {fname}: {e}")

def task_success_log(context):
    log_to_run_file(context.get('run_id'), context.get('task_instance').task_id, "SUCCESS")

def task_failure_log(context):
    log_to_run_file(context.get('run_id'), context.get('task_instance').task_id, f"FAILED: {context.get('exception')}")
