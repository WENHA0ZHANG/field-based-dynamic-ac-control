# Authors: Wenhao, 2026
# Project: HEATS
# Experiment: Yanta

from datetime import datetime, timedelta, timezone
import pandas as pd
from influxdb import InfluxDBClient, DataFrameClient
from sensibo_api import *
from get_sleep_schecule import *
from db_functions import *

def dynamic_control(
    now: datetime,
    p: dict,
    flag: int,
    wake_dt: datetime,
    df_sensibo_part: pd.DataFrame,
    df_cozie: pd.DataFrame,
    cli_w: InfluxDBClient,
):
    """
    Called only when sleep_flag == 1.

      • Sleep start = last timestamp where q_activity == 'Going to sleep in my bedroom'
      • Prints current AC status
      • Computes tonight's phase schedule & target temperatures
      • Writes sleep_schedule (dedup ≤5 h) and sends AC command if needed
    """
    pid, dev, key, fan_level = p["id"], p["ID_DEVICE"], p["API_KEY"], p.get("FAN_LEVEL", "auto")
    print("################### Dynamic Control Start ########################")

    # A) Current AC state -------------------------------------------------------
    cur = get_state(dev, key)
    print(f"[{pid}] {now:%F %T} | AC: {'ON' if cur and cur.get('on') else 'OFF'} "
          f"| Current temp: {cur.get('targetTemperature') if cur else None}")

    # 1) Determine sleep_start --------------------------------------------------
    warmer_rows = df_cozie.query(
        "(id_participant == @pid) and (q_activity == 'Going to sleep in my bedroom')"
    )
    if warmer_rows.empty:
        print(f"[{pid}] No watch survey found — abort dynamic control")
        return
    sleep_start = warmer_rows.index.max()

    # 2) Phase & target temperature --------------------------------------------
    phase, need_on, tgt_temp, _ = phase_and_target(
        now, flag, wake_dt, p, sleep_start
    )

    # 3) Build tonight's schedule string ---------------------------------------
    cs_h, cs_m = map(int, p["CONTROL_START"].split(":"))
    cs_today = now.replace(hour=cs_h, minute=cs_m, second=0, microsecond=0)
    end    = wake_dt if now < wake_dt else wake_dt + timedelta(days=1)
    first  = sleep_start + (end - sleep_start) / 5
    second = sleep_start + 1 * (end - sleep_start) / 2
    schedule_str = (
        f"pre:{cs_today:%H:%M}-{sleep_start:%H:%M};"
        f"1:{sleep_start:%H:%M}-{first:%H:%M};"
        f"2:{first:%H:%M}-{second:%H:%M};"
        f"3:{second:%H:%M}-{end:%H:%M}"
    )

    # —— Print schedule —— -----------------------------------------------------
    print(f"[{pid}] Tonight’s schedule:")
    print(f"  • pre_sleep   ({p['T_WARM']}°C):   {cs_today:%H:%M} → {sleep_start:%H:%M}")
    print(f"  • sleep_first ({p['T_NEUTRAL_DYNAMIC']}°C): {sleep_start:%H:%M} → {first:%H:%M}")
    print(f"  • sleep_second({p['T_COOL']}°C):    {first:%H:%M} → {second:%H:%M}")
    print(f"  • sleep_third ({p['T_NEUTRAL']}°C): {second:%H:%M} → {end:%H:%M}")

    # 4) Deduplicate sleep_schedule (once every 12 h) ---------------------------
    if not isinstance(df_sensibo_part.index, pd.DatetimeIndex):
        if "time" in df_sensibo_part.columns:
            df_sensibo_part["time"] = pd.to_datetime(df_sensibo_part["time"], errors="coerce", utc=True)
            df_sensibo_part = df_sensibo_part.set_index("time").sort_index()
        else:
            # Convert the current index to datetime
            df_sensibo_part.index = pd.to_datetime(df_sensibo_part.index, errors="coerce", utc=True)
    
    # Check only the last 12 hours
    recent = df_sensibo_part.loc[df_sensibo_part.index >= now - timedelta(hours=12)]
    wrote_same_recently = False
    
    # Only compare if the column exists and 'recent' is not empty
    if (not recent.empty) and ("sleep_schedule" in recent.columns):
        # If schedule_str exists in the history, consider it "already written"
        wrote_same_recently = (recent["sleep_schedule"].astype(str).str.strip() == schedule_str).any()
    
    sched_to_write = None if wrote_same_recently else schedule_str

    # 5) Decide & act -----------------------------------------------------------
    needs_change = (
        not cur or
        cur.get("on") != need_on or
        (need_on and cur.get("targetTemperature") != tgt_temp)
    )
    if not needs_change:
        log_row(cli_w, pid, cur or {}, "no_change",
                tgt_temp if need_on else None, phase, flag,
                sleep_schedule=sched_to_write)
        return

    send_to_sensibo(dev, key, on=need_on, temp=tgt_temp, fan_level=fan_level)
    log_row(cli_w, pid, {"on": True}, "send",
            tgt_temp if need_on else None, phase, flag,
            sleep_schedule=sched_to_write)
    print(f"[{pid}] Command sent → {phase}, set {tgt_temp}°C")
