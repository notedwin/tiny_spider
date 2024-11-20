from datetime import datetime, timedelta

import duckdb
import pandas as pd
import requests
import structlog
from utils import get_secret

url = "https://api.cloudflare.com/client/v4/graphql/"


def get_cf_graphql(start_date, end_date, api_token, api_account):
    assert start_date <= end_date
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}",
    }
    # The GQL query we would like to use:
    # https://pages.johnspurlock.com/graphql-schema-docs/cloudflare.html#AccountHttpRequestsOverviewAdaptiveGroupsSum
    payload = f"""{{"query":
      "query HttpDaily($accountTag: string) {{
        viewer {{
          accounts(
            filter: {{ accountTag: $accountTag }}
          ) {{
            httpRequestsOverviewAdaptiveGroups(
              limit: 40
              filter: $filter
              orderBy: [ date_DESC ]
            ) {{
              dimensions {{
                date
              }}
              sum {{
                bytes
                cachedBytes
                cachedRequests
                requests
                visits
                pageViews
              }}
            }}
          }}
        }}
      }}",
      "variables": {{
        "accountTag": "{api_account}",
        "filter": {{
          "AND":[
            {{
              "date_geq": "{start_date}"
            }},
            {{
              "date_leq": "{end_date}"
            }}
          ]
        }}
      }}
    }}"""

    r = requests.post(url, data=payload.replace("\n", ""), headers=headers)
    return r.json()


def main():
    log = structlog.get_logger()

    db_url = get_secret("LOGS_DB")
    api_token = get_secret("CF_API_TOKEN")
    api_account = get_secret("CF_ACCOUNT")

    duckdb.execute("INSTALL postgres; LOAD postgres;")
    duckdb.execute(f"ATTACH IF NOT EXISTS 'postgres:{db_url}' AS postgres")
    last_date = duckdb.execute(
        """
        SELECT MAX(date) FROM postgres.cloudflare_analytics
    """
    ).fetchone()[0]
    last_date = datetime.strptime(last_date, "%Y-%m-%d") - timedelta(days=1)
    last_date = last_date.date()

    today = datetime.utcnow().date()

    if today - last_date >= timedelta(days=30):
        log.info("Cloudflare: Data is missing for more than 90 days")
        last_date = today - timedelta(days=30)

    log.info(f"Cloudflare: Fetching data from {last_date} to {today}")

    req = get_cf_graphql(last_date, today, api_token, api_account)

    data = req["data"]["viewer"]["accounts"][0]["httpRequestsOverviewAdaptiveGroups"]

    # 1day groups for free cloudlfare account are deprecated

    df = pd.DataFrame(
        [
            {
                "Date": row["dimensions"]["date"],
                "Bytes": row["sum"]["bytes"],
                "CachedBytes": row["sum"]["cachedBytes"],
                "CachedRequests": row["sum"]["cachedRequests"],
                "EncryptedBytes": 0,
                "EncryptedRequests": 0,
                "Requests": row["sum"]["requests"],
                "PageViews": row["sum"]["pageViews"],
                "Threats": 0,
                "Uniques": 0,
            }
            for row in data
        ]
    )

    log.info(f"Cloudflare: Inserting {len(df)} rows")

    duckdb.execute(
        """
        INSERT INTO postgres.cloudflare_analytics
        SELECT * FROM df
        """
    )


if __name__ == "__main__":
    main()
