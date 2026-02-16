from fastapi import FastAPI, Depends,HTTPException,status
from pydantic import BaseModel,ConfigDict
from sqlalchemy import Column, Integer,String,create_engine
from sqlalchemy.orm import declarative_base,sessionmaker,Session
from sqlalchemy.exc import SQLAlchemyError
import os
import sys
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()
raw_password=os.getenv("MYSQL_PASSWORD")
if not raw_password:
    print("ERROR: MYSQL_PASSWORD environment variable not set.")
    sys.exit(1)

password=quote_plus(raw_password)
DATABASE_URL=(f"mysql+pymysql://root:{password}@localhost:3306/crud_api")

try:
    engine=create_engine(DATABASE_URL,pool_pre_ping=True,echo=False)
except SQLAlchemyError as e:
    print("Database connection failed:", e)
    sys.exit(1)

SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()

class Item(Base):
    __tablename__="items"
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String(255),index=True,nullable=False)
    description=Column(String(255),nullable=False)

Base.metadata.create_all(bind=engine)
app=FastAPI()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ItemCreate(BaseModel):
    name:str
    description:str
class ItemUpdate(BaseModel):
    name:str
    description:str
class ItemResponse(BaseModel):
    id:int
    name:str
    description:str
    model_config=ConfigDict(from_attributes=True)

# CREATE
@app.post("/items/",response_model=ItemResponse,status_code=status.HTTP_201_CREATED)
def create_item(item:ItemCreate,db:Session=Depends(get_db)):
    db_item=Item(name=item.name,description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# READ (Single)
@app.get("/items/{item_id}",response_model=ItemResponse)
def read_item(item_id: int, db: Session=Depends(get_db)):
    item=db.query(Item).filter(Item.id==item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# READ (All)
@app.get("/items/",response_model=list[ItemResponse])
def read_items(db:Session=Depends(get_db)):
    return db.query(Item).all()

# UPDATE
@app.put("/items/{item_id}",response_model=ItemResponse)
def update_item(item_id: int,item:ItemUpdate,db:Session=Depends(get_db)):
    db_item = db.query(Item).filter(Item.id==item_id).first()

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db_item.name=item.name
    db_item.description=item.description
    db.commit()
    db.refresh(db_item)
    return db_item

# DELETE
@app.delete("/items/{item_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id:int,db:Session=Depends(get_db)):
    db_item = db.query(Item).filter(Item.id==item_id).first()

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(db_item)
    db.commit()
