# Authors: Wenhao, 2026
# Project: HEATS
# Experiment: Yanta

from datetime import datetime, timezone, timedelta
import pandas as pd


def get_sleep_flag(df_cozie: pd.DataFrame, pid: str) -> int:
    """
    Check if there was a 'Going to sleep in my bedroom' event in the last 12 hours.

    Returns:
        int: 1 if such an event is found, otherwise 0.
    """
    df_part = df_cozie.query(
        "(id_participant == @pid) and "
        "(q_activity == 'Going to sleep in my bedroom')"
    )

    if df_part.empty:
        return 0

    last_ts = (
        df_part.index.max() if df_part.index.dtype.kind == "M"
        else pd.to_datetime(df_part["time"]).max()
    )
    last_ts_utc = (last_ts if last_ts.tzinfo else last_ts.replace(tzinfo=timezone.utc))
    
    print("Last watch survey data was ", datetime.now(timezone.utc) - last_ts_utc, "ago.")
    
    return int(
        datetime.now(timezone.utc) - last_ts_utc <= timedelta(hours=14)
    )