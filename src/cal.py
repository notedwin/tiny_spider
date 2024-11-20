from datetime import datetime, timedelta

import duckdb
import pandas as pd
import requests
import structlog
from utils import get_secret

log = structlog.get_logger()
gh_url = "https://api.github.com/graphql"
lc_url = "https://leetcode.com/graphql"


def leetcode_data():
    lc_query = """query
    {
        matchedUser(username: "notedwin")
        {
            submissionCalendar
        }
    }"""
    res = requests.post(lc_url, json={"query": lc_query})
    return res.json()["data"]["matchedUser"]["submissionCalendar"]


def github_data(gh_token):
    last_date = duckdb.execute(
        """
        SELECT MAX(date) FROM postgres.contribution_calendar
    """
    ).fetchone()[0]
    last_date = datetime.strptime(last_date, "%Y-%m-%d") - timedelta(days=30)
    last_utz = last_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    now_utz = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    gh_query = """query {{
        user(login: "{0}"){{
            contributionsCollection(
                from: "{1}"
                to: "{2}"        
            ){{
                contributionCalendar{{
                    weeks{{
                        contributionDays{{
                            contributionCount
                            date
                        }}
                    }}
                }}
            }}
        }}
    }}"""

    data = {}

    for user in ["notedwin", "notedwin-hznp"]:
        q = gh_query.format(user, last_utz, now_utz)
        res = requests.post(
            gh_url,
            json={"query": q},
            headers={"Authorization": f"bearer {gh_token}"},
        )
        contribs = res.json()["data"]["user"]["contributionsCollection"][
            "contributionCalendar"
        ]["weeks"]
        for week in contribs:
            for day in week["contributionDays"]:
                date = day["date"]
                count = day["contributionCount"]
                data[date] = data.get(date, 0) + count
    return data


def main():
    gh_token = get_secret("GITHUB_API")
    db_url = get_secret("LOGS_DB")

    duckdb.execute("INSTALL postgres; LOAD postgres;")
    duckdb.execute(f"ATTACH IF NOT EXISTS 'postgres:{db_url}' AS postgres")
    contributions = {}
    log.info(f"Github: Fetching contribution calendar update {datetime.now()}")
    # data = json.loads(leetcode_data())
    # for date, count in data.items():
    #     date = datetime.fromtimestamp(int(date)).strftime("%Y-%m-%d")
    #     print(date, count)
    #     contributions[date] = count

    data = github_data(gh_token)
    for date, count in data.items():
        contributions[date] = contributions.get(date, 0) + count

    df = pd.DataFrame(contributions.items(), columns=["Date", "contributions"])

    duckdb.execute(
        """
        INSERT INTO postgres.contribution_calendar
        SELECT date, contributions FROM df
        """
    )

    log.info(f"Github: Inserted {len(data)} new rows")


if __name__ == "__main__":
    main()
