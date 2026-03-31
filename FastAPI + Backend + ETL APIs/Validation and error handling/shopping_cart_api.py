from fastapi import FastAPI,Depends,HTTPException,status,Query
from pydantic import BaseModel
from sqlalchemy import Column,Integer,String,create_engine,Float,ForeignKey
from sqlalchemy.orm import declarative_base,sessionmaker,Session,relationship
from sqlalchemy.exc import SQLAlchemyError
import os
import sys
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()
raw_user=os.getenv("user")
if not raw_user:
    print("ERROR: user environment variable not set.")
    sys.exit(1)
raw_host=os.getenv("host")
if not raw_host:
    print("ERROR: host environment variable not set.")
    sys.exit(1)
raw_password=os.getenv("MYSQL_PASSWORD")
if not raw_password:
    print("ERROR: MYSQL_PASSWORD environment variable not set.")
    sys.exit(1)
raw_port=os.getenv("port")
if not raw_port:
    print("ERROR: port environment variable not set.")
    sys.exit(1)
raw_database=os.getenv("database")
if not raw_database:
    print("ERROR: database environment variable not set.")
    sys.exit(1)

user=quote_plus(raw_user)
host=quote_plus(raw_host)
password=quote_plus(raw_password)
port=quote_plus(raw_port)
database=quote_plus(raw_database)

database_url=(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")
try:
    engine=create_engine(database_url)
except SQLAlchemyError as e:
    print("Database connection failed:", e)
    sys.exit(1)

SessionLocal=sessionmaker(bind=engine)
Base=declarative_base()
app=FastAPI()

class User(Base):
    __tablename__="users"
    id=Column(Integer, primary_key=True,index=True)
    username=Column(String(50),unique=True,index=True)
    email=Column(String(100),unique=True)
    cart_items=relationship("CartItem",back_populates="user")

class Product(Base):
    __tablename__="products"
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String(100),unique=True)
    price=Column(Float)

class CartItem(Base):
    __tablename__="cart_items"
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.id"))
    product_id=Column(Integer,ForeignKey("products.id"))
    quantity=Column(Integer)

    user=relationship("User",back_populates="cart_items")
    product=relationship("Product")

Base.metadata.create_all(bind=engine)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserSchema(BaseModel):
    id:int
    username:str
    email:str
    class Config:
        from_attributes=True

class ProductSchema(BaseModel):
    id:int
    name:str
    price:float
    class Config:
        from_attributes=True

class CartItemSchema(BaseModel):
    product_id:int
    quantity:int
    class Config:
        from_attributes=True

@app.post("/users/",response_model=UserSchema)
def create_user(id:int=Query(...,description="User ID"),
    username:str=Query(...,description="Username"),
    email:str=Query(...,description="Email"),
    db:Session=Depends(get_db)):
    user = UserSchema(id=id, username=username, email=email)

    db_user = User(id=user.id, username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/products/",response_model=ProductSchema)
def create_product(id:int=Query(..., description="Product ID"),
    name:str=Query(..., description="Product name"),
    price:float=Query(...,description="Product price"),
    db:Session=Depends(get_db)):
    product=ProductSchema(id=id, name=name, price=price)

    db_product=Product(id=product.id, name=product.name, price=product.price)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.post("/cart/{user_id}/add")
def add_to_cart(
    user_id:int,
    product_id:int=Query(..., description="Product ID"),
    quantity:int=Query(..., description="Quantity"),
    db: Session=Depends(get_db)):
    item=CartItemSchema(product_id=product_id, quantity=quantity)

    user=db.query(User).filter(User.id == user_id).first()
    product=db.query(Product).filter(Product.id == item.product_id).first()
    if not user or not product:
        raise HTTPException(status_code=404, detail="User or Product not found")

    cart_item=db.query(CartItem).filter(CartItem.user_id == user_id, 
                                        CartItem.product_id == item.product_id).first()

    if cart_item:
        cart_item.quantity+= item.quantity
    else:
        cart_item = CartItem(user_id=user_id, product_id=item.product_id, quantity=item.quantity)
        db.add(cart_item)
    db.commit()
    return {"message": f"Added {item.quantity} of {product.name} to {user.username}'s cart."}