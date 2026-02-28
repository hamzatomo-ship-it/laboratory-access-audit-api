import os
import mysql.connector

conn = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cur = conn.cursor()
cur.execute("SHOW TABLES;")
print(cur.fetchall())

cur.close()
conn.close()
print("DB connection OK")
