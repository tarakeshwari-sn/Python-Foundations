import os
from datetime import datetime

log_dir="/opt/airflow/data/logs"

def log_to_run_file(run_id, task_id, message):
    safe_run_id = str(run_id).replace(":", "_").replace("+", "_")
    os.makedirs(log_dir,exist_ok=True)
    log_file=os.path.join(log_dir,f"dag_run_{safe_run_id}.log")
    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message=f"{timestamp} - [{task_id}] - {message}\n"
    
    with open(log_file,"a") as f:
        f.write(formatted_message)
