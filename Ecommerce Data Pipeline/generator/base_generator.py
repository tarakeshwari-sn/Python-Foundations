import os
import csv
import uuid
import random
import logging
from faker import Faker
from datetime import datetime

logger = logging.getLogger(__name__)
fake = Faker()

class EcommerceDataGenerator:
    def __init__(self, output_dir=None):
        self.output_dir = output_dir or os.getenv("DATA_DIR", "/opt/airflow/data/ecommerce_daily")
        os.makedirs(self.output_dir, exist_ok=True)
        self.customers,self.products = [], []
        self.synced_customers,self.synced_products = set(), set()
        self.payment_methods=["Credit Card", "Debit Card", "PayPal", "UPI", "Cash on Delivery"]
        self.categories=["Electronics", "Clothing", "Home", "Books", "Sports"]

    def _init_base(self, num_c, num_p):
        for _ in range(num_c):
            self.customers.append({"cid": str(uuid.uuid4()),"name": fake.name(),
                "dob": fake.date_of_birth(minimum_age=18, maximum_age=70).isoformat(),
                "country": fake.country(),"gender": random.choice(["Male", "Female", "Other"]),
                "address": fake.street_address(),"email": fake.unique.email()})
        
        for _ in range(num_p):
            self.products.append({"pid": str(uuid.uuid4()),
                "pname": f"{fake.word().capitalize()} {fake.word().capitalize()}",
                "category": random.choice(self.categories),"price": round(random.uniform(10, 1000), 2),
                "brand": fake.company(), "supplier": fake.company()})

    def generate_day(self, date_obj, num_orders=100, p_new_c=0.05, p_new_p=0.03):
        c_rows, p_rows, o_rows, pay_rows = [], [], [], []
        if random.random() < p_new_c:
            new_c = {"cid": str(uuid.uuid4()),
                     "name": fake.name(),"dob": fake.date_of_birth(minimum_age=18, maximum_age=70).isoformat(),
                     "country": fake.country(),"gender": random.choice(["Male", "Female", "Other"]),
                     "address": fake.street_address(),"email": fake.unique.email()}
            self.customers.append(new_c); c_rows.append(new_c)

        if random.random() < p_new_p:
            new_p = {"pid": str(uuid.uuid4()),
                    "pname": f"{fake.word().capitalize()} {fake.word().capitalize()}",
                    "category": random.choice(self.categories),
                    "price": round(random.uniform(10, 1000), 2),
                    "brand": fake.company(),
                    "supplier": fake.company()}
            self.products.append(new_p); p_rows.append(new_p)
        
        for _ in range(num_orders):
            oid, c, p = str(uuid.uuid4()), random.choice(self.customers), random.choice(self.products)
            qty, disc = random.randint(1, 5), round(random.uniform(0, 20), 2)
            
            if c['cid'] not in self.synced_customers: 
                c_rows.append(c)
                self.synced_customers.add(c['cid'])
            
            if p['pid'] not in self.synced_products: 
                p_rows.append(p) 
                self.synced_products.add(p['pid'])
           
            o_rows.append({"oid": oid, "cid": c["cid"], 
                           "pid": p["pid"], "quantity": qty, 
                           "discount": disc,
                            "order_date": datetime.combine(date_obj, fake.time_object()).isoformat()})
            
            pay_rows.append({"payid": str(uuid.uuid4()), "oid": oid, 
                            "amount": round((p["price"]*qty)-disc, 2), 
                            "method_payment": random.choice(self.payment_methods),
                            "provider": random.choice(["Stripe", "PayPal", "Square", "Bank"]),
                            "payment_status": random.choice(["Paid", "Pending", "Failed"]),
                            "order_status": random.choice(["Placed", "Shipped", "Cancelled"])})
        
        return {"customers": c_rows, "products": p_rows, "orders": o_rows, "payments": pay_rows}

    def save(self, data, date_obj):
        for entity, rows in data.items():
            if not rows: 
                continue
            
            fpath=os.path.join(self.output_dir, f"{entity}_{date_obj}.csv")
            with open(fpath, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=rows[0].keys())
                w.writeheader()
                w.writerows(rows)
