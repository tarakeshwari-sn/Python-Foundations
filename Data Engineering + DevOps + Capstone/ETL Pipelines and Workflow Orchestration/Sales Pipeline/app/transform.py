# app/etl.py
import pandas as pd
import glob
import os
import shutil
from app.utils.logger import get_logger
from app.config import get_engine

logger=get_logger("ETL")
base_dir=os.path.abspath("app/data")
incoming_dir=os.path.join(base_dir,"incoming")
archive_dir=os.path.join(base_dir,"archive")
processed_file=os.path.join(base_dir,"processed/transformed_sales.csv")

def transform_sales_data():
    os.makedirs(archive_dir, exist_ok=True)
    os.makedirs(os.path.dirname(processed_file), exist_ok=True)
    files=sorted(glob.glob(f"{incoming_dir}/sales_*.csv"))
    if not files:
        logger.info("No new files to process")
        return None

    existing_tx_ids=set()
    if os.path.exists(processed_file):
        df_existing=pd.read_csv(processed_file)
        existing_tx_ids=set(df_existing["TransactionID"].astype(str))

    all_data=[]
    max_tx_id=max([int(tid.replace("TX","")) for tid in existing_tx_ids],default=0)
    for file in files:
        df=pd.read_csv(file)
        df.drop_duplicates(inplace=True)
        df.dropna(inplace=True)

        new_ids=[]
        for _ in range(len(df)):
            max_tx_id+=1
            new_ids.append(f"TX{max_tx_id:06d}")
        df["TransactionID"]=new_ids
        df["Date"]=pd.to_datetime(df["Date"], format="%d-%m-%Y")
        df["Age"]=df["Age"].astype(int)
        df["Quantity"]=df["Quantity"].astype(int)
        df["Price per Unit"]=df["Price per Unit"].astype(float)

        df["Total Amount"]=df["Quantity"] * df["Price per Unit"]
        df["Quarter"]=df["Date"].dt.quarter
        df["Year"]=df["Date"].dt.year
        df["Product Category"]=df["Product Category"].str.title()

        df["Age Group"]=pd.cut(df["Age"],bins=[18,25,40,60,100],labels=["Teenager","Youth","Middle Aged","Retired"])
        df["Revenue Band"]=pd.cut(df["Total Amount"],bins=[0,100,500,10000],labels=["Low","Medium","High"])
        all_data.append(df)  
        shutil.move(file,os.path.join(archive_dir,os.path.basename(file)))
        logger.info(f"Archived {file}")

    final_df=pd.concat(all_data, ignore_index=True)
    final_df.to_csv(processed_file, index=False)
    logger.info(f"Processed {len(final_df)} records into {processed_file}")
    return final_df

def load_to_mysql(df):
    if df is None or df.empty:
        logger.info("No data to load")
        return

    engine=get_engine()
    df.to_sql("sales", engine,if_exists="append", index=False)
    logger.info(f"Loaded {len(df)} records into MySQL")