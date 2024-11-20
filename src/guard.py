from __future__ import annotations

import requests
import requests.auth
from dotenv import dotenv_values

c = dotenv_values(".env")


serv = [
    "4chan",
    "amazon",
    "amazon_streaming",
    "apple_streaming",
    "bluesky",
    "discord",
    "disneyplus",
    "ebay",
    "electronic_arts",
    "epic_games",
    "espn",
    "facebook",
    "hbomax",
    "hulu",
    "instagram",
    "linkedin",
    "minecraft",
    "netflix",
    "nintendo",
    "nvidia",
    "onlyfans",
    "paramountplus",
    "peacock_tv",
    "pinterest",
    "playstation",
    "reddit",
    "riot_games",
    "roblox",
    "rockstar_games",
    "samsung_tv_plus",
    "signal",
    "skype",
    "slack",
    "snapchat",
    "soundcloud",
    "spotify",
    "steam",
    "telegram",
    "temu",
    "tidal",
    "tinder",
    "tumblr",
    "twitch",
    "twitter",
    "youtube",
]


def block():
    update_blocked_services(serv)


def unblock():
    update_blocked_services([])


def update_blocked_services(services):
    requests.request(
        "PUT",
        "http://192.168.0.200:3003/control/blocked_services/update",
        auth=requests.auth.HTTPBasicAuth(c["user"], c["pw"]),
        json={
            "ids": services,
            "schedule": {"time_zone": "America/Chicago"},
        },
        headers={
            "Accept": "application/json, text/plain, */*",
        },
    )


def all_services() -> str:
    response = requests.request(
        "GET",
        "http://192.168.0.200:3003/control/blocked_services/all",
        auth=requests.auth.HTTPBasicAuth("notedwin", "hydroflask13"),
        headers={
            "Accept": "application/json, text/plain, */*",
        },
    )
    serv = [x["id"] for x in response.json()["blocked_services"]]
    print(serv)


if __name__ == "__main__":
    pass
