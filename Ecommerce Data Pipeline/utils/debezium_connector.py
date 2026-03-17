import os
import time
import logging
import requests

logger = logging.getLogger(__name__)

class DebeziumConnector:
    CONNECTOR_NAME = "mysql-ecommerce-connector"

    def __init__(self):
        self.session = requests.Session()
        self.debezium_url = os.getenv("DEBEZIUM_URL", "http://debezium:8083/connectors")
        db_name = os.getenv("MYSQL_DATABASE", "ecommerce")
        kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

        self.connector_config = {
            "name": self.CONNECTOR_NAME,
            "config": {"connector.class": "io.debezium.connector.mysql.MySqlConnector",
                "database.hostname": os.getenv("MYSQL_HOST", "mysql"),
                "database.port": os.getenv("MYSQL_PORT", "3306"),
                "database.user": "root",
                "database.password": os.getenv("MYSQL_ROOT_PASSWORD", "root"),
                "database.server.id": os.getenv("DEBEZIUM_CONNECTOR_SERVER_ID", "184054"),
                "topic.prefix": "dbserver1",
                "database.include.list": db_name,
                "table.include.list": f"{db_name}.customers,{db_name}.products,{db_name}.orders,{db_name}.payments",
                "schema.history.internal.kafka.bootstrap.servers": kafka_servers,
                "schema.history.internal.kafka.topic": f"schema-changes.{db_name}",
                "include.schema.changes": "true",
                "decimal.handling.mode": "string"}}

    def register(self, snapshot_wait_seconds: int = 15):
        connector_url = f"{self.debezium_url}/{self.CONNECTOR_NAME}"
        try:
            self.session.delete(connector_url)
            logger.info(f"Deleted existing connector (if any): {self.CONNECTOR_NAME}")

            headers = {"Content-Type": "application/json"}
            response = self.session.post(self.debezium_url, headers=headers, json=self.connector_config)

            if response.status_code in (200, 201):
                logger.info(f"Debezium connector registered. Waiting {snapshot_wait_seconds}s for snapshot...")
                time.sleep(snapshot_wait_seconds)
            else:
                logger.error(f"Failed to register Debezium connector: {response.status_code} {response.text}")
                raise RuntimeError(f"Failed to register Debezium connector: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while connecting to Debezium: {e}")
            raise RuntimeError(f"Could not reach Debezium at {self.debezium_url}")
        finally:
            self.session.close()

def register_debezium():
    DebeziumConnector().register()
