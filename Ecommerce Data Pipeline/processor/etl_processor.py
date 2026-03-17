import logging
import os
from extractor import KafkaExtractor
from transformer import CDCTransformer
from loader import PostgresLoader
from run_logger_util import log_to_run_file

logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')
logger=logging.getLogger(__name__)

class ProcessorConfig:
    def __init__(self):
        self.kafka_bootstrap=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092').split(',')
        self.postgres_dsn=os.getenv('POSTGRES_DSN', 'host=localhost port=5432 dbname=ecommerce_olap user=airflow password=airflow')
        self.topic_prefix=os.getenv('TOPIC_PREFIX', 'dbserver1.ecommerce')
        self.topics=[f"{self.topic_prefix}.customers",f"{self.topic_prefix}.products",
            f"{self.topic_prefix}.orders",f"{self.topic_prefix}.payments",]

class ETLPipeline:
    def __init__(self):
        self.config=ProcessorConfig()
        self.extractor=None
        self.transformer=CDCTransformer()
        self.loader=PostgresLoader(self.config.postgres_dsn)

    def run(self,batch_mode=False,timeout_ms=5000,**kwargs):
        run_id = kwargs.get('run_id')
        task_id = kwargs.get('ti').task_id if kwargs.get('ti') else 'run_etl_processor'
        group_id = f'etl_processor_group_{run_id}' if run_id else 'etl_processor_group_default'

        def log_msg(msg,level='info'):
            getattr(logger,level)(msg)
            if run_id:
                log_to_run_file(run_id,task_id, msg)

        log_msg(f"Initializing ETL Pipeline (Batch: {batch_mode})")
        
        try:
            self.extractor=KafkaExtractor(self.config.kafka_bootstrap, self.config.topics, group_id)
            self.extractor.connect(timeout_ms=timeout_ms, batch_mode=batch_mode)
            self.loader.connect()
            
            message_count = 0
            failed_count = 0

            for message in self.extractor.consume():
                message_count += 1
                if message_count % 10 == 0:
                    log_msg(f"Processed {message_count} messages...")

                try:
                    entity_type, clean_data, op_type, payload_id = self.transformer.transform(message.topic, message.value)
                    
                    if entity_type:
                        self.loader.load(entity_type, clean_data)
                        
                        self.loader.log_reconciliation(message.topic, message.partition, message.offset,
                            payload_id, op_type, "SUCCESS")
                    
                    self.loader.commit()

                except Exception as e:
                    self.loader.rollback()
                    failed_count += 1
                    log_msg(f"Failed to process message {message_count} on {message.topic}: {e}", level='error')
                    
                    try:
                        self.loader.log_reconciliation(message.topic, message.partition, message.offset,
                            None, "ERROR", "FAILED", str(e))
                        self.loader.commit()
                    except:
                        self.loader.rollback()

            if message_count == 0:
                log_msg("No messages found.")
            log_msg(f"ETL completed. Total: {message_count}, Failed: {failed_count}")

        except Exception as e:
            log_msg(f"Fatal error in ETL pipeline: {e}", level='error')
        
        finally:
            if hasattr(self, 'loader') and self.loader:
                self.loader.close()
            if hasattr(self, 'extractor') and self.extractor:
                self.extractor.close()

def main(batch_mode=False, timeout_ms=5000, **kwargs):
    ETLPipeline().run(batch_mode=batch_mode, timeout_ms=timeout_ms, **kwargs)

if __name__ == "__main__":
    main()