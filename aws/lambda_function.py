# Authors: Mario, Wenhao, 2026
# Project: HEATS
# Experiment: Yanta

import json
import pandas as pd
from influxdb import InfluxDBClient, DataFrameClient
import pytz
import requests
import os
import time
import datetime as dt
#import schedule
from typing import Optional
from datetime import timedelta
from zoneinfo import ZoneInfo
from db_functions import *
from config import *
from sensibo_api import *
from sleep_flag import *
from get_sleep_schecule import *
from dynamic_control import *
from baseline_control import *
from mrt_probability import *

# ═════ Lambda Entry-Point ═══════════════════════════════════════════════
def lambda_handler(event, context):
    """
    Run the multi-user control loop once.

    • Detects user_off / user_change events that occurred in the past 12 h (deduplicated).  
    • Only the first detected override of each type is taken into account;
      subsequent duplicates are logged as *_recorded.  
    • A manual power toggle (on ⇄ off) counts as an override whenever the
      current AC state differs from the last command we sent.
    """
    now = datetime.now(TZ)
    print("════ Multi-User Sensibo Lambda START ════")

    # ── 1) Initialise InfluxDB Clients ──────────────────────────────────
    cli_r = DataFrameClient(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME,
                            ssl=True, verify_ssl=True)
    cli_w = InfluxDBClient(DB_HOST_W, DB_PORT_W, DB_USER_W, DB_PASSWORD_W,
                           DB_NAME_W, ssl=True, verify_ssl=True)

    df_cozie   = db_read_cozie(cli_r)
    df_sensibo = db_read_sensibo(cli_w)
    df_sensibo["id_participant"] = (df_sensibo["id_participant"].astype(str).str.strip())

    # ── 2) Weekend / Off-Hours Guard ────────────────────────────────────
    weekday_name = now.strftime("%A")
    is_workday   = weekday_name in OPERATION_DAYS
    is_op_hour   = (now.hour >= OPERATION_HOUR_START) or (now.hour < OPERATION_HOUR_END)

    if not is_workday or not is_op_hour:
        reason = "weekend_non_operational" if not is_workday else "daily_non_operational"
        for p in LIST_PARTICIPANTS:
            pid, dev, key = p["id"], p["ID_DEVICE"], p["API_KEY"]
            cur = get_state(dev, key)               # Query only
            # Log current state; action is “no_action” to indicate monitoring-only
            log_row(cli_w, pid, cur or {}, "no_action (non_operational)", None, reason, 0)

        msg = f"{reason.replace('_', ' ').title()} – monitoring only, no control sent"
        print(msg)
        print("✅ Lambda run complete")
        return {"statusCode": 200,
                "body": json.dumps(msg)}

    # ── 3) Loop Over Participants ───────────────────────────────────────
    for i, p in enumerate(LIST_PARTICIPANTS):
        
        if i > 0:
            print("⏳ Cooling down 5s to prevent Sensibo too many requests ...")
            time.sleep(10)
        
        pid, dev, key, fan_level = p["id"], p["ID_DEVICE"], p["API_KEY"], p.get("FAN_LEVEL", "auto")
        print(f"###################### Participant {pid} ######################")

        # 3.1  Derive Key Timestamps ────────────────────────────────────
        cs_h, cs_m      = map(int, p["CONTROL_START"].split(":"))

        # Read q_wake_hour / q_wake_minute from df_cozie (for this participant)
        df_part_cozie = (
            df_cozie.query("id_participant == @pid") if not df_cozie.empty else pd.DataFrame()
        )
        
        def _last_int(series):
            """Take the last non-null value and convert it to int; raise ValueError if it fails."""
            val = series.dropna().iloc[-1]
            return int(str(val).strip())
        
        use_df_time = False
        wake_h = wake_m = None
        
        if not df_part_cozie.empty and ("q_wake_hour" in df_part_cozie.columns) and ("q_wake_minute" in df_part_cozie.columns):
            try:
                # The last (most recent) entry
                hour_series = df_part_cozie["q_wake_hour"]
                minute_series = df_part_cozie["q_wake_minute"]
        
                # Only use if both columns have at least one non-null value
                if not hour_series.dropna().empty and not minute_series.dropna().empty:
                    wake_h = _last_int(hour_series)
                    wake_m = _last_int(minute_series)
        
                    # Basic range validation
                    if 0 <= wake_h <= 23 and 0 <= wake_m <= 59:
                        use_df_time = True
            except Exception:
                use_df_time = False  # On any exception, fall back
        
        if not use_df_time:
            # Fallback logic
            wake_h, wake_m = map(int, p["WAKE_TIME"].split(":"))

    
        wake_dt = now.replace(hour=wake_h, minute=wake_m, second=0, microsecond=0)
        #wake_h, wake_m  = map(int, p["WAKE_TIME"].split(":"))
        #wake_dt         = now.replace(hour=wake_h, minute=wake_m, second=0, microsecond=0)
        # —— operation start (may be yesterday if now < 19:00) ——
        if now.hour >= OPERATION_HOUR_START:
            op_start_today = now.replace(hour=OPERATION_HOUR_START, minute=0, second=0, microsecond=0)
        else:
            op_start_today = (now - timedelta(days=1)).replace(
                hour=OPERATION_HOUR_START, minute=0, second=0, microsecond=0
            )
        
        # —— control-start: next occurrence of CONTROL_START after op_start_today ——
        cs_today = op_start_today.replace(hour=cs_h, minute=cs_m)
        if cs_today <= op_start_today:
            cs_today += timedelta(days=1)
            
        op_end_today = now.replace(hour=OPERATION_HOUR_END,   minute=0, second=0, microsecond=0)

        
        print("• Operation_start_today :", op_start_today)
        print("• Control_start_today       :", cs_today)
        print("• Control_end_today       :", wake_dt)        
        print("• Operation_end_today       :", op_end_today)

        # Decide strategy from the fixed MRT table
        mrt_today = get_mrt_value(now)          # 0 or 1, 15 :00 cut-off handled inside
        print("• MRT condition today (0 - baseline control; 1 - dynamic control):", mrt_today)

        # 3.2  Load Historical Data ─────────────────────────────────────
        #print('mario: pid:', pid)
        #print('mario: unique:', df_sensibo['id_participant'].unique())
        #print('mario: head:', df_sensibo.head(20))
        df_part_sensibo = (df_sensibo[df_sensibo["id_participant"] == pid].copy() if not df_sensibo.empty else pd.DataFrame())
        
        df_part_cozie = (
            df_cozie.query("id_participant == @pid") if not df_cozie.empty else pd.DataFrame()
        )
        
        # 3.3  Read Current AC State ────────────────────────────────────
        cur = get_state(dev, key)

        # 3.4  Pre-Control Guard: Before CONTROL_START ─────────────────
        if op_start_today < now < cs_today:
            log_row(cli_w, pid, cur or {}, "no_action (status_log)",
                    None, "before_control_start", 0)          # action changed to status_log
            print("monitor only (before CONTROL_START)")
            continue

        # 3.5  Wake-Time Shutdown (0-5 min After WAKE_TIME) ───────────
        wake_shutdown_end = wake_dt + timedelta(minutes=5)
        if wake_dt <= now < wake_shutdown_end:
            if cur and cur.get("on"):
                send_to_sensibo(dev, key, on=False, temp=None, fan_level=fan_level)
            log_row(cli_w, pid, cur or {}, "shutdown",
                    None, "wake_shutdown", 0)
            print("shutdown (0-5 min after WAKE_TIME)")
            continue

        # 3.6  Post-Wake Monitoring (5 min → OPERATION_END) ───────────
        if wake_shutdown_end <= now < op_end_today:
            log_row(cli_w, pid, cur or {}, "no_action (status_log)",
                    None, "after_wake_monitor", 0)        # monitor only, no control
            print("monitor only (5 min-OP_END after WAKE_TIME)")
            continue

        # 4) Pre-Sleep Logic (flag == 0, Not Yet Asleep) ───────────────

        flag = get_sleep_flag(df_part_cozie, pid)
        print("sleep_flag:", flag)

        # 4.1  Define Pre-Sleep Control Start Window ───────────────────
        presleep_start = cs_today
        presleep_end   = cs_today + timedelta(minutes=10)

        cur_on  = bool(cur and cur.get("on"))
        cur_tmp = cur.get("targetTemperature") if cur else None

        # 4.2  Check Last Pre-Sleep Command to Avoid Duplicates ───────
        pre_send_q  = df_part_sensibo.query(
            "(phase == 'pre_sleep_control') and (action == 'send')" #and (index >= @presleep_start)
        )

        last_pre_send = pre_send_q.iloc[-1:]  # May be empty
        #print("presleep_start", presleep_start)   
        #print("pre_send_q", pre_send_q)
        #print("last_pre_send", last_pre_send)
        
        # 4.2.1  First 10 min of Pre-Sleep Window ─────────────────────
        if presleep_start <= now < presleep_end and flag == 0:
            # choose target temperature based on mrt_today
            if mrt_today == 1:
                target_temp = p["T_WARM"]
            else:
                target_temp = p["T_NEUTRAL"]
        
            needs_change = (
                not cur_on or
                (cur_tmp != target_temp)
            )
        
            if needs_change:  # and last_pre_send.empty:
                # First time we need to send command
                send_to_sensibo(dev, key, on=True, temp=target_temp, fan_level=fan_level)
                log_row(cli_w, pid, {"on": True},
                        "send", target_temp, "pre_sleep_control", flag)
                print(f"send pre-sleep command: set T = {target_temp}")
            else:
                log_row(cli_w, pid, cur or {},
                        "no_action (command_sent)", target_temp, "pre_sleep_control", flag)
                print("pre-sleep command was sent, no change needed")
        
            continue  # Next participant

        # 5) Handle User Overrides (Look-Back 12 h) ───────────────────
        skip_auto = False
        if not df_part_sensibo.empty:
            last_send_df = df_part_sensibo.query("action == 'send'")
            if not last_send_df.empty:
                last_send  = last_send_df.iloc[-1]
                last_send_time = last_send.name
                after_send = df_part_sensibo[df_part_sensibo.index > last_send.name]
                
                # 5.A  Inspect Current Override and Log --------------
                override_time = None
                if (now - last_send.name) <= timedelta(hours=12):
                    last_on  = bool(last_send.get("acState"))
                    cur_on   = bool(cur and cur.get("on"))
                    
                    last_cmd = (
                        last_send.get("commandTemperature")
                        if pd.notna(last_send.get("commandTemperature"))
                        else last_send.get("targetTemperature")
                    )
                    last_phase = last_send.get("phase", "unknown")
                    print(f"Current targetTemperature = {cur.get('targetTemperature')} | Last commandTemperature = {last_cmd}")


                    # → Manual Power Toggle (on ⇄ off)
                    if cur_on != last_on:
                        if not cur_on:  # on → off
                            already_logged = not after_send.query("action == 'user_off'").empty
                            action_name    = "user_off_recorded" if already_logged else "user_off"
                            log_row(cli_w, pid, cur or {}, action_name, None,
                                    last_phase, 0, sleep_schedule=None)
                            if not already_logged:
                                override_time = now
                                print("» Detected *current* user_off – recorded")
                            else:
                                print("» Duplicate user_off – logged as user_off_recorded")
                        '''
                        else:          # off → on (optional log, no override trigger)
                            already_logged = not after_send.query("action == 'user_on'").empty
                            action_name    = "user_on_recorded" if already_logged else "user_on"
                            log_row(cli_w, pid, cur or {}, action_name, None,
                                    last_phase, 0, sleep_schedule=None)
                            if not already_logged:
                                print("» Detected *current* user_on – recorded")
                            else:
                                print("» Duplicate user_on – logged as user_on_recorded")
                        '''
                        
                    # → Manual Temperature Change (AC must be on)
                    elif cur_on and last_cmd is not None and cur.get("targetTemperature") != last_cmd:
                        already_logged = not after_send.query("action == 'user_change'").empty
                        action_name    = "user_change_recorded" if already_logged else "user_change"
                        log_row(cli_w, pid, cur or {}, action_name,
                                cur.get("targetTemperature"), last_phase, 0,
                                sleep_schedule=None)
                        if not already_logged:
                            override_time = now
                            print("» Detected *current* user_change – recorded")
                        else:
                            print("» Duplicate user_change – logged as user_change_recorded")

                # 5.B  Consolidate First Override Timestamp ----------
                last_off = after_send.query("action == 'user_off'").iloc[-1:]   # May be empty
                last_chg = after_send.query("action == 'user_change'").iloc[-1:] # May be empty
                cand_times = [t.index[0] for t in (last_off, last_chg) if not t.empty]
                if override_time:   # New override detected this run
                    cand_times.append(override_time)
                latest_user_action_time = max(cand_times) if cand_times else None

                # 5.C  Retrieve Latest Watch Survey -------------------
                last_survey = (
                    df_part_cozie.query("q_activity == 'Going to sleep in my bedroom'").iloc[-1:]
                    if not df_part_cozie.empty else pd.DataFrame()
                )
                last_survey_time = last_survey.index[0] if not last_survey.empty else None

                # Print Timestamps ------------------------------------
                print("   ↪ last send command to Sensibo :", last_send_time.strftime('%F %T'))
                print("   ↪ last watch survey            :", 
                      last_survey_time.strftime('%F %T') if last_survey_time else "None")
                print("   ↪ last user_off                :", 
                      last_off.index[0].strftime('%F %T') if not last_off.empty else "None")
                print("   ↪ last user_change             :", 
                      last_chg.index[0].strftime('%F %T') if not last_chg.empty else "None")

                # 5.D  Decide Whether to Skip Auto-Control ------------
                override_recent = (
                    latest_user_action_time is not None and
                    (now - latest_user_action_time) <= timedelta(hours=12)
                )
                if override_recent:
                    if (last_survey_time is not None) and (last_survey_time > latest_user_action_time):
                        print("   ↪ Watch survey newer than first override – ignore override")
                    else:
                        print("» Skip auto-control due to override (≤ 12 h)")
                        skip_auto = True

        if skip_auto:
            continue

        # 6) Active Control Phase ──────────────────────────────────────

        # 6.A  Dynamic Control While Sleeping (flag == 1) --------------
        if flag == 1:
            print("################### AC Control Start ########################")
            if mrt_today == 1:
                # Use full dynamic, multi-phase control
                dynamic_control(
                    now, p, flag, wake_dt,
                    df_part_sensibo, df_part_cozie, cli_w
                )
            else:
                # Use baseline constant-setpoint control
                baseline_control(
                    now, p, flag, wake_dt, 
                    df_part_sensibo, df_part_cozie, cli_w
                )
        
            continue   # Processing for this participant done

        # 6.B  Post-Pre-Sleep Monitoring (After 10 min, No Action) -----
        action_name = "no_action (status_log)"            # Default: log only
        if not last_pre_send.empty:
            last_pre   = last_pre_send.iloc[-1]
            last_on    = bool(last_pre.get("acState"))
            last_temp  = (
                last_pre.get("commandTemperature")
                if pd.notna(last_pre.get("commandTemperature"))
                else last_pre.get("targetTemperature")
            )

            if last_on and not cur_on:
                action_name = "user_off_presleep"
            elif cur_on and last_temp is not None and cur_tmp != last_temp:
                action_name = "user_change_presleep"

        log_row(cli_w, pid, cur or {}, action_name, cur_tmp, "pre_sleep_monitor", flag)
        print("pre-sleep monitor:", action_name)

    # Loop Ends ─────────────────────────────────────────────────────────
    print("✅ Lambda run complete")
    return {"statusCode": 200,
            "body": json.dumps("All participants processed")}
