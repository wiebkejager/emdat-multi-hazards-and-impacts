# %% Imports
import pandas as pd
import numpy as np
import json
import itertools

# %% Constants
PROCESSED_UNIQUE_IMPACT_PATH_CSV = "data/unique_events_impact_2000_2018.csv"


# %% Load impact data
df_impact = pd.read_csv(PROCESSED_UNIQUE_IMPACT_PATH_CSV, sep=";", index_col=0)
df_impact[["Hazard1", "Hazard2", "Hazard3"]] = df_impact[
    ["Hazard1", "Hazard2", "Hazard3"]
].fillna("")

# %% Load overlapping event list and remove empty entries
df_overlapping_events = pd.read_csv(
    "data/df_spatially_overlapping_events.csv", sep=";", index_col=0
)
df_overlapping_events.replace("[]", np.nan, inplace=True)
df_overlapping_events.dropna(inplace=True)


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
for ix, row in df_impact.iterrows():
    # disaster does not have spatial overlap
    if ix not in df_overlapping_events.index:
        hazards = [row["Hazard1"], row["Hazard2"], row["Hazard3"]]
        hazards = sorted([hazard for hazard in hazards if hazard != ""])

        new_row = pd.DataFrame(
            [
                [
                    ix,
                    np.nan,
                    row["Hazard1"],
                    row["Hazard2"],
                    row["Start Date"],
                    row["End Date"],
                    np.nan,
                    np.nan,
                    row["Country"],
                    row["Continent"],
                    np.nan,
                    np.nan,
                    row["Dis Mag Value"],
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
                    3,
                    "Associated",
                    hazards,
                    len(hazards),
                ]
            ],
            columns=cols,
        )

        # if is single hazard
        if (row["Hazard2"] == "") & (row["Hazard3"] == ""):
            new_row["Total Deaths 1"] = row["Total Deaths"]
            new_row["Total Affected 1"] = row["Total Affected"]
            new_row["Total Damages 1"] = row["Total Damages, Adjusted ('000 US$')"]
            new_row["Number Hazards"] = 1
        # if is double hazard
        elif row["Hazard3"] == "":
            new_row["Country 2"] = row["Country"]
            new_row["Total Deaths 12"] = row["Total Deaths"]
            new_row["Total Affected 12"] = row["Total Affected"]
            new_row["Total Damages 12"] = row["Total Damages, Adjusted ('000 US$')"]
            new_row["Number Hazards"] = 2

        df = pd.concat([df, new_row], ignore_index=True)

    # disaster has spatial overlap:
    else:
        disastersi = [ix] + json.loads(
            df_overlapping_events.loc[ix, "Overlapping events"]
        )
        df_tempi = df_impact.loc[disastersi][["Start Date", "End Date"]].sort_values(
            by="Start Date"
        )

        # consider only if ix is temporally first of all overlapping hazards
        if ix == df_tempi.index[0]:
            hazards = set(
                itertools.chain.from_iterable(
                    df_impact.loc[disastersi][
                        ["Hazard1", "Hazard2", "Hazard3"]
                    ].values.tolist()
                )
            )
            hazards = sorted([hazard for hazard in hazards if hazard != ""])

            new_row = pd.DataFrame(
                [
                    [
                        ix,
                        np.nan,
                        row["Hazard1"],
                        row["Hazard2"],
                        row["Start Date"],
                        row["End Date"],
                        np.nan,
                        np.nan,
                        row["Country"],
                        row["Continent"],
                        np.nan,
                        np.nan,
                        row["Dis Mag Value"],
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
                        len(df_tempi),
                        "Spatially overlapping",
                        hazards,
                        len(hazards),
                    ]
                ],
                columns=cols,
            )

            # if ix is a single hazard add as Hazard1 to new row and potentially add hazard 2 as well
            if (row["Hazard2"] == "") & (row["Hazard3"] == ""):
                disastersi = [ix] + json.loads(
                    df_overlapping_events.loc[ix, "Overlapping events"]
                )
                df_tempi = df_impact.loc[disastersi][
                    ["Start Date", "End Date"]
                ].sort_values(by="Start Date")

                new_row["Magnitude 1"] = row["Dis Mag Value"]
                new_row["Total Deaths 1"] = row["Total Deaths"]
                new_row["Total Affected 1"] = row["Total Affected"]
                new_row["Total Damages 1"] = row["Total Damages, Adjusted ('000 US$')"]

                # Investigate hazard that is temporally second
                jx = df_tempi.index[1]
                # If jx single hazard, add as Hazard 2 to new row
                if (df_impact.loc[jx, "Hazard2"] == "") & (
                    df_impact.loc[jx, "Hazard3"] == ""
                ):
                    new_row["Dis No 2"] = jx
                    new_row["Hazard 2"] = df_impact.loc[jx, "Hazard1"]
                    new_row["Magnitude 2"] = df_impact.loc[jx, "Dis Mag Value"]
                    new_row["Start Date 2"] = df_impact.loc[jx, "Start Date"]
                    new_row["End Date 2"] = df_impact.loc[jx, "End Date"]
                    new_row["Country 2"] = df_impact.loc[jx, "Country"]
                    new_row["Continent 2"] = df_impact.loc[jx, "Continent"]
                    new_row["Total Deaths 2"] = df_impact.loc[jx, "Total Deaths"]
                    new_row["Total Affected 2"] = df_impact.loc[jx, "Total Affected"]
                    new_row["Total Damages 2"] = df_impact.loc[
                        jx, "Total Damages, Adjusted ('000 US$')"
                    ]
                    new_row["Total Deaths 12"] = (
                        new_row["Total Deaths 1"] + new_row["Total Deaths 2"]
                    )
                    new_row["Total Affected 12"] = (
                        new_row["Total Affected 1"] + new_row["Total Affected 2"]
                    )
                    new_row["Total Damages 12"] = (
                        new_row["Total Damages 1"] + new_row["Total Damages 2"]
                    )

            # Add row to dataframe
            df = pd.concat([df, new_row], ignore_index=True)


# %%
df.to_csv("data/df_multi_hazard_events.csv", sep=";", index=False)

# %%
