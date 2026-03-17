import os
from airflow import DAG
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from generate_data import main as generate_csv_main
from etl_processor import main as etl_main
from debezium_connector import register_debezium
from dag_utils import execute_ddl, load_csv_files, task_success_log, task_failure_log

with DAG(dag_id="ecommerce_pipeline", start_date=days_ago(4), schedule_interval="@daily", catchup=False,
    template_searchpath=["/opt/airflow/sql"], tags=["ecommerce"],
    default_args={"on_success_callback": task_success_log, "on_failure_callback": task_failure_log}) as dag:

    generate_csv = PythonOperator(task_id="generate_csv", python_callable=generate_csv_main)
    
    create_schema = MySqlOperator(task_id="create_schema", mysql_conn_id="local_mysql", sql="schema.sql")
    
    create_trigger = PythonOperator(task_id="create_trigger", python_callable=execute_ddl,
        op_args=[os.path.join(os.getenv("AIRFLOW_HOME", "/opt/airflow"), "sql/trigger.sql")])
    
    create_olap_schema = PostgresOperator(task_id="create_olap_schema", postgres_conn_id="local_postgres", sql="olap_schema.sql")
    
    start_debezium = PythonOperator(task_id="start_debezium", python_callable=register_debezium)
    
    load_csv = PythonOperator(task_id="load_csv", python_callable=load_csv_files)
    
    run_etl_processor = PythonOperator(task_id="run_etl_processor", python_callable=etl_main,
        op_kwargs={"batch_mode": True, "timeout_ms": 40000})

    generate_csv >> create_schema >> create_trigger >> create_olap_schema >> start_debezium >> load_csv >> run_etl_processor
