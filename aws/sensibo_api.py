# Authors: Wenhao, 2026
# Project: HEATS
# Experiment: Yanta

from typing import Optional
import datetime as dt
import requests
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, timezone

TZ = ZoneInfo("Asia/Singapore")


## Sensibo API 

def api_url(device_id: str) -> str:
    return f"https://home.sensibo.com/api/v2/pods/{device_id}"


def get_state(device_id: str, api_key: str) -> Optional[dict]:
    try:
        r = requests.get(
            f"{api_url(device_id)}/acStates",
            params={"apiKey": api_key, "limit": 1, "fields": "acState"},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()["result"][0]["acState"]
    except Exception as e:
        print(f"{datetime.now(TZ):%F %T} | ⚠️ fetch error ({device_id}): {e}")
        return None


def send_to_sensibo(device_id: str, api_key: str, *, on: bool, temp: Optional[int], fan_level: str = "auto"):
    """Send a new AC state to the Sensibo cloud."""
    payload: Dict[str, Dict] = {"acState": {"on": on}}
    if on:
        payload["acState"].update({
            "mode": "cool",
            "fanLevel": fan_level,
            "targetTemperature": temp,
            "temperatureUnit": "C",
            "swing": "stopped",
        })
    try:
        r = requests.post(
            f"{api_url(device_id)}/acStates?apiKey={api_key}",
            json=payload,
            timeout=10,
        )
        r.raise_for_status()
        print(f"{datetime.now(TZ):%F %T} | ▶️ sent {payload} to {device_id}")
    except requests.RequestException as e:
        print(f"{datetime.now(TZ):%F %T} | ⚠️ send error ({device_id}): {e}")