import logging
import os
import plistlib
import subprocess
from datetime import datetime
from functools import wraps

import duckdb
import requests
import structlog
from dotenv import dotenv_values
from infisical_sdk import InfisicalSDKClient

c = {}

if dotenv_values(".env"):
    c = dotenv_values(".env")
else:
    c["id"] = os.environ.get("id")
    c["secret"] = os.environ.get("secret")
    c["project_id"] = os.environ.get("project_id")

print(c)
client = InfisicalSDKClient(host="http://192.168.0.200:8080")

client.auth.universal_auth.login(
    client_id=c["id"],
    client_secret=c["secret"],
)


def get_secret(name):
    return client.secrets.get_secret_by_name(
        secret_name=name,
        project_id=c["project_id"],
        environment_slug="prod",
        secret_path="/",
    ).secret.secret_value


def task(func, hc_url):
    @wraps(func)
    def task_closure(*args, **kwargs):
        start = datetime.now()
        log.info(f"Function: {func.__name__} started at: {start}")
        try:
            requests.get(hc_url + "/start", timeout=3)
            result = func(*args, **kwargs)
        except Exception as e:
            log.exception(
                f"Function: {func.__name__} failed with error: {e}", stack_info=True
            )
            requests.get(hc_url + "/fail")
            return None
        requests.get(hc_url, timeout=3)
        end = datetime.now()
        log.info(f"Function: {func.__name__} executed in: {end - start}")
        return result

    return task_closure


structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    processors=[
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.processors.add_log_level,
        structlog.processors.UnicodeDecoder(),
        structlog.dev.ConsoleRenderer(colors=True),
    ],
)

log = structlog.get_logger()


# uv run python3 -c "from screentime import create; create()"
def create():
    # get the path of the virtualenv local to this script
    # get the path of the script create a plist file from this data
    # move this plist to the ~/Library/LaunchAgents/ directory
    # load the job
    command = [
        os.environ.get("VIRTUAL_ENV") + "/bin/python",
        os.path.realpath(__file__),
    ]
    print(command)
    s = 60 * 60 * 6  # 6 hours
    d = {
        "Label": "io.screen.thyme",
        "ProgramArguments": command,
        # ["/usr/bin/open", "-W", "/Applications/Calculator.app"],
        "RunAtLoad": True,
        "KeepAlive": True,
        "StartOnMount": True,
        "StartInterval": s,
        "ThrottleInterval": s,
        # https://apple.stackexchange.com/questions/435496/launchd-service-logs
        "StandardErrorPath": "/tmp/screen.err",
        "StandardOutPath": "/tmp/screen.out",
        "EnvironmentVariables": dict(c),
    }
    file_ = os.path.join(
        "/Users/edwinzamudio/Library/LaunchAgents/io.screen.thyme.plist"
    )
    print(f"Creating PLIST file {file_}")
    with open(file_, "wb+") as fp:
        plistlib.dump(d, fp)

    print("Loading job")
    command = f"launchctl unload -w {file_}"
    subprocess.run(command, shell=True)
    command = f"launchctl load -w {file_}"
    subprocess.run(command, shell=True)


def apple_exporter():
    """
    flow:
        get last row seen from postgres
        pull all data after last row from sqlite and insert into postgres
        update metadata with new last row

    Notes:
    When using postgres ext, it requires you use SQL syntax for it.
    ex. NOW() is only available in postgres and not duckdb
    """
    latest_row = "SELECT MAX(last_row) FROM postgres.apple_screentime_metadata;"
    last_row = duckdb.execute(latest_row).fetchone()[0]
    log.info(f"apple: adding rows after {last_row}")

    insert_new = f"""--sql
        INSERT INTO postgres.apple_screentime
        SELECT
        Z_PK as z_pk,
        ZSTREAMNAME as zstreamname,
        ZVALUESTRING as zvaluestring,
        to_timestamp(ZCREATIONDATE::DOUBLE + 978307200)  AS zcreationdate,
        to_timestamp(ZENDDATE::DOUBLE + 978307200) AS zenddate,
        to_timestamp(ZLOCALCREATIONDATE::DOUBLE + 978307200) AS zlocalcreationdate,
        to_timestamp(ZSTARTDATE::DOUBLE + 978307200) AS zstartdate
        FROM apple.zobject
        WHERE Z_PK::INT > {last_row}
        """

    duckdb.execute(insert_new)

    rows = duckdb.execute(
        f"SELECT COUNT(1) FROM apple.zobject WHERE Z_PK::INT > {last_row} LIMIT 1"
    ).fetchone()[0]
    log.info(f"apple: Inserted {rows} new rows!")

    update_metadata = """--sql
        INSERT INTO postgres.apple_screentime_metadata
        SELECT MAX(Z_PK::INT) AS last_row,
        NOW() as date
        FROM apple.zobject
        """
    duckdb.execute(update_metadata)

    last_row = duckdb.execute("SELECT MAX(Z_PK::INT) FROM apple.zobject").fetchone()[0]
    log.info(f"apple: Last row seen {last_row}, Metadata updated!")


def aw_exporter():
    latest_row = "SELECT MAX(last_row) FROM postgres.eventmodel_metadata;"
    last_row = duckdb.execute(latest_row).fetchone()[0]
    log.info(f"aw: adding rows after {last_row}")

    insert_new = f"""--sql
        INSERT INTO postgres.eventmodel
        SELECT *
        FROM aw.eventmodel
        WHERE id::int > {last_row}::int
        """
    duckdb.execute(insert_new)

    rows = duckdb.execute(
        f"SELECT COUNT(1) FROM aw.eventmodel WHERE id::int > {last_row}::int LIMIT 1"
    ).fetchone()[0]
    log.info(f"aw: Inserted {rows} new rows!")

    update_metadata = """--sql
        INSERT INTO postgres.eventmodel_metadata
        SELECT MAX(id::int) AS last_row,
        NOW() as date
        FROM aw.eventmodel
        """

    duckdb.execute(update_metadata)

    last_row = duckdb.execute("SELECT MAX(id::int) FROM aw.eventmodel").fetchone()[0]
    log.info(f"aw: Last row seen {last_row}, Metadata updated!")


if __name__ == "__main__":
    pg_url = get_secret("LOGS_DB")
    duckdb.execute(
        f"""--sql
            INSTALL postgres; LOAD postgres;
            INSTALL sqlite; LOAD sqlite;
            SET GLOBAL sqlite_all_varchar = true;
            ATTACH 'postgres:{pg_url}' as postgres;
            ATTACH 'sqlite:/Users/edwinzamudio/Library/Application Support/Knowledge/knowledgeC.db' AS apple;
            ATTACH 'sqlite:/Users/edwinzamudio/Library/Application Support/activitywatch/aw-server/peewee-sqlite.v2.db' AS aw;
        """
    )

    apple_exporter()
    aw_exporter()
