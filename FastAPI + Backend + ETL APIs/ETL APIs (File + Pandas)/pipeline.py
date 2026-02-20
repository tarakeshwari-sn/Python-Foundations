import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Integer, String, Float, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session, Mapped, mapped_column
from urllib.parse import quote_plus

load_dotenv()
user=os.getenv("user")
host=os.getenv("host")
password=os.getenv("MYSQL_PASSWORD")
passw=quote_plus(password) if password else None
port=os.getenv("port")
database=os.getenv("database")

if not all([user,host,password,port,database]):
    print("ERROR: Required environment variables are not set.")
    sys.exit(1)

DATABASE_URL=f"mysql+pymysql://{user}:{passw}@{host}:{port}/{database}"
engine=create_engine(DATABASE_URL,pool_pre_ping=True)
SessionLocal=sessionmaker(bind=engine)
Base=declarative_base()

class SharkAttack(Base):
    __tablename__ = "shark_attacks"

    number:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    year:Mapped[int]=mapped_column(Integer,nullable=False)
    country:Mapped[str]=mapped_column(String(100),nullable=False)
    activity:Mapped[str]=mapped_column(String(255),nullable=False)
    sex:Mapped[str]=mapped_column(String(20),nullable=False)
    age: Mapped[float]=mapped_column(Float,nullable=False)
    fatal_clean: Mapped[int]=mapped_column(Integer,nullable=False)
    decade: Mapped[int]=mapped_column(Integer,nullable=False)
    century: Mapped[int]=mapped_column(Integer,nullable=False)
    
class SharkAttackBase(BaseModel):
    year:int=Field(gt=0, lt=2100)
    country:str
    activity:str
    sex:str
    age:float=Field(ge=0)
    fatal_clean:int=Field(ge=0,le=1)

class SharkAttackCreate(SharkAttackBase):
    pass

class SharkAttackUpdate(BaseModel):
    year: int|None = Field(default=None,gt=0,lt=2100)
    country: str|None=None
    activity: str|None=None
    sex: str|None = None
    age: float|None=Field(default=None,ge=0)
    fatal_clean:int|None=Field(default=None, ge=0, le=1)

class SharkAttackResponse(SharkAttackBase):
    number:int
    decade:int
    century:int
    model_config=ConfigDict(from_attributes=True)

app=FastAPI(title="Shark Attacks API")
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

def calculate_time_fields(year:int):
    year=int(year)
    decade=(year//10) * 10
    century=(year+99)//100
    return decade,century

data_path=Path("data/attacks.csv")
output_dir=Path("output")
output_dir.mkdir(exist_ok=True)
JSON_OUTPUT=output_dir / "shark_attacks_cleaned.json"

def load_data(path:Path):
    try:
        return pd.read_csv(path,encoding="latin1")
    except Exception as e:
        print("Dataset load failed:", e)
        sys.exit(1)

def clean_data(df:pd.DataFrame):

    df=df.dropna(how="all")
    df.columns=df.columns.str.strip().str.lower().str.replace(" ", "_", regex=False)
    df=df.drop_duplicates().copy()

    required=["year","country","activity","sex","age"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    cat_cols=["country","activity","sex"]
    for col in cat_cols:
        df[col]=(df[col].astype(str).str.strip().replace(["", "nan", "NaN"],np.nan).fillna("Unknown"))

    if "fatal_(y/n)" in df.columns:
        df["fatal_(y/n)"]=df["fatal_(y/n)"].astype(str).str.upper().str.strip()
        df["fatal_clean"]=df["fatal_(y/n)"].map({"Y":1, "N":0}).fillna(0).astype(int)
    else:
        df["fatal_clean"] = 0

    df["age"]=df["age"].astype(str).str.extract(r"(\d+)")
    df["age"]=pd.to_numeric(df["age"],errors="coerce")
    median_age=df["age"].median()
    df["age"]=df["age"].fillna(median_age if not pd.isna(median_age) else 0)

    df["year"]=pd.to_numeric(df["year"],errors="coerce")
    df=df[df["year"].notna()]
    df=df[df["year"]>0]
    df=df.reset_index(drop=True)
    return df

def transform_data(df:pd.DataFrame):

    df["year"]=df["year"].astype(int)
    df["decade"]=(df["year"]//10) * 10
    df["century"]=(df["year"]+99) // 100
    df["fatal_clean"]=df["fatal_clean"].fillna(0).astype(int)
    return df

@app.post("/load-data")
def run_pipeline(db:Session = Depends(get_db)):

    df=load_data(data_path)
    df=clean_data(df)
    df=transform_data(df)

    expected_cols=["year","country", "activity","sex","age","fatal_clean","decade","century"]
    df=df[expected_cols]

    db.query(SharkAttack).delete()
    db.commit()
    objects = [SharkAttack(
            year=row["year"],country=row["country"],activity=row["activity"],
            sex=row["sex"],age=row["age"],fatal_clean=row["fatal_clean"],decade=row["decade"],century=row["century"])
            for _, row in df.iterrows()]
    if objects:
        db.add_all(objects)
        db.commit()
        return {"message": f"{len(objects)} records loaded successfully."}
    return {"message":"No records to load."}

@app.post("/attacks", response_model=SharkAttackResponse)
def create_attack(data: SharkAttackCreate, db: Session = Depends(get_db)):

    decade,century=calculate_time_fields(data.year)
    attack_data = data.model_dump()
    new_attack = SharkAttack(year=attack_data["year"],country=attack_data["country"],activity=attack_data["activity"],
                sex=attack_data["sex"],age=attack_data["age"],fatal_clean=attack_data["fatal_clean"],decade=decade,
                century=century)
    db.add(new_attack)
    db.commit()
    db.refresh(new_attack)
    return new_attack

@app.get("/attacks",response_model=list[SharkAttackResponse])
def get_all_attacks(db:Session=Depends(get_db)):
    return db.query(SharkAttack).all()

@app.get("/attacks/{attack_id}",response_model=SharkAttackResponse)
def get_attack(attack_id:int,db:Session=Depends(get_db)):

    attack=db.query(SharkAttack).filter(SharkAttack.number==attack_id).first()
    if not attack:
        raise HTTPException(status_code=404,detail="Record not found")
    return attack

@app.put("/attacks/{attack_id}",response_model=SharkAttackResponse)
def update_attack(attack_id:int,data:SharkAttackCreate,db:Session=Depends(get_db)):

    attack=db.query(SharkAttack).filter(SharkAttack.number==attack_id).first()
    if not attack:
        raise HTTPException(status_code=404, detail="Record not found")

    for key,value in data.model_dump().items():
        setattr(attack, key, value)
    attack.decade, attack.century = calculate_time_fields(attack.year)
    db.commit()
    db.refresh(attack)
    return attack

@app.patch("/attacks/{attack_id}", response_model=SharkAttackResponse)
def patch_attack(attack_id:int, data:SharkAttackUpdate, db:Session=Depends(get_db)):

    attack=db.query(SharkAttack).filter(SharkAttack.number == attack_id).first()
    if not attack:
        raise HTTPException(status_code=404, detail="Attack not found")
    update_data=data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(attack, key, value)
    if "year" in update_data:
        attack.decade,attack.century=calculate_time_fields(attack.year)
    db.commit()
    db.refresh(attack)
    return attack

@app.delete("/attacks/{attack_id}")
def delete_attack(attack_id:int, db:Session=Depends(get_db)):

    attack=db.query(SharkAttack).filter(SharkAttack.number == attack_id).first()
    if not attack:
        raise HTTPException(status_code=404, detail="Attack not found")
    db.delete(attack)
    db.commit()
    return {"message": "Attack deleted successfully"}

def calculate_kpis(df: pd.DataFrame):

    total_attacks = len(df)
    total_fatalities = int(df["fatal_clean"].sum())
    fatality_rate = round((total_fatalities / total_attacks) * 100, 2) if total_attacks else 0
    return {
        "total_attacks": total_attacks,
        "total_fatalities": total_fatalities,
        "fatality_rate_%": fatality_rate,
        "most_affected_country": df["country"].mode().iloc[0] if not df["country"].mode().empty else None,
        "most_common_activity": df["activity"].mode().iloc[0] if not df["activity"].mode().empty else None,
        "peak_decade": df["decade"].mode().iloc[0] if not df["decade"].mode().empty else None
    }

def export_to_json(df:pd.DataFrame,output_path: Path):
    df.to_json(output_path,orient="records", indent=4)
    df.to_csv(output_dir/"shark_attacks_cleaned.csv", index=False)

def main():
    df=load_data(data_path)
    df=clean_data(df)
    df=transform_data(df)
    calculate_kpis(df)
    export_to_json(df,JSON_OUTPUT)

if __name__ == "__main__":
    main()