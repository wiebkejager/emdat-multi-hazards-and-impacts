# %% Imports
import pandas as pd
import numpy as np
import json
import itertools
import datetime

# %% Constants
PROCESSED_IMPACT_PATH_CSV = "data/impact_2000_2018.csv"
TIME_LAG = 182  # days

# %% Load impact data
df_impact = pd.read_csv(PROCESSED_IMPACT_PATH_CSV, sep=";", index_col=0).set_index(
    "Dis No"
)
df_impact[["Hazard1", "Hazard2", "Hazard3"]] = df_impact[
    ["Hazard1", "Hazard2", "Hazard3"]
].fillna("")
df_impact["Start Date"] = pd.to_datetime(df_impact["Start Date"])
df_impact["End Date"] = pd.to_datetime(df_impact["End Date"])


# %%
df_spatially_overlapping_events = pd.read_csv(
    "data/df_spatially_overlapping_events.csv", sep=";", index_col=0
)

# %% temporal overlap
temporal_buffer = datetime.timedelta(days=TIME_LAG)
df_s_t_overlapping_events = df_spatially_overlapping_events.copy(deep=True)

# %%
for ix, row in df_s_t_overlapping_events.iterrows():
    start_event = df_impact.loc[ix]["Start Date"]
    overlapping_events = []
    for row_element in json.loads(row["Overlapping events"]):
        start_ol_event = df_impact.loc[row_element]["Start Date"]
        day_difference = (start_ol_event - start_event).days
        if abs(day_difference) < TIME_LAG:
            overlapping_events.append(row_element)
    df_s_t_overlapping_events.loc[ix]["Overlapping events"] = json.dumps(
        overlapping_events
    )


# %%
df_s_t_overlapping_events.replace("[]", np.nan, inplace=True)
df_s_t_overlapping_events.to_csv("data/df_s_t_overlapping_events.csv", sep=";")
df_s_t_overlapping_events.dropna(inplace=True)


# %%
cols = [
    "Dis No 1",
    "Dis No 2",
    "Hazard 1",
    "Hazard 2",
    "Start Date 1",
    "End Date 1",
    "Start Date 2",
    "End Date 2",
    "Country 1",
    "Continent 1",
    "Country 2",
    "Continent 2",
    "Magnitude 1",
    "Magnitude 2",
    "Total Deaths 1",
    "Total Deaths 2",
    "Total Deaths 12",
    "Total Affected 1",
    "Total Affected 2",
    "Total Affected 12",
    "Total Damages 1",
    "Total Damages 2",
    "Total Damages 12",
    "Number Hazards",
    "Type Event",
    "Type Hazards",
    "Number Types",
]

df = pd.DataFrame(
    columns=cols,
)


# %%
def create_new_row() -> pd.DataFrame:
    return pd.DataFrame(
        [
            [
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
            ]
        ],
        columns=cols,
    )


# %%
for ix, row in df_impact.iterrows():
    # disaster does not have spatial overlap
    if ix not in df_s_t_overlapping_events.index:
        hazards = [row["Hazard1"], row["Hazard2"], row["Hazard3"]]
        hazards = sorted([hazard for hazard in hazards if hazard != ""])

        new_row = create_new_row()
        new_row["Dis No 1"] = ix
        new_row["Hazard 1"] = row["Hazard1"]
        new_row["Hazard 2"] = row["Hazard2"]
        new_row["Start Date 1"] = row["Start Date"]
        new_row["End Date 1"] = row["End Date"]
        new_row["Country 1"] = row["Country"]
        new_row["Continent 1"] = row["Continent"]
        new_row["Dis Mag Value 1"] = row["Dis Mag Value"]
        new_row["Number Hazards"] = 3
        new_row["Type Event"] = "Compound"
        new_row["Type Hazards"] = ", ".join(hazards)
        new_row["Number Types"] = len(hazards)

        # if is single hazard
        if (row["Hazard2"] == "") & (row["Hazard3"] == ""):
            new_row["Total Deaths 1"] = row["Total Deaths"]
            new_row["Total Affected 1"] = row["Total Affected"]
            new_row["Total Damages 1"] = row["Total Damages, Adjusted ('000 US$')"]
            new_row["Number Hazards"] = 1
            new_row["Type Event"] = "Single"

        # if is double hazard
        elif row["Hazard3"] == "":
            new_row["Country 2"] = row["Country"]
            new_row["Total Deaths 12"] = row["Total Deaths"]
            new_row["Total Affected 12"] = row["Total Affected"]
            new_row["Total Damages 12"] = row["Total Damages, Adjusted ('000 US$')"]
            new_row["Number Hazards"] = 2

        df = pd.concat([df, new_row], ignore_index=True)

    # disaster has spatial and temporal overlap:
    else:
        disastersi = [ix] + json.loads(
            df_s_t_overlapping_events.loc[ix, "Overlapping events"]
        )
        df_tempi = df_impact.loc[disastersi][["Start Date", "End Date"]].sort_values(
            by="Start Date"
        )

        # if ix is temporally first of all overlapping hazards add to dataframe
        if ix == df_tempi.index[0]:
            hazards = set(
                itertools.chain.from_iterable(
                    df_impact.loc[disastersi][
                        ["Hazard1", "Hazard2", "Hazard3"]
                    ].values.tolist()
                )
            )
            hazards = sorted([hazard for hazard in hazards if hazard != ""])

            new_row = create_new_row()
            new_row["Dis No 1"] = ix
            new_row["Hazard 1"] = row["Hazard1"]
            new_row["Hazard 2"] = row["Hazard2"]
            new_row["Start Date 1"] = row["Start Date"]
            new_row["End Date 1"] = row["End Date"]
            new_row["Country 1"] = row["Country"]
            new_row["Continent 1"] = row["Continent"]
            new_row["Dis Mag Value 1"] = row["Dis Mag Value"]
            new_row["Total Deaths 1"] = row["Total Deaths"]
            new_row["Total Affected 1"] = row["Total Affected"]
            new_row["Total Damages 1"] = row["Total Damages, Adjusted ('000 US$')"]
            new_row["Number Hazards"] = len(df_tempi)
            new_row["Type Event"] = "First"
            new_row["Type Hazards"] = ", ".join(hazards)
            new_row["Number Types"] = len(hazards)

            # Add row to dataframe
            df = pd.concat([df, new_row], ignore_index=True)

        # if ix is temporally second and a single hazard and the first one is a single hazard as well and first in its own sequence
        elif (
            (ix == df_tempi.index[1])
            & (df_impact.loc[ix, "Hazard2"] == "")
            & (df_impact.loc[ix, "Hazard3"] == "")
        ):
            # Investigate hazard that is temporally first in ix's sequence
            jx = df_tempi.index[0]
            disastersi = [jx] + json.loads(
                df_s_t_overlapping_events.loc[jx, "Overlapping events"]
            )
            df_tempj = df_impact.loc[disastersi][
                ["Start Date", "End Date"]
            ].sort_values(by="Start Date")

            # If jx is single hazard and also first in its own sequence:
            if (
                (jx == df_tempj.index[0])
                & (df_impact.loc[jx, "Hazard2"] == "")
                & (df_impact.loc[jx, "Hazard3"] == "")
            ):
                hazards = set(
                    itertools.chain.from_iterable(
                        df_impact.loc[disastersi][
                            ["Hazard1", "Hazard2", "Hazard3"]
                        ].values.tolist()
                    )
                )
                hazards = sorted([hazard for hazard in hazards if hazard != ""])

                new_row = create_new_row()
                new_row["Dis No 1"] = jx
                new_row["Dis No 2"] = ix
                new_row["Hazard 2"] = row["Hazard1"]
                new_row["Start Date 1"] = df_impact.loc[jx, "Start Date"]
                new_row["End Date 1"] = df_impact.loc[jx, "End Date"]
                new_row["Start Date 2"] = row["Start Date"]
                new_row["End Date 2"] = row["End Date"]
                new_row["Hazard 1"] = df_impact.loc[jx, "Hazard1"]
                new_row["Country 1"] = df_impact.loc[jx, "Country"]
                new_row["Continent 1"] = df_impact.loc[jx, "Continent"]
                new_row["Dis Mag Value 1"] = df_impact.loc[jx, "Dis Mag Value"]
                new_row["Total Deaths 1"] = df_impact.loc[jx, "Total Deaths"]
                new_row["Total Affected 1"] = df_impact.loc[jx, "Total Affected"]
                new_row["Total Damages 1"] = df_impact.loc[
                    jx, "Total Damages, Adjusted ('000 US$')"
                ]
                new_row["Country 2"] = row["Country"]
                new_row["Continent 2"] = row["Continent"]
                new_row["Dis Mag Value 2"] = row["Dis Mag Value"]
                new_row["Total Deaths 2"] = row["Total Deaths"]
                new_row["Total Affected 2"] = row["Total Affected"]
                new_row["Total Damages 2"] = row["Total Damages, Adjusted ('000 US$')"]
                new_row["Number Hazards"] = len(df_tempi)
                new_row["Type Event"] = "Consecutive"
                new_row["Type Hazards"] = ", ".join(hazards)
                new_row["Number Types"] = len(hazards)

                new_row["Total Deaths 12"] = (
                    df_impact.loc[jx, "Total Deaths"] + new_row["Total Deaths 2"]
                )
                new_row["Total Affected 12"] = (
                    df_impact.loc[jx, "Total Affected"] + new_row["Total Affected 2"]
                )
                new_row["Total Damages 12"] = (
                    df_impact.loc[jx, "Total Damages, Adjusted ('000 US$')"]
                    + new_row["Total Damages 2"]
                )

                # Add row to dataframe
                df = pd.concat([df, new_row], ignore_index=True)

# %%
# Remove duplicates!
df = df.sort_values("Type Event", ascending=True).drop_duplicates("Dis No 1")

df.loc[df["Type Event"] == "First", "Type Event"] = "Consecutive"

# %%
df.to_csv("data/df_compound_consecutive_events.csv", sep=";", index=False)

# %%
