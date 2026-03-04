# Authors: Wenhao, 2026
# Project: HEATS
# Experiment: Yanta

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Database credentials (InfluxDB)
DB_HOST = "lonepine-64d016d6.influxcloud.net"
DB_PORT = 8086
DB_USER = "Cozie-Apple-JITAI-Hwesta-Hyarmen"
DB_PASSWORD = "x!S4$+k5dr3@ymb8eRE%9Q=t"
DB_NAME = "cozie-apple"
S3_BUCKET_NAME = 'cozie-apple-jitai'

DB_HOST_W = "lonepine-64d016d6.influxcloud.net"
DB_PORT_W = 8086
DB_USER_W = "HEATS-control-lambda-function"
DB_PASSWORD_W = "jp0ky64sasdpas9iur0b5o"
DB_NAME_W = "HEATS-control" 


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
        "ID_DEVICE": "3jaAZfve",
        "API_KEY": "QnymKZc9mFWr2qRdgJF2RvkuN90Yjf",
        "WAKE_TIME": "08:00",   # 24h
        "CONTROL_START": "22:30",
        "T_NEUTRAL": 23,
        "T_WARM": 24,
        "T_NEUTRAL_DYNAMIC": 23,
        "T_COOL": 22,
        "FAN_LEVEL": "medium",
    },
]
'''
    {
        "id": "yanta014",
        "ID_DEVICE": "foS9gHUd",
        "API_KEY": "QnymKZc9mFWr2qRdgJF2RvkuN90Yjf",
        "WAKE_TIME": "05:45",   # 24h
        "CONTROL_START": "23:00",
        "T_NEUTRAL": 25,
        "T_WARM": 26,
        "T_NEUTRAL_DYNAMIC": 25,
        "T_COOL": 24,
        "FAN_LEVEL": "medium",
    },
    {
        "id": "yanta015",
        "ID_DEVICE": "jFYt9M72",
        "API_KEY": "QnymKZc9mFWr2qRdgJF2RvkuN90Yjf",
        "WAKE_TIME": "06:30",   # 24h
        "CONTROL_START": "23:00",
        "T_NEUTRAL": 22,
        "T_WARM": 23,
        "T_NEUTRAL_DYNAMIC": 22,
        "T_COOL": 21,
        "FAN_LEVEL": "medium",
    },

    {
        "id": "yanta007",
        "ID_DEVICE": "TD6zVRTR",
        "API_KEY": "QnymKZc9mFWr2qRdgJF2RvkuN90Yjf",
        "WAKE_TIME": "09:30",   # 24h
        "CONTROL_START": "23:55",
        "T_NEUTRAL": 27,        
        "T_WARM": 28,
        "T_NEUTRAL_DYNAMIC": 27,
        "T_COOL": 26,
        "FAN_LEVEL": "quiet",
    },
    {
        "id": "yanta012",
        "ID_DEVICE": "QG49DCaG",
        "API_KEY": "QnymKZc9mFWr2qRdgJF2RvkuN90Yjf",
        "WAKE_TIME": "07:00",   # 24h
        "CONTROL_START": "22:50",
        "T_NEUTRAL": 26,
        "T_WARM": 27,
        "T_NEUTRAL_DYNAMIC": 26,
        "T_COOL": 25,
        "FAN_LEVEL": "low",
    },
    {
        "id": "yanta013",
        "ID_DEVICE": "Hqmjpnqz",
        "API_KEY": "QnymKZc9mFWr2qRdgJF2RvkuN90Yjf",
        "WAKE_TIME": "08:00",   # 24h
        "CONTROL_START": "23:30",
        "T_NEUTRAL": 24,
        "T_WARM": 25,
        "T_NEUTRAL_DYNAMIC": 24,
        "T_COOL": 23,
        "FAN_LEVEL": "medium",
    },
    {
        "id": "yanta009",
        "ID_DEVICE": "3jaAZfve",
        "API_KEY": "QnymKZc9mFWr2qRdgJF2RvkuN90Yjf",
        "WAKE_TIME": "06:00",   # 24h
        "CONTROL_START": "22:45",
        "T_NEUTRAL": 27,
        "T_WARM": 28,
        "T_NEUTRAL_DYNAMIC": 27,
        "T_COOL": 26,
        "FAN_LEVEL": "low",
    },

    {
        "id": "yanta011",
        "ID_DEVICE": "K3R7tZtY",
        "API_KEY": "QnymKZc9mFWr2qRdgJF2RvkuN90Yjf",
        "WAKE_TIME": "09:30",   # 24h
        "CONTROL_START": "00:00",
        "T_NEUTRAL": 21,
        "T_WARM": 22,
        "T_NEUTRAL_DYNAMIC": 21,
        "T_COOL": 20,
        "FAN_LEVEL": "high",
    },

    {
        "id": "yanta010",
        "ID_DEVICE": "jFYt9M72",
        "API_KEY": "QnymKZc9mFWr2qRdgJF2RvkuN90Yjf",
        "WAKE_TIME": "09:00",   # 24h
        "CONTROL_START": "23:45",
        "T_NEUTRAL": 26,
        "T_WARM": 27,
        "T_NEUTRAL_DYNAMIC": 26,
        "T_COOL": 25,
        "FAN_LEVEL": "low",
    },
    {
        "id": "yanta005",
        "ID_DEVICE": "9gZFTKyk",
        "API_KEY": "QnymKZc9mFWr2qRdgJF2RvkuN90Yjf",
        "WAKE_TIME": "11:00",   # 24h
        "CONTROL_START": "00:10",
        "T_NEUTRAL": 24,
        "T_WARM": 25,
        "T_NEUTRAL_DYNAMIC": 24,
        "T_COOL": 23,
        "FAN_LEVEL": "medium",
    },
    {
        "id": "yanta014",
        "ID_DEVICE": "foS9gHUd",
        "API_KEY": "QnymKZc9mFWr2qRdgJF2RvkuN90Yjf",
        "WAKE_TIME": "05:45",   # 24h
        "CONTROL_START": "23:00",
        "T_NEUTRAL": 24,
        "T_WARM": 26,
        "T_NEUTRAL_DYNAMIC": 25,
        "T_COOL": 23,
        "FAN_LEVEL": "low",
    },

    {
        "id": "yanta004",
        "ID_DEVICE": "foS9gHUd",
        "API_KEY": "QnymKZc9mFWr2qRdgJF2RvkuN90Yjf",
        "WAKE_TIME": "06:30",   # 24h
        "CONTROL_START": "22:00",
        "T_NEUTRAL": 26,
        "T_WARM": 27,
        "T_NEUTRAL_DYNAMIC": 26,
        "T_COOL": 25,
        "FAN_LEVEL": "low",
    },
    {
        "id": "yanta011",
        "ID_DEVICE": "K3R7tZtY",
        "API_KEY": "QnymKZc9mFWr2qRdgJF2RvkuN90Yjf",
        "WAKE_TIME": "09:30",   # 24h
        "CONTROL_START": "00:00",
        "T_WARM": 22,
        "T_NEUTRAL": 21,
        "T_COOL": 20,
        "FAN_LEVEL": "high",
    },
        {
        "id": "yanta001",
        "ID_DEVICE": "QG49DCaG",
        "API_KEY": "QnymKZc9mFWr2qRdgJF2RvkuN90Yjf",
        "WAKE_TIME": "10:00",   # 24h
        "CONTROL_START": "01:00",
        "T_NEUTRAL": 27,
        "T_WARM": 28,
        "T_NEUTRAL_DYNAMIC": 27,
        "T_COOL": 26,
        "FAN_LEVEL": "medium",
    },
    
    {
        "id": "yanta006",
        "ID_DEVICE": "Hqmjpnqz",
        "API_KEY": "QnymKZc9mFWr2qRdgJF2RvkuN90Yjf",
        "WAKE_TIME": "07:30",   # 24h
        "CONTROL_START": "00:30",
        "T_NEUTRAL": 23,
        "T_WARM": 24,
        "T_NEUTRAL_DYNAMIC": 23,
        "T_COOL": 20,
        "FAN_LEVEL": "auto",
    },
'''
