import os
import mysql.connector

conn = mysql.connector.connect(
    host= "127.0.0.1",
    port="3306",
    user="root",
    password= "Adeyemi2025",
    database="lab_audit_db",
    )

cur = conn.cursor()
cur.execute("SHOW TABLES;")
print(cur.fetchall())

cur.close()
conn.close()
print("DB connection OK")
