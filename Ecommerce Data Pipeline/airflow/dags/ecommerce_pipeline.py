from airflow import DAG
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
import os
import shutil
import requests
import pandas as pd
import logging
import time
from generate_data import main
from etl_processor import main as etl_main
from run_logger_util import log_to_run_file

logger=logging.getLogger("airflow.task")
data_dir="/opt/airflow/data/ecommerce_daily"
processed_dir="/opt/airflow/data/ecommerce_processed"

def execute_ddl(filepath, **kwargs):
    run_id = kwargs.get('run_id')
    task_id = kwargs.get('ti').task_id
    
    hook = MySqlHook(mysql_conn_id="local_mysql")
    msg = f"Executing DDL script: {filepath}"
    logger.info(msg)
    if run_id: log_to_run_file(run_id, task_id, msg)
    
    with open(filepath, "r") as f:
        content = f.read()
    statements = [s.strip() for s in content.split("-- split") if s.strip()]
    for i, stmt in enumerate(statements):
        msg = f"Executing statement {i+1}/{len(statements)}"
        logger.info(msg)
        if run_id: log_to_run_file(run_id, task_id, msg)
        hook.run(stmt)
    
    msg = f"Finished executing {filepath}"
    logger.info(msg)
    if run_id: log_to_run_file(run_id, task_id, msg)

def register_debezium():
    connector_config = {"name": "mysql-ecommerce-connector",
        "config": {
            "connector.class": "io.debezium.connector.mysql.MySqlConnector",
            "database.hostname": os.getenv("MYSQL_HOST", "mysql"),
            "database.port": os.getenv("MYSQL_PORT", "3306"),
            "database.user": "root",
            "database.password": os.getenv("MYSQL_ROOT_PASSWORD", "root"),
            "database.server.id": os.getenv("DEBEZIUM_CONNECTOR_SERVER_ID", "184054"),
            "topic.prefix": "dbserver1",
            "database.include.list": "ecommerce",
            "table.include.list": "ecommerce.customers,ecommerce.products,ecommerce.orders,ecommerce.payments",
            "schema.history.internal.kafka.bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
            "schema.history.internal.kafka.topic": "schema-changes.ecommerce",
            "include.schema.changes": "true",
            "decimal.handling.mode": "string"}}
    
    debezium_url = os.getenv("DEBEZIUM_URL", "http://debezium:8083/connectors")
    url = f"{debezium_url}/mysql-ecommerce-connector"
    requests.delete(url)
    
    create_url = debezium_url
    headers = {"Content-Type": "application/json"}
    response = requests.post(create_url, headers=headers, json=connector_config)
    
    if response.status_code in [200, 201]:
        print("Debezium connector refreshed. Waiting for snapshot...")
        time.sleep(15)
    else:
        print(f"Registration Attempt: {response.status_code} {response.text}")

def load_csv_files(**kwargs):
    run_id = kwargs.get('run_id')
    task_id = kwargs.get('ti').task_id
    hook = MySqlHook(mysql_conn_id="local_mysql")
    os.makedirs(processed_dir, exist_ok=True)
    
    entities = ["customers", "products", "orders", "payments"]
    for entity in entities:
        files = [f for f in os.listdir(data_dir) 
            if f.startswith(entity) and f.endswith(".csv")]
        if not files:
            msg=f"No CSV files found for {entity}."
            logger.info(msg)
            if run_id: 
                log_to_run_file(run_id, task_id, msg)
            continue

        for f in files:
            filepath = os.path.join(data_dir, f)
            msg = f"Loading {entity} from {f}"
            logger.info(msg)
            if run_id: 
                log_to_run_file(run_id, task_id, msg)

            df = pd.read_csv(filepath)
            df = df.where(pd.notnull(df), None)
            df = df.drop_duplicates()
            
            if entity in ["customers", "products"]:
                target_fields = list(df.columns)
                placeholders = ", ".join(["%s"] * len(target_fields))
                sql = f"REPLACE INTO {entity} ({', '.join(target_fields)}) VALUES ({placeholders})"
                
                rows = df.values.tolist()
                for row in rows:
                    hook.run(sql, parameters=tuple(row))
            else:
                hook.insert_rows(table=entity, rows=df.values.tolist(), target_fields=list(df.columns))
            
            shutil.move(filepath, os.path.join(processed_dir, f))
            msg = f"Finished loading {f}"
            logger.info(msg)
            if run_id: 
                log_to_run_file(run_id, task_id, msg)

def task_success_log(context):
    run_id = context.get('run_id')
    task_id = context.get('task_instance').task_id
    log_to_run_file(run_id, task_id, f"Task {task_id} completed successfully.")

def task_failure_log(context):
    run_id = context.get('run_id')
    task_id = context.get('task_instance').task_id
    exception = context.get('exception')
    log_to_run_file(run_id, task_id, f"ERROR: Task {task_id} failed. Reason: {exception}")

with DAG(dag_id="ecommerce_pipeline",
    start_date=days_ago(4),
    schedule_interval="@daily",
    catchup=False,
    template_searchpath=["/opt/airflow/sql"],
    tags=["ecommerce", "cdc", "kafka"],
    default_args={"on_success_callback": task_success_log,"on_failure_callback": task_failure_log}) as dag:

    generate_csv = PythonOperator(task_id="generate_csv",python_callable=main)

    create_schema = MySqlOperator(task_id="create_schema",mysql_conn_id="local_mysql",
    sql="schema.sql",)

    create_trigger = PythonOperator(task_id="create_trigger",python_callable=execute_ddl,
    op_args=["/opt/airflow/sql/trigger.sql"],)

    load_csv = PythonOperator(task_id="load_csv",python_callable=load_csv_files)

    create_olap_schema = PostgresOperator(task_id="create_olap_schema",postgres_conn_id="local_postgres",
    sql="olap_schema.sql",)

    run_etl_processor = PythonOperator(task_id="run_etl_processor",python_callable=etl_main,
    op_kwargs={"batch_mode": True, "timeout_ms": 40000}) 

    start_debezium = PythonOperator(task_id="start_debezium",python_callable=register_debezium, )

    generate_csv >> create_schema >> create_trigger >> create_olap_schema >> \
    start_debezium >> load_csv >> run_etl_processor

