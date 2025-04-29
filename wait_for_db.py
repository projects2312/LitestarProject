import time
import psycopg2
import os

while True:
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host="db",
            port=5432,
        )
        conn.close()
        print("Database is available")
        break
    except psycopg2.OperationalError:
        print("Database unavailable, waiting 1 second...")
        time.sleep(1)