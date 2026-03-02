# app/scheduler.py
import schedule
import time
from app.generator import generate_files
from app.transform import transform_sales_data, load_to_mysql
from app.utils.logger import get_logger

logger = get_logger("SCHEDULER")
def pipeline_job():
    logger.info("Pipeline started")
    generated_files=generate_files()
    logger.info(f"Generated {len(generated_files)} new files")

    df = transform_sales_data()
    load_to_mysql(df)
    logger.info("Pipeline completed")
pipeline_job()
schedule.every(3).minutes.do(pipeline_job)
logger.info("Scheduler started. Pipeline will run periodically...")
while True:
    schedule.run_pending()
    time.sleep(1)