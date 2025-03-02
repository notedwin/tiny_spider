import duckdb
import pandas as pd
import requests
import structlog
from utils import get_secret

# if this gets more complex use mqtt

cost_per_watt = 0.15 / 1000  # 15 cents per kwh, multiply by watts to get cost

ddb = duckdb.connect("local.db")
ddb.execute(
    "CREATE TABLE IF NOT EXISTS local_plugs (time TIMESTAMPTZ, plug_id INT, power DECIMAL, voltage DECIMAL, current DECIMAL, energy_past_minute INT)"
)


def sync():
    log = structlog.get_logger()
    db_url = get_secret("LOGS_DB")
    ddb.execute("INSTALL postgres; LOAD postgres;")
    ddb.execute(f"ATTACH IF NOT EXISTS 'postgres:{db_url}' AS postgres")
    # ddb.execute(
    #     "CREATE TABLE IF NOT EXISTS postgres.plugs (time TIMESTAMPTZ, plug_id INT, power DECIMAL, voltage DECIMAL, current DECIMAL, energy_past_minute INT)"
    # )

    # get the latest date from the database
    last_date = ddb.execute(
        """
        SELECT MAX(time) FROM postgres.plugs
    """
    ).fetchone()[0]

    # last_date = "2025-01-31 18:43:47.168699-06:00"

    diff = ddb.execute(
        """
        SELECT now() - MAX(time) FROM postgres.plugs
    """
    ).fetchone()[0]

    log.info(f"Last synced on {last_date}, which is {diff} ago")

    new_data = ddb.execute(
        f"SELECT COUNT(*) FROM local_plugs WHERE time >= '{last_date}'"
    ).fetchone()[0]

    ddb.execute(
        f"""
        INSERT INTO postgres.plugs
        SELECT * FROM local_plugs WHERE time >= '{last_date}'
    """
    )
    log.info(f"Inserted {new_data} rows into postgres")


def store_power_usage(plug_id, url):
    log = structlog.get_logger()

    log.info("Fetching power usage")
    r = requests.get(url)
    data = r.json()

    df = pd.DataFrame(
        [
            {
                "plug_id": plug_id,
                "power": data["apower"],
                "voltage": data["voltage"],
                "current": data["current"],
                "energy_past_minute": data["aenergy"]["by_minute"][0],
            }
        ]
    )

    ddb.execute(
        """
        INSERT INTO local_plugs
        SELECT 
            now() as time,
            * 
        FROM df
        WHERE energy_past_minute > 35
            
        """
    )


def pull():
    plugs = ["http://192.168.0.52/rpc/Switch.GetStatus?id=0"]

    for idx, url in enumerate(plugs):
        store_power_usage(idx, url)


if __name__ == "__main__":
    pull()
    sync()
