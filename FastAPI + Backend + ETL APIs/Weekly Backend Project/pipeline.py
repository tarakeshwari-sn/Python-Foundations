import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os
import logging
from datetime import datetime,timedelta
from dotenv import load_dotenv
from fastapi import FastAPI,Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from pydantic import BaseModel,Field,ConfigDict
from sqlalchemy import Integer,String, Float,create_engine
from sqlalchemy.orm import declarative_base,sessionmaker,Session,Mapped,mapped_column
from urllib.parse import quote_plus
from jose import JWTError, jwt
from passlib.context import CryptContext

load_dotenv()
user=os.getenv("user")
host=os.getenv("host")
password = os.getenv("MYSQL_PASSWORD")
port=os.getenv("port")
database=os.getenv("database")

SECRET_KEY=os.getenv("SECRET_KEY","fallback_secret")
ALGORITHM=os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
passw=quote_plus(password) if password else None

if not all([user, host, password, port, database]):
    print("ERROR: Required environment variables are not set.")
    sys.exit(1)

DATABASE_URL = f"mysql+pymysql://{user}:{passw}@{host}:{port}/{database}"
logging.basicConfig(level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("shark_api")

engine=create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal=sessionmaker(bind=engine)
Base=declarative_base()

class SharkAttack(Base):
    __tablename__ = "shark_attacks"
    number:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    year:Mapped[int] = mapped_column(Integer, nullable=False)
    country:Mapped[str] = mapped_column(String(100), nullable=False)
    activity:Mapped[str] = mapped_column(String(255), nullable=False)
    sex:Mapped[str] = mapped_column(String(20), nullable=False)
    age:Mapped[float] = mapped_column(Float, nullable=False)
    fatal_clean:Mapped[int] = mapped_column(Integer, nullable=False)
    decade:Mapped[int] = mapped_column(Integer, nullable=False)
    century:Mapped[int] = mapped_column(Integer, nullable=False)

class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    username: Mapped[str]=mapped_column(String(100), unique=True)
    hashed_password: Mapped[str]=mapped_column(String(255))

class SharkAttackBase(BaseModel):
    year: int = Field(gt=0, lt=2100)
    country: str
    activity: str
    sex: str
    age: float = Field(ge=0)
    fatal_clean: int = Field(ge=0, le=1)

class SharkAttackCreate(SharkAttackBase):
    pass

class SharkAttackUpdate(BaseModel):
    year: int |None = Field(default=None, gt=0, lt=2100)
    country: str |None = None
    activity: str |None = None
    sex: str |None = None
    age: float |None = Field(default=None, ge=0)
    fatal_clean: int |None = Field(default=None, ge=0, le=1)

class SharkAttackResponse(SharkAttackBase):
    number: int
    decade: int
    century: int
    model_config=ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    username: str
    password: str

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain, hashed):
    plain = plain.encode("utf-8")[:72].decode("utf-8",errors="ignore")
    return pwd_context.verify(plain,hashed)

def hash_password(password: str):
    password = password.encode("utf-8")[:72].decode("utf-8",errors="ignore")
    return pwd_context.hash(password)

def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY,algorithm=ALGORITHM)

def get_user(db:Session,username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db:Session,username:str,password:str):
    user=get_user(db,username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

app = FastAPI(title="Shark Attacks API")
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created.")

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register(user:UserCreate, db:Session=Depends(get_db)):
    try:
        if get_user(db, user.username):
            raise HTTPException(status_code=400, detail="Username already exists")

        new_user=User(username=user.username,hashed_password=hash_password(user.password))
        db.add(new_user)
        db.commit()
        logger.info(f"User registered: {user.username}")
        return {"message": "User created successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error:{e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm=Depends(),
          db: Session = Depends(get_db)):
    user=authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt: {form_data.username}")
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    access_token=create_access_token(data={"sub":user.username})
    logger.info(f"User logged in: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}

def calculate_time_fields(year: int):
    decade=(year // 10) * 10
    century=(year + 99) // 100
    return decade, century

data_path=Path("data/attacks.csv")
def load_data(path:Path):
    try:
        logger.info("Loading CSV dataset")
        return pd.read_csv(path,encoding="latin1")
    except Exception as e:
        logger.error(f"Dataset load failed: {e}")
        raise

def clean_data(df: pd.DataFrame):
    logger.info("Cleaning dataset")
    df=df.dropna(how="all")
    df.columns=df.columns.str.strip().str.lower().str.replace(" ", "_", regex=False)
    df=df.drop_duplicates().copy()

    required=["year","country","activity","sex","age"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df["country"]=df["country"].fillna("Unknown")
    df["activity"]=df["activity"].fillna("Unknown")
    df["sex"]=df["sex"].fillna("Unknown")

    if "fatal_(y/n)" in df.columns:
        df["fatal_(y/n)"]=df["fatal_(y/n)"].astype(str).str.upper().str.strip()
        df["fatal_clean"]=df["fatal_(y/n)"].map({"Y": 1, "N": 0}).fillna(0).astype(int)
    else:
        df["fatal_clean"] = 0

    df["age"]=df["age"].astype(str).str.extract(r"(\d+)")
    df["age"]=pd.to_numeric(df["age"],errors="coerce")
    df["age"]=df["age"].fillna(df["age"].median())

    df["year"]=pd.to_numeric(df["year"], errors="coerce")
    df = df[df["year"].notna()]
    df["year"]=df["year"].astype(int)
    return df

def transform_data(df: pd.DataFrame):
    logger.info("Transforming dataset")

    df["decade"] = (df["year"] // 10) * 10
    df["century"] = (df["year"] + 99) // 100
    return df

def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):   
    credentials_exception=HTTPException(status_code=401, detail="Invalid credentials")
    try:
        payload=jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username=payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user=get_user(db, username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/load-data")
def load_csv_to_db(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):

    df=load_data(data_path)
    df=clean_data(df)
    df=transform_data(df)
    db.query(SharkAttack).delete()
    db.commit()

    objects = [SharkAttack(year=row["year"],
            country=row["country"],activity=row["activity"],
            sex=row["sex"],age=row["age"],
            fatal_clean=row["fatal_clean"],decade=row["decade"],century=row["century"])
        for _, row in df.iterrows()]
    db.add_all(objects)
    db.commit()
    logger.info(f"{len(objects)} records loaded from CSV.")
    return {"message": f"{len(objects)} records loaded successfully."}

@app.post("/attacks", response_model=SharkAttackResponse)
def create_attack(data: SharkAttackCreate,db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):

    decade, century = calculate_time_fields(data.year)
    new_attack = SharkAttack(**data.model_dump(),decade=decade,century=century)
    db.add(new_attack)
    db.commit()
    db.refresh(new_attack)
    logger.info(f"Attack created ID={new_attack.number}")
    return new_attack

@app.get("/attacks", response_model=list[SharkAttackResponse])
def get_all_attacks(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    return db.query(SharkAttack).all()

@app.get("/attacks/{attack_id}", response_model=SharkAttackResponse)
def get_attack(attack_id: int,db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    attack = db.query(SharkAttack).filter(SharkAttack.number == attack_id).first()
    if not attack:
        raise HTTPException(status_code=404, detail="Record not found")
    return attack

@app.put("/attacks/{attack_id}", response_model=SharkAttackResponse)
def update_attack(attack_id: int,data: SharkAttackCreate,db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):

    attack = db.query(SharkAttack).filter(SharkAttack.number == attack_id).first()
    if not attack:
        raise HTTPException(status_code=404, detail="Record not found")

    for key, value in data.model_dump().items():
        setattr(attack, key, value)

    attack.decade, attack.century=calculate_time_fields(attack.year)
    db.commit()
    db.refresh(attack)
    logger.info(f"Attack updated ID={attack_id}")
    return attack


@app.patch("/attacks/{attack_id}", response_model=SharkAttackResponse)
def patch_attack(attack_id: int,data: SharkAttackUpdate,db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):

    attack = db.query(SharkAttack).filter(SharkAttack.number == attack_id).first()
    if not attack:
        raise HTTPException(status_code=404, detail="Record not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(attack, key, value)

    if "year" in update_data:
        attack.decade, attack.century=calculate_time_fields(attack.year)
    db.commit()
    db.refresh(attack)
    logger.info(f"Attack patched ID={attack_id}")
    return attack

@app.delete("/attacks/{attack_id}")
def delete_attack(attack_id: int,db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    attack = db.query(SharkAttack).filter(SharkAttack.number == attack_id).first()
    if not attack:
        raise HTTPException(status_code=404, detail="Record not found")

    db.delete(attack)
    db.commit()
    logger.info(f"Attack deleted ID={attack_id}")
    return {"message": "Attack deleted successfully"}