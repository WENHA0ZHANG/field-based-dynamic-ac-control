# Authors: Wenhao, 2026
# Project: HEATS
# Experiment: Yanta

import datetime as dt
from datetime import datetime, timedelta
from typing import Optional, Dict

# Calculate sleep phase and target temp

def phase_and_target(
    now: datetime,
    flag: int,
    wake_dt: datetime,
    temps: dict,
    sleep_start: Optional[datetime] = None,
):
    """
    Compute (phase, ac_on, target_temp) based on current time & sleep_flag.

    • flag == 0  → pre-sleep stage (T_WARM)
    • flag == 1  → sleep stage, divided into three equal parts:
        - first  : T_NEUTRAL_DYNAMIC
        - second : T_COOL
        - third  : T_NEUTRAL

    Returns:
        phase        str     one of {"pre_sleep", "sleep_first", "sleep_second", "sleep_third"}
        need_on      bool    whether AC should be on
        target_temp  int     target temperature (°C)
        sleep_start  datetime | None   actual sleep start time (for caller to record)
    """
    if flag == 0:
        return "pre_sleep", True, temps["T_WARM"], None

    # On first entry into sleep, if sleep_start is not passed from caller, use now as start
    sleep_start = sleep_start or now.replace(second=0, microsecond=0)
    end = wake_dt if now < wake_dt else wake_dt + timedelta(days=1)

    ratio = (now - sleep_start).total_seconds() / (end - sleep_start).total_seconds()
    if ratio < 1/5:
        return "sleep_first",  True, temps["T_NEUTRAL_DYNAMIC"], sleep_start
    if ratio < 1/2:
        return "sleep_second", True, temps["T_COOL"],    sleep_start
    return "sleep_third", True, temps["T_NEUTRAL"], sleep_start