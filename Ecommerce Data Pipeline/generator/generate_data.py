import logging
from datetime import datetime
from base_generator import EcommerceDataGenerator
from run_logger_util import log_to_run_file

logger = logging.getLogger(__name__)

def main(**kwargs):
    ti = kwargs.get('ti')
    run_id, task_id = kwargs.get('run_id'), ti.task_id if ti else 'generate_csv'
    ds = kwargs.get('ds')
    dt = datetime.strptime(ds, "%Y-%m-%d").date() if ds else datetime.now().date()
    
    def log(msg):
        logger.info(msg); 
        if run_id: log_to_run_file(run_id, task_id, msg)
    
    log(f"Generating data for {dt}")
    gen = EcommerceDataGenerator()
    gen._init_base(200, 800)
    data = gen.generate_day(dt)
    gen.save(data, dt)
    log(f"Generated data for {dt}")

if __name__ == "__main__":
    main()
