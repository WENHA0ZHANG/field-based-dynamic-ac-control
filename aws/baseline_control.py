# Authors: Wenhao, 2026
# Project: HEATS
# Experiment: Yanta

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Database credentials (InfluxDB)
DB_HOST = "XXXXXXXXX"
DB_PORT = XXXXXXXXX
DB_USER = "XXXXXXXXX"
DB_PASSWORD = "XXXXXXXXX"
DB_NAME = "XXXXXXXXX"
S3_BUCKET_NAME = 'XXXXXXXXX'

DB_HOST_W = "XXXXXXXXX"
DB_PORT_W = XXXXXXXXX
DB_USER_W = "XXXXXXXXX"
DB_PASSWORD_W = "XXXXXXXXX"
DB_NAME_W = "XXXXXXXXX" 


# Settings
ID_EXPERIMENT_READ = 'yanta'
ID_EXPERIMENT_WRITE = 'yanta'
DB_TIME_HORIZON = 4 # Number of weeks worth of data to be retrieved from database
OPERATION_HOUR_START = 19
OPERATION_HOUR_END = 14
OPERATION_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Time-zone
TZ = ZoneInfo("Asia/Singapore")        # used for all “local” prints & comparisons
YOUR_TIMEZONE = "Asia/Singapore"       # only needed for timestamp_now demo


LIST_PARTICIPANTS = [

    {
        "id": "yanta016",
        "ID_DEVICE": "XXXXXXXXX",
        "API_KEY": "XXXXXXXXX",
        "WAKE_TIME": "08:00",   # 24h
        "CONTROL_START": "22:30",
        "T_NEUTRAL": 23,
        "T_WARM": 24,
        "T_NEUTRAL_DYNAMIC": 23,
        "T_COOL": 22,
        "FAN_LEVEL": "medium",
    },
]

