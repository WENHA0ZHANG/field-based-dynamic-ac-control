# Field evaluation of dynamic bedroom air-temperature control for sleep in real homes: implementation fidelity and exploratory sleep outcomes

This repository contains the data and code for paper:

> Wenhao Zhang, Adrian Chong, Hui Zhang, Stefano Schiavon, Clayton Miller.
> *Field evaluation of dynamic bedroom air-temperature control for sleep in real homes: implementation fidelity and exploratory sleep outcomes*.
> Building and Environment.
> https://doi.org/10.1016/j.buildenv.2026.115100.

```
@article{ZHANG2026115100,
title = {Field evaluation of dynamic bedroom air-temperature control for sleep in real homes: implementation fidelity and exploratory sleep outcomes},
author = {Wenhao Zhang and Adrian Chong and Hui Zhang and Stefano Schiavon and Clayton Miller},
journal = {Building and Environment},
pages = {115100},
year = {2026},
issn = {0360-1323},
doi = {https://doi.org/10.1016/j.buildenv.2026.115100}
}
```

### Abstract
Lab-based findings suggest that a “fall–rise” temperature profile aligned with nightly thermoregulatory changes during sleep may improve sleep. However, such profiles have not yet been experimentally tested in real-world bedrooms. We built a scalable research prototype that applies a predefined night-time temperature profile to typical split-type air conditioners using an infrared smart controller. The dynamic temperature profile is set to +1 °C relative to each participant’s habitual setpoint before sleep, returned to the habitual setpoint at bedtime, then lowered to −1 °C during the early sleep period, and finally returned to the habitual setpoint during the later sleep stages. We conducted a micro-randomized trial with 18 participants in Singapore, collecting at least 30 study nights per participant, and evaluated both implementation fidelity and sleep-related outcomes. Overall, 44% of the 285 valid dynamic nights met the alignment criterion, meaning that the temperature profile achieved in the bedroom matched the target temperature profile. Nine homes were classified as aligned, while the remaining nine were not aligned. This rate was lower than we expected, showing that the target profile is often hard to achieve in real bedrooms. Under dynamic control, participants reported a stronger preference for a cooler pre-sleep environment (*p* < 0.05), while the overall sleep outcomes showed no clear intervention effects. Overall, the prototype showed that the profile could be implemented in some homes, but the 44% alignment rate represents limited implementation success and is not sufficient for reliable deployment. Future studies should focus on improving implementation fidelity through pre-deployment bedroom screening and calibration.

## Dataset overview

This dataset comes from Phase 2 of the HEATS (Heat Exposure, AcTivity, and Sleep) field study. The study ran in occupied Singapore bedrooms from August 2025 to February 2026 as a micro-randomized trial (MRT): each night was assigned with equal probability to either **dynamic control** or **baseline control**.

On dynamic nights, a predefined fall–rise air-temperature profile was applied around each participant’s habitual AC setpoint (*T*<sub>reference</sub>):

1. **Pre-sleep** (about 1 hour before typical bedtime): *T*<sub>reference</sub> + 1 °C
2. **Bedtime** (evening watch survey submitted): return to *T*<sub>reference</sub>
3. **Early sleep** (after 1/5 of planned time in bed): *T*<sub>reference</sub> − 1 °C
4. **Later sleep** (after 1/2 of planned time in bed): return to *T*<sub>reference</sub>
5. **Wake time**: AC turned off

On baseline nights, the same automation window was used, but the setpoint stayed at the habitual temperature.

The paper analysed **18 participants** (9 male, 9 female; age 24–54 years), with **627 valid nights** after protocol checks and **570 nights** after sleep-data quality control (285 baseline and 285 dynamic). A night was valid only if wearable sleep data, two daily ecological momentary assessment (EMA) surveys, and continuous bedroom sensor data were available, the participant slept in the study bedroom, and the AC was not manually overridden during the control period.

Participant IDs in this repository:

| Cohort | IDs | Role in the paper |
| --- | --- | --- |
| `vala` | `vala001`–`vala003` | First 3 homes in the 18-home sample |
| `yanta` | `yanta001`–`yanta007`, `yanta009`–`yanta016` | Remaining 15 homes (`yanta008` was not used) |

## Repository structure

```text
.
├── aws/                  # AWS Lambda prototype for nightly AC control
├── data/
│   ├── vala/
│   │   ├── raw/          # original exports
│   │   └── processed/    # analysis-ready tables
│   └── yanta/
│       ├── raw/
│       └── processed/
├── LICENSE
└── README.md
```

Each participant folder contains the same family of Parquet files (`*.parquet.gzip`):

| File | Source | Contents |
| --- | --- | --- |
| `{id}_cozie_data.parquet.gzip` | [Cozie Apple](https://cozie.app/) + Apple Watch / HealthKit | Daily evening/morning EMA surveys, sleep stages, heart rate, HRV, wrist temperature, activity |
| `{id}_atmocube_data.parquet.gzip` | Atmocube bedroom monitor (1-min) | Indoor air temperature, relative humidity, CO₂, PM, noise, light, TVOC, and related IEQ variables |
| `{id}_qualtrics_data.parquet.gzip` | Qualtrics | Onboarding, optional bi-weekly, and exit questionnaires (demographics, housing, sleep health) |
| `{id}_jitai_data.parquet.gzip` | HEATS notification / reminder system | Just-in-time messages and reminders delivered during the broader HEATS deployment |
| `{id}_all_data.parquet.gzip` | Merged (`processed/` only) | Time-aligned combination of the streams above |

Additional files:

- `data/yanta/raw/yanta_watch_survey.json` and `data/vala/raw/vala_watch_survey.json`: Cozie watch-survey schema used for the evening and morning EMAs.
- `data/yanta/raw/yanta_outdoor_pm25_data.parquet.gzip`: hourly outdoor PM2.5 by Singapore region (north, east, south, west, central).

`raw/` keeps the original database export (UTC timestamps and extra device/system metadata). `processed/` is the version intended for reuse: timestamps are converted to `Asia/Singapore`, selected identifiers are removed, and Atmocube temperature/humidity include calibrated columns (`temperature_calibrated`, `humidity_calibrated`).

## Key variables

All tables are indexed by `timestamp`. In `processed/` data the index is timezone-aware (`Asia/Singapore`).

### Bedroom environment (`*_atmocube_data`)

The paper’s implementation-fidelity analysis uses air temperature and relative humidity. Other IEQ channels are included in the files but were not the focus of the article.

| Column | Description |
| --- | --- |
| `temperature`, `humidity` | Raw Atmocube air temperature (°C) and relative humidity (%) |
| `temperature_calibrated`, `humidity_calibrated` | Calibrated temperature and humidity used for analysis |
| `co2`, `pm1.0`, `pm2.5`, `pm4.0`, `pm10`, `voc`, `ch2o` | Indoor air quality |
| `noise`, `light`, `pressure` | Bedroom noise, light, and pressure |

### Watch surveys and sleep (`*_cozie_data`)

Evening survey submission (`q_activity == "Going to sleep in my bedroom"`) was used as the bedtime marker that triggered nightly control and sleep-onset calculations. Planned wake time (`q_wake_hour`, `q_wake_minute`) set the end of the control schedule.

| Column | Description |
| --- | --- |
| `q_activity` | Survey branch: going to sleep vs. awake in the morning |
| `q_thermal_sensation_evening`, `q_thermal_preference_evening` | Pre-sleep thermal sensation and preference |
| `q_thermal_sensation_last_night`, `q_thermal_preference_last_night` | Overnight thermal sensation and preference |
| `q_sleep_quality`, `q_sleep_disturbance` | Subjective sleep quality and whether sleep was disrupted |
| `q_wake_hour`, `q_wake_minute` | Planned next-morning wake time |
| `ts_sleep_awake`, `ts_sleep_core`, `ts_sleep_deep`, `ts_sleep_REM` | Apple Watch sleep-stage segments |
| `ts_heart_rate`, `ts_HRV`, `ts_wrist_temperature` | Overnight physiology |
| `x_sleep_*` | Derived sleep indicators in the processed files |

The full question wording and response options are in the watch-survey JSON files.

### Questionnaires (`*_qualtrics_data`)

`qualtrics_survey` labels each row as `onboarding`, `bi-weekly`, or `exit`. Onboarding captured participant background, habitual AC setpoint, housing, and sleep-health scales used to characterise the sample.

### Notifications (`*_jitai_data`)

These files log HEATS platform messages (survey reminders and behaviour-change prompts). They are part of the field deployment archive; the Building and Environment paper’s main analyses use the environmental, EMA, and Apple Watch streams.

## Control prototype (`aws/`)

The IoT prototype ran on AWS Lambda. It polled Cozie survey data and Sensibo Sky status, then sent infrared AC commands according to that night’s MRT assignment.

| File | Role |
| --- | --- |
| `lambda_function.py` | Lambda entry point: nightly loop, override detection, and dispatch to dynamic or baseline control |
| `dynamic_control.py` | Fall–rise setpoint schedule on intervention nights |
| `baseline_control.py` | Constant habitual-setpoint control on baseline nights |
| `get_sleep_schecule.py` | Maps current time onto pre-sleep / early-sleep / later-sleep phases |
| `sleep_flag.py` | Detects the evening “going to sleep” survey |
| `mrt_probability.py` | Fixed 0/1 nightly randomisation table (0 = baseline, 1 = dynamic) |
| `sensibo_api.py` | Sensibo API helpers for reading AC state and sending setpoints |
| `db_functions.py` | InfluxDB read/write helpers |
| `config.py` | Deployment settings (credentials should remain placeholders) |

Replace placeholders in `config.py` before any local test. Do not commit device IDs, API keys, or database passwords.

## Loading the data

```python
import pandas as pd

df = pd.read_parquet(
    "data/yanta/processed/yanta001/yanta001_all_data.parquet.gzip"
)
print(df.index.tz)          # Asia/Singapore
print(df["source"].unique())  # cozie / atmocube / qualtrics / jitai, depending on the file
```

For most analyses, start from `processed/` rather than `raw/`. Bedroom temperature tracking is in `*_atmocube_data`; thermal comfort and sleep outcomes are in `*_cozie_data`.

The study protocol was approved by the National University of Singapore Institutional Review Board (NUS-IRB-2023-1031). Please treat participant data as confidential and do not attempt to re-identify individuals.

**Text and figures :**
[CC-BY-4.0](http://creativecommons.org/licenses/by/4.0/)
