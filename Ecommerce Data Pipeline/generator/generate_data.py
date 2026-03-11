import csv
import uuid
import random
import os
import logging
from faker import Faker
from datetime import datetime,timedelta
import pandas as pd
from run_logger_util import log_to_run_file

logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

fake = Faker()
initial_customers = 200
initial_products = 800
orders_per_day = 120
max_items_per_order =8
prob_new_customer = 0.05
prob_new_product = 0.03

output_dir = os.getenv("DATA_DIR", r"/opt/airflow/data/ecommerce_daily")
os.makedirs(output_dir, exist_ok=True)

payment_methods = ["Credit Card", "Debit Card", "PayPal", "UPI", "Cash on Delivery"]
payment_statuses = ["Paid", "Pending", "Failed"]
order_statuses = ["Placed", "Shipped", "Cancelled"]
categories = ["Electronics", "Clothing", "Home", "Books", "Sports"]
customers = []

for _ in range(initial_customers):
    customers.append({"cid": str(uuid.uuid4()),"name": fake.name(),
        "dob": fake.date_of_birth(minimum_age=18, maximum_age=70).isoformat(),
        "country": fake.country(),"gender": random.choice(["Male", "Female", "Other"]),
        "address": fake.street_address(),"email": fake.unique.email()})

products = []
for _ in range(initial_products):
    products.append({
        "pid": str(uuid.uuid4()),"pname": fake.word().capitalize() + " " + fake.word().capitalize(),
        "category": random.choice(categories),"price": round(random.uniform(10, 1000), 2)})

# Track synced IDs across runs 
synced_customers = set()
synced_products = set()

def main(**kwargs):
    run_id = kwargs.get('run_id')
    task_id = kwargs.get('ti', {}).task_id if kwargs.get('ti') else 'generate_csv'
    
    def log_msg(msg,level='info'):
        if level=='info':
            logger.info(msg)
        elif level=='warning':
            logger.warning(msg)
        if run_id:
            log_to_run_file(run_id, task_id, msg)

    ds=kwargs.get('ds')
    current_date = datetime.strptime(ds, "%Y-%m-%d").date() if ds else datetime.now().date()
    log_msg(f"Running normalized data generation for {current_date}")

    try:
        customer_rows = []
        for c in customers:
            if random.random() < 0.05: 
                c['address'] = fake.street_address()
                c['email'] = fake.unique.email()
                customer_rows.append(c)
        
        if random.random()<prob_new_customer:
            new_c = {"cid": str(uuid.uuid4()), "name": fake.name(), 
                "dob": fake.date_of_birth(minimum_age=18, maximum_age=70).isoformat(),
                "country": fake.country(), "gender": random.choice(["Male", "Female", "Other"]),
                "address": fake.street_address(), "email": fake.unique.email()}
            customers.append(new_c)
            customer_rows.append(new_c)
        
        product_rows = []
        if random.random() < prob_new_product:
            new_p = {"pid": str(uuid.uuid4()), "pname": fake.word().capitalize() + " " + fake.word().capitalize(),
                "category": random.choice(categories), "price": round(random.uniform(10, 1000), 2)}
            products.append(new_p)
            product_rows.append(new_p)

        order_rows = []
        payment_rows = []
        for _ in range(orders_per_day):
            oid=str(uuid.uuid4())
            customer=random.choice(customers)
            product=random.choice(products)
            qty=random.randint(1, 5)
            amount=round((product["price"] * qty), 2)
            
            if customer['cid'] not in synced_customers:
                customer_rows.append(customer)
                synced_customers.add(customer['cid'])
            
            if product['pid'] not in synced_products:
                product_rows.append(product)
                synced_products.add(product['pid'])

            order_rows.append({"oid": oid, "cid": customer["cid"], "pid": product["pid"],
                "quantity": qty, "order_date": datetime.combine(current_date, fake.time_object()).isoformat()})
            
            payment_rows.append({"payid": str(uuid.uuid4()), "oid": oid, "amount": amount,
                "method_payment": random.choice(payment_methods),
                "payment_status": random.choice(payment_statuses),
                "order_status": random.choice(order_statuses)})

        entity_files = {"customers": customer_rows, "products": product_rows,"orders": order_rows, "payments": payment_rows}
        
        for entity, data in entity_files.items():
            if data:
                fpath=os.path.join(output_dir, f"{entity}_{current_date}.csv")
                with open(fpath, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                log_msg(f"Generated {len(data)} records for {entity} in {fpath}")
    except Exception as e:
        log_msg(f"Data Generation failed: {str(e)}", level='warning')
        raise e

if __name__ == "__main__":
    main()
