import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path
import sys
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

load_dotenv()
data_path=Path("data/attacks.csv")
output_dir=Path("output")
output_dir.mkdir(exist_ok=True)

JSON_OUTPUT=output_dir/"shark_attacks_cleaned.json"
raw_password = os.getenv("MYSQL_PASSWORD")

if raw_password is None:
    print("ERROR: MYSQL_PASSWORD environment variable not set.")
    sys.exit(1)

password=quote_plus(raw_password)

mysql_configG = {"user":"root","password":password,
    "host":"localhost","port":"3306",
    "database":"shark_pipeline"}

def load_data(path):
    try:
        df=pd.read_csv(path,encoding="latin1")
        print(f"Loaded {df.shape[0]} rows, {df.shape[1]} columns.")
        return df
    except Exception as e:
        print("Failed to load dataset:", e)
        sys.exit(1)

#Data Cleaning
def clean_data(df):

    df=df.copy()  
    df.columns=(df.columns.str.strip().str.lower().str.replace(" ", "_"))
    df = df.drop_duplicates().copy()

    df.loc[:,"fatal_(y/n)"]=(df["fatal_(y/n)"].astype(str).str.upper().str.strip())

    df.loc[:,"fatal_clean"]=df["fatal_(y/n)"].map({"Y": 1,"N": 0})

    df.loc[:,"age"] = pd.to_numeric(df["age"],errors="coerce")

    df.loc[:,"sex"]=(df["sex"].astype(str).str.upper().str.strip().replace({"M": "Male", "F": "Female"}))

    df.loc[:,"year"]=pd.to_numeric(df["year"],errors="coerce")

    df = df[df["year"].notna()].copy()

    print("Cleaning completed.")
    return df

#Data Transformation
def transform_data(df):

    df["age_group"]=pd.cut(df["age"],bins=[0, 12, 18, 30, 50, 100],labels=["Child", "Teen", "Young Adult", "Adult", "Senior"])

    df["decade"]=(df["year"]// 10)*10

    df["fatal_flag"]=df["fatal_clean"].fillna(0).astype(int)

    print("Transformations complete.")
    return df

#KPI Calaculations
def calculate_kpis(df):

    print("\n Key Performance Indicators of Shark Attacks")

    kpis = {"total_attacks": len(df),"total_fatalities": int(df["fatal_flag"].sum()),
        "fatality_rate_%": round((df["fatal_flag"].sum()/len(df)) * 100, 2),
        "most_affected_country": df["country"].mode()[0],
        "most_common_activity": df["activity"].mode()[0],
        "peak_decade": df["decade"].mode()[0]}

    for k,v in kpis.items():
        print(f"{k}: {v}")
    return kpis

#SQL Export
def export_to_mysql(df,config):

    try:
        connection_string = (f"mysql+mysqlconnector://{config['user']}:{config['password']}"
        f"@{config['host']}:{config['port']}/{config['database']}")

        engine=create_engine(connection_string)
        df.to_sql(name="shark_attacks",con=engine,if_exists="replace",index=False)
        print("Data exported to MySQL successfully.")

    except SQLAlchemyError as e:
        print("MySQL export failed:", e)
        sys.exit(1)

#JSON Export
def export_to_json(df, output_path):

    df.to_json(output_path,orient="records",indent=4)
    print(f"JSON exported to {output_path}")

def main():

    df=load_data(data_path)
    df=clean_data(df)
    df=transform_data(df)
    calculate_kpis(df)
    export_to_mysql(df, mysql_configG)
    export_to_json(df, JSON_OUTPUT)

    print("\nPipeline executed successfully.")

if __name__ == "__main__":
    main()
