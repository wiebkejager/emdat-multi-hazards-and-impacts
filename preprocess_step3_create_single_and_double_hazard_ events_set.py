# %% Imports
import pandas as pd
import numpy as np
import json


# %% Constants
PROCESSED_UNIQUE_IMPACT_PATH_CSV = "data/unique_events_impact_2000_2018.csv"


# %% Load impact data
df_impact = pd.read_csv(PROCESSED_UNIQUE_IMPACT_PATH_CSV, sep=";", index_col=0)
df_impact[["Hazard1", "Hazard2", "Hazard3"]] = df_impact[
    ["Hazard1", "Hazard2", "Hazard3"]
].fillna("")

# %% Load overlapping event list and remove empty entries
df_overlapping_events = pd.read_csv(
    "data/df_s_t_overlapping_events.csv", sep=";", index_col=0
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
    "Country 2",
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
]

df = pd.DataFrame(
    columns=cols,
)

# %%
for ix, row in df_impact.iterrows():
    # disaster does not have spatial overlap
    if ix not in df_overlapping_events.index:
        if row["Hazard3"] == "":
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
                    ]
                ],
                columns=cols,
            )
            # and is single hazard
            if row["Hazard2"] == "":
                new_row["Total Deaths 1"] = row["Total Deaths"]
                new_row["Total Affected 1"] = row["Total Affected"]
                new_row["Total Damages 1"] = row["Total Damages, Adjusted ('000 US$')"]
            # and is double hazard
            else:
                new_row["Country 2"] = row["Country"]
                new_row["Total Deaths 12"] = row["Total Deaths"]
                new_row["Total Affected 12"] = row["Total Affected"]
                new_row["Total Damages 12"] = row["Total Damages, Adjusted ('000 US$')"]
            df = pd.concat([df, new_row], ignore_index=True)
    # disaster has spatial overlap and is single hazard:
    elif (row["Hazard2"] == "") & (row["Hazard3"] == ""):
        disastersi = [ix] + json.loads(
            df_overlapping_events.loc[ix, "Overlapping events"]
        )
        df_tempi = df_impact.loc[disastersi][["Start Date", "End Date"]].sort_values(
            by="Start Date"
        )
        jx = df_tempi.index[0]
        # # if 1st in overlapping hazards -> add to dataframe as H1
        # if ix == df_tempi.index[0]:
        #     new_row = pd.DataFrame(
        #         [
        #             [
        #                 ix,
        #                 np.nan,
        #                 row["Hazard1"],
        #                 np.nan,
        #                 row["Start Date"],
        #                 row["End Date"],
        #                 np.nan,
        #                 np.nan,
        #                 row["Country"],
        #                 np.nan,
        #                 row["Dis Mag Value"],
        #                 np.nan,
        #                 row["Total Deaths"],
        #                 np.nan,
        #                 np.nan,
        #                 row["Total Affected"],
        #                 np.nan,
        #                 np.nan,
        #                 row["Total Damages, Adjusted ('000 US$')"],
        #                 np.nan,
        #                 np.nan,
        #             ]
        #         ],
        #         columns=cols,
        #     )
        #     df = pd.concat([df, new_row], ignore_index=True)
        if (
            (ix == df_tempi.index[1])
            & (df_impact.loc[jx, "Hazard2"] == "")
            & (df_impact.loc[jx, "Hazard3"] == "")
        ):  # if 2nd in overlapping hazards and 1st hazard is also single hazard-> add to dataframe as H2
            new_row = pd.DataFrame(
                [
                    [
                        np.nan,
                        ix,
                        np.nan,
                        row["Hazard1"],
                        np.nan,
                        np.nan,
                        row["Start Date"],
                        row["End Date"],
                        np.nan,
                        row["Country"],
                        np.nan,
                        row["Dis Mag Value"],
                        np.nan,
                        row["Total Deaths"],
                        np.nan,
                        np.nan,
                        row["Total Affected"],
                        np.nan,
                        np.nan,
                        row["Total Damages, Adjusted ('000 US$')"],
                        np.nan,
                    ]
                ],
                columns=cols,
            )
            if jx not in df_overlapping_events.index:
                continue
            # if 1st hazard has no other overlapping hazard before it add as H1 and add H1+H2
            disastersj = [jx] + json.loads(
                df_overlapping_events.loc[jx, "Overlapping events"]
            )
            df_tempj = df_impact.loc[disastersj][
                ["Start Date", "End Date"]
            ].sort_values(by="Start Date")
            if jx == df_tempj.index[0]:
                new_row["Dis No 1"] = jx
                new_row["Hazard 1"] = df_impact.loc[jx, "Hazard1"]
                new_row["Magnitude 1"] = df_impact.loc[jx, "Dis Mag Value"]
                new_row["Start Date 1"] = df_impact.loc[jx, "Start Date"]
                new_row["End Date 1"] = df_impact.loc[jx, "End Date"]
                new_row["Country 1"] = df_impact.loc[jx, "Country"]
                new_row["Total Deaths 1"] = df_impact.loc[jx, "Total Deaths"]
                new_row["Total Affected 1"] = df_impact.loc[jx, "Total Affected"]
                new_row["Total Damages 1"] = df_impact.loc[
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

            df = pd.concat([df, new_row], ignore_index=True)

    else:
        continue

# %%
df.to_csv("data/df_single_and_pair_impacts.csv", sep=";", index=False)

# %%
