import os
import csv
import random
from datetime import datetime, timedelta
from app.utils.logger import get_logger

base_dir=os.path.abspath("app/data")
incoming_dir=os.path.join(base_dir,"incoming")
logger=get_logger("GENERATOR")
rows_per_csv=5000
num_files=2

categories=["Beauty","Electronics","Clothing","Groceries","Sports","Books"]
genders=["Male","Female"]
start_date=datetime(2023,11,24)

def generate_files():
    os.makedirs(incoming_dir,exist_ok=True)
    logger.info("Generating sales files")
    generated_files=[]
    for i in range(num_files):
        current_date=start_date + timedelta(days=i)
        date_str=current_date.strftime("%d-%m-%Y")
        file_path=os.path.join(incoming_dir,f"sales_{date_str}.csv")

        with open(file_path,"w",newline="") as f:
            writer=csv.writer(f)
            writer.writerow(["TransactionID","Date","CustomerID","Gender","Age",
                "Product Category","Quantity","Price per Unit","Total Amount"])

            for j in range(rows_per_csv):
                quantity=random.randint(1,20)
                price=random.randint(10,500)
                total=quantity * price  

                writer.writerow([j+1,
                    date_str,f"CUST{random.randint(1,9999):04d}",
                    random.choice(genders),random.randint(18,70),
                    random.choice(categories),quantity,
                    price,total])
        logger.info(f"Generated {file_path}")
        generated_files.append(file_path)
    return generated_files

if __name__=="__main__":
    generate_files()