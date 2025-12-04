import os
from dotenv import load_dotenv
import psycopg2

# Cargar variables desde .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Conectar a PostgreSQL
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cur = conn.cursor()

# Comprobar la conexión mostrando las bases de datos
cur.execute("SELECT current_database();")
databases = cur.fetchall()
print(databases)

cur.close()
conn.close()
