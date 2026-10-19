import os
import mysql.connector
from dotenv import load_dotenv

# Credentials come from the .env file, never from the code.
load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
)

cur = conn.cursor()
cur.execute("SHOW TABLES;")
print(cur.fetchall())
