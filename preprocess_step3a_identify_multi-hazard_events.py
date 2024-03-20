# %% Imports
import pandas as pd
import numpy as np
import json
import datetime

# %% Constants
PROCESSED_EMDAT_CSV = "data/emdat_2000_2018.csv"
TIME_LAGS = [0, 91, 182, 365]  # days

# %% Load impact data
df_emdat = pd.read_csv(PROCESSED_EMDAT_CSV).set_index("Dis No")
df_emdat[["Hazard1", "Hazard2", "Hazard3"]] = df_emdat[
    ["Hazard1", "Hazard2", "Hazard3"]
]  # .fillna("")
df_emdat["Start Date"] = pd.to_datetime(df_emdat["Start Date"])
df_emdat["End Date"] = pd.to_datetime(df_emdat["End Date"])


# %%
df_spatially_overlapping_events = pd.read_csv(
    "data/df_spatially_overlapping_events.csv", sep=";", index_col=0
)

# %% temporal overlap
for TIME_LAG in TIME_LAGS:
    temporal_buffer = datetime.timedelta(days=TIME_LAG)
    df_s_t_overlapping_events = df_spatially_overlapping_events.copy(deep=True)

    for ix, row in df_s_t_overlapping_events.iterrows():
        start_event = df_emdat.loc[ix]["Start Date"]
        overlapping_events = []
        for row_element in json.loads(row["Overlapping events"]):
            start_ol_event = df_emdat.loc[row_element]["Start Date"]
            day_difference = (start_ol_event - start_event).days
            if abs(day_difference) <= TIME_LAG:
                overlapping_events.append(row_element)
        df_s_t_overlapping_events.loc[ix]["Overlapping events"] = json.dumps(
            overlapping_events
        )

    df_s_t_overlapping_events["Overlapping events"] = df_s_t_overlapping_events[
        "Overlapping events"
    ].apply(json.loads)

    df_s_t_overlapping_events["Number overlapping events"] = df_s_t_overlapping_events[
        "Overlapping events"
    ].apply(len)

    df_s_t_overlapping_events["Hazards"] = np.nan

    for ix, row in df_s_t_overlapping_events.iterrows():
        ov_events = row.loc["Overlapping events"]
        hazards = list(
            df_emdat.loc[ix, ["Hazard1", "Hazard2", "Hazard3"]].dropna().values
        )

        for ov_event in ov_events:
            hazards = hazards + list(
                df_emdat.loc[ov_event, ["Hazard1", "Hazard2", "Hazard3"]]
                .dropna()
                .values
            )

        df_s_t_overlapping_events.loc[ix, "Hazards"] = json.dumps(hazards)

    df_s_t_overlapping_events["Hazards"] = df_s_t_overlapping_events["Hazards"].apply(
        json.loads
    )

    df_s_t_overlapping_events["Number hazards"] = df_s_t_overlapping_events[
        "Hazards"
    ].apply(len)

    # df_s_t_overlapping_events.replace("[]", np.nan, inplace=True)
    df_s_t_overlapping_events.to_csv(
        "data/df_s_t_overlapping_events_" + str(TIME_LAG) + ".csv", sep=";", index=True
    )

# %%
