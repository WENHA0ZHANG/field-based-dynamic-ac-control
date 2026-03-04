# Authors: Mario, Wenhao, 2026
# Project: HEATS
# Experiment: Yanta


import os
import json
from influxdb import InfluxDBClient, DataFrameClient
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from config import *
from typing import Optional
import datetime as dt

# Read Cozie Data
def db_read_cozie(client):
    # Read Cozie data from database (settings, question flows, healthkit data)
    
    # Columns of interest
    columns = ['id_participant',
               'ws_survey_count',
               'ts_audio_exposure_environment',
               'id_onesignal',
               'q_activity',
               'q_preference_thermal',
               'ws_heart_rate',
               'location_change',
               'ws_sleep_REM',
               'ws_sleep_core',
               'ws_sleep_deep',
               'ts_step_count_phone',
               'ts_step_count_watch',
               'ws_step_count_phone',
               'ws_step_count_watch',
               'ts_workout_type',
               'ws_workout_type',
               'ts_sleep_REM', 
               'ts_sleep_core', 
               'ts_sleep_deep', 
               'ts_heart_rate',
               "q_wake_hour",
               "q_wake_minute"
               ]
    columns_str = '"' + '", "'.join(columns) + '"'
    #print(columns)
    
    # Initilize dataframe for Cozie data
    df = pd.DataFrame()

    # Query influx
    for participant in LIST_PARTICIPANTS:
      query = f'SELECT {columns_str} FROM "{DB_NAME}"."autogen"."{ID_EXPERIMENT_READ}" WHERE "time">now()-{DB_TIME_HORIZON}w AND "id_participant"=\'{participant["id"]}\''
      print("Cozie query:", query)
      result = client.query(query, epoch='ns')
      #print(result)
      try:
        df_participant = pd.DataFrame.from_dict(result[ID_EXPERIMENT_READ])
        #df = df.append(df_participant) # deprecated
        df = pd.concat([df, df_participant])
        
      # no data for that query were available
      except KeyError:
          print("DB Error:", KeyError)
    
      # Add new row for missing columns/values
      first_timestamp = pd.to_datetime('1999-02-21 00:00:00.100000+00:00')#.tz_localize('UTC')
        
      new_row = pd.DataFrame([[np.nan] * len(df.columns)], 
                             columns=df.columns, 
                            index=[first_timestamp])
      df = pd.concat([df, new_row])
      df = df.sort_index()
      
      # Add missing columns and default values (columns with no data for this participant)
      for col in columns:
          if col not in df.columns:
              # Add column
              df[col] = np.nan
              
              # Add default value
              df.loc[first_timestamp, col] = -1
              df.loc[first_timestamp, 'id_participant'] = df.iloc[-1]['id_participant']
    
    
    # Convert index to local timezone
    df.index = df.index.tz_convert(YOUR_TIMEZONE)

    return df

# Read Sensibo Data
def db_read_sensibo(client: DataFrameClient) -> pd.DataFrame:
    """Return the full yanta measurement **in Asia/Singapore time** for inspection."""
    
    # Initilize dataframe for Sensibo data
    df = pd.DataFrame()    
    #print("mario sensibo query participant list:", LIST_PARTICIPANTS)
    list_df = []
    for participant in LIST_PARTICIPANTS:
        qry = f'SELECT * FROM "{DB_NAME_W}"."autogen"."{ID_EXPERIMENT_WRITE}" WHERE "time">now()-{DB_TIME_HORIZON}w AND "id_participant"=\'{participant["id"]}\''
        print("Sensibo query:", qry)
        result = client.query(qry, epoch="ns")
        try:
            list_df.append(pd.DataFrame.from_dict(result[ID_EXPERIMENT_WRITE]))
        except KeyError:
            print("Sensibo Influx query Error:", KeyError)
    
    df = pd.concat(list_df)

    # ——— Ensure index in Asia/Singapore ———
    if df.index.dtype.kind == "M":
        if df.index.tz is None:                 # assume UTC
            df.index = df.index.tz_localize(timezone.utc)
        df.index = df.index.tz_convert(TZ)
    elif "time" in df.columns:
        df["time"] = (
            pd.to_datetime(df["time"], utc=True)
              .dt.tz_convert(TZ)
        )
        df.set_index("time", inplace=True)

    return df.sort_index()

# Write Sensibo Data to InfluxDB Log
def log_row(
    client_w: InfluxDBClient,
    participant_id: str,
    state: Optional[dict],
    action: str,
    cmd_temp: Optional[int],
    phase: str,
    flag_val: int,
    sleep_schedule: Optional[str] = None,          # NEW
):
    ts = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    json_body = [{
        "time": ts,
        "measurement": ID_EXPERIMENT_WRITE,
        "tags": {"id_participant": participant_id},
        "fields": {
            "phase":              phase,
            "sleep_flag":         flag_val,
            "acState":            state.get("on")                if state else None,
            "mode":               state.get("mode")              if state else None,
            "fanLevel":           state.get("fanLevel")          if state else None,
            "targetTemperature":  state.get("targetTemperature") if state else None,
            "commandTemperature": cmd_temp,
            "temperatureUnit":    state.get("temperatureUnit")   if state else None,
            "swing":              state.get("swing")             if state else None,
            "action":             action,
            "sleep_schedule":     sleep_schedule,                # NEW COLUMN
        }}]
    print(json_body)
    ok = client_w.write_points(json_body, database=DB_NAME_W, batch_size=5000)
    print(f"➡️  Influx write ({participant_id}):", ok)
    
    