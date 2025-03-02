import json
import logging
import time
from datetime import datetime
from functools import wraps

import cal
import cf_export
import plug

# import guard
import requests
import schedule
import structlog

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    processors=[
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.processors.add_log_level,
        structlog.processors.UnicodeDecoder(),
        structlog.dev.ConsoleRenderer(colors=True),
    ],
)

API_KEY = "6uSF6XuorPIn_vJYy9KWp7mqkdODsVwS"  # only works from authorized IP
log = structlog.get_logger()
URL = "http://spark:8002/api/v3/checks/"

# todo set default timeout for requests, use exponential backoff for retries


class Job:
    _id_counter = 1

    def __init__(self, name, desc, interval=None, daily_time=None, fn=None):
        self.id = Job._id_counter
        Job._id_counter += 1
        self.name = name
        self.desc = desc
        self.interval = interval
        self.daily_time = daily_time  # Format: "HH:MM" (24-hour format)
        self.fn = fn

        if interval is None and daily_time is None:
            raise ValueError("Either interval or daily_time must be specified")

    def get_json(self):
        # json sent to health checks
        return json.dumps(
            {
                "name": self.name,
                "slug": self.name,
                "desc": self.desc,
                "timeout": self.interval if self.interval else 3600,
                "grace_period": 60 * 60,
                "channels": "*",
            }
        )


def heart_beat():
    log.info("Heartbeat")


def hours_to_seconds(hours):
    return hours * 60 * 60


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


def delete_all_jobs():
    r = requests.get(URL, headers={"X-Api-Key": API_KEY})
    if r.status_code != 200:
        log.error("Failed to get jobs")
        return

    r = r.json()

    for job in r["checks"]:
        job = job["update_url"].split("/")[-1]

        if job == "57ec0564-d52d-433f-8c81-a98930aae20f":  # skip evidence
            continue

        r = requests.delete(
            f"http://spark:8002/api/v3/checks/{job}", headers={"X-Api-Key": API_KEY}
        )
    log.info("Deleted all jobs")


def create_or_update_job(jobs):
    """Creates or updates job in health checks,
    schedules job and runs it once
    """
    name = jobs.name
    json = jobs.get_json()

    created = requests.post(URL, headers={"X-Api-Key": API_KEY}, data=json)

    if created.status_code not in [200, 201]:
        log.error(f"Failed to create {name}")
        return

    log.info(f"Created {name}")

    health = requests.get(URL + "?slug=" + name, headers={"X-Api-Key": API_KEY})

    ping_url = health.json()["checks"][0]["ping_url"]

    fn = task(jobs.fn, ping_url)

    if jobs.interval:
        schedule.every(jobs.interval).seconds.do(fn)
    else:
        schedule.every().day.at(jobs.daily_time).do(fn)
    fn()


if __name__ == "__main__":
    jobs = [
        Job(
            name="heart_beat",
            desc="heart_beat for scheduler",
            interval=hours_to_seconds(6),
            fn=heart_beat,
        ),
        Job(
            name="cal",
            desc="Generate contribution calendar",
            interval=hours_to_seconds(48),
            fn=cal.main,
        ),
        Job(
            name="cf_export",
            desc="Export cloudflare data",
            interval=hours_to_seconds(48),
            fn=cf_export.main,
        ),
        Job(
            name="plug_pull",
            desc="Pull power usage data from plugs",
            interval=60 * 15,
            fn=plug.pull,
        ),
        Job(
            name="plug_sync",
            desc="Sync power usage data from plugs",
            interval=hours_to_seconds(1),
            fn=plug.sync,
        ),
        # job everyday at 8Pm to check if vscode or commit has been used for more than 15 min
        # if no, notify user
        # For every hour of screentime, 5 minutes of coding would be nice
        # every morning at 9, send over last days rest heart rate, screen time
    ]

    delete_all_jobs()
    for job in jobs:
        create_or_update_job(job)

    while True:
        n = schedule.idle_seconds()
        if n is None:
            # no more jobs
            break
        elif n > 0:
            # sleep exactly the right amount of time
            log.info(f"Next job in {n} seconds")
            time.sleep(n)
        schedule.run_pending()


# hello.deploy(
#     name,
#     schedule
#     extra_packages=["duckdb"],
# )
# make a way to add jobs + package dependencies without having to modify and redeploy
