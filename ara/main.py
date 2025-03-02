import time

import aranet4
import psycopg
from dotenv import dotenv_values

c = dotenv_values(".env")
device_mac = "F1:29:4B:C4:EA:22"


def sync():
    db_url = c["LOGS_DB"]
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """CREATE TABLE IF NOT EXISTS aranet (time TIMESTAMPTZ, co2_ppm INT, temp DECIMAL, humidity_pct INT, pressure DECIMAL)"""
            )

            current = aranet4.client.get_current_readings(device_mac)
            cur.execute(
                f"""INSERT INTO aranet
                SELECT
                    now() as time,
                    {current.co2} AS co2_ppm,
                    {current.temperature} AS temp,
                    {current.humidity} AS humidity_pct,
                    {current.pressure} AS pressure
                
                """
            )
            print(f"Inserted new aranet data: {current.co2} ppm")
            conn.commit()


if __name__ == "__main__":
    while True:
        sync()
        time.sleep(5*60)
        
