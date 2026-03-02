from urllib.parse import quote_plus
import os
from dotenv import load_dotenv
import sqlalchemy
import sys

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

MYSQL_URI=f"mysql+pymysql://{user}:{passw}@{host}:{port}/{database}"
def get_engine():
    return sqlalchemy.create_engine(MYSQL_URI)