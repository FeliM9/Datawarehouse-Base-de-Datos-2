


'''
from dotenv import load_dotenv
import os

load_dotenv()

print("HOST:", os.getenv("DB_HOST"))
print("DB:", os.getenv("DB_NAME"))
print("USER:", os.getenv("DB_USER"))
'''

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os

load_dotenv()

host = os.getenv("DB_HOST")
db = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
port = os.getenv("DB_PORT")

url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"

engine = create_engine(url)

with engine.connect() as conn:
    result = conn.execute(text("SELECT version();"))
    print(result.fetchone()[0])

print("Conexion OK")