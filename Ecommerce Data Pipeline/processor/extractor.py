import json
import logging
import os
from kafka import KafkaConsumer

logger = logging.getLogger(__name__)

class KafkaExtractor:    
    def __init__(self, bootstrap_servers, topics, group_id):
        self.bootstrap_servers = bootstrap_servers
        self.topics = topics
        self.group_id = group_id
        self.consumer = None

    def connect(self, timeout_ms=5000, batch_mode=False):
        self.consumer = KafkaConsumer(*self.topics,
            bootstrap_servers=self.bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m is not None else {},
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=self.group_id,
            consumer_timeout_ms=timeout_ms if batch_mode else -1)
        logger.info(f"Connected to Kafka topics: {self.topics}")

    def consume(self):
        if not self.consumer:
            raise RuntimeError("Consumer not connected. Call connect() first.")
        for message in self.consumer:
            yield message

    def close(self):
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed.")
