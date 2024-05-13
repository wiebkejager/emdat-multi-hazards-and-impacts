# %% Imports
import pandas as pd
import numpy as np
import json


# %% Constants
PROCESSED_EMDAT_PATH = "data/emdat_2000_2018.csv"

# %%
df_emdat = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")
df_emdat["Start Date"] = pd.to_datetime(df_emdat["Start Date"])
df_emdat["End Date"] = pd.to_datetime(df_emdat["End Date"])
df_emdat[["Hazard1", "Hazard2", "Hazard3"]] = df_emdat[
    ["Hazard1", "Hazard2", "Hazard3"]
].fillna("")


# %%
min_overlap_thres = 0.5
max_time_lag = 30
df_chains = pd.read_csv(
    "data/df_chain_" + str(min_overlap_thres) + "_" + str(max_time_lag) + ".csv",
    sep=";",
    index_col=0,
)
df_chains["Events"] = df_chains["Events"].apply(json.loads)


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
    "Timelag",
    "Min spatial overlap",
]

df = pd.DataFrame(
    columns=cols,
)


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
            ]
        ],
        columns=cols,
    )


# %% Get impacts for first and second hazards
for ix, row in df_chains.loc[df_chains["No hazards"] <= 2].iterrows():
    dis_no1 = row["Events"][0]
    event1 = df_emdat.loc[dis_no1]

    # if is single hazard
    if (event1["Hazard2"] == "") & (event1["Hazard3"] == ""):

        new_row = create_new_row()
        new_row["Dis No 1"] = dis_no1
        new_row["Hazard 1"] = event1["Hazard1"]
        new_row["Start Date 1"] = event1["Start Date"]
        new_row["End Date 1"] = event1["End Date"]
        new_row["Country 1"] = event1["Country"]
        new_row["Continent 1"] = event1["Continent"]
        new_row["Dis Mag Value 1"] = event1["Dis Mag Value"]

        if len(row["Events"]) == 1:
            new_row["Total Deaths 1"] = event1["Total Deaths"]
            new_row["Total Affected 1"] = event1["Total Affected"]
            new_row["Total Damages 1"] = event1["Total Damages, Adjusted ('000 US$')"]
        # new_row["Number Hazards"] = 1

        if len(row["Events"]) > 1:

            dis_no2 = row["Events"][1]
            event2 = df_emdat.loc[dis_no2]

            if (event2["Hazard2"] == "") & (event2["Hazard3"] == ""):
                new_row["Dis No 2"] = dis_no2
                new_row["Hazard 2"] = event2["Hazard1"]
                new_row["Start Date 2"] = event2["Start Date"]
                new_row["End Date 2"] = event2["End Date"]
                new_row["Country 2"] = event2["Country"]
                new_row["Continent 2"] = event2["Continent"]
                new_row["Dis Mag Value 2"] = event2["Dis Mag Value"]
                new_row["Total Deaths 2"] = event2["Total Deaths"]
                new_row["Total Affected 2"] = event2["Total Affected"]
                new_row["Total Damages 2"] = event2[
                    "Total Damages, Adjusted ('000 US$')"
                ]
                # new_row["Number Hazards"] = 2
                new_row["Total Deaths 12"] = (
                    event1["Total Deaths"] + event2["Total Deaths"]
                )
                new_row["Total Affected 12"] = (
                    event1["Total Affected"] + event2["Total Affected"]
                )
                new_row["Total Damages 12"] = (
                    event1["Total Damages, Adjusted ('000 US$')"]
                    + event2["Total Damages, Adjusted ('000 US$')"]
                )

        new_row["Timelag"] = max_time_lag
        new_row["Min spatial overlap"] = min_overlap_thres
        df = pd.concat([df, new_row], ignore_index=True)

    # if is double hazard
    elif event1["Hazard3"] == "":

        new_row = create_new_row()
        new_row["Dis No 1"] = dis_no1
        new_row["Hazard 1"] = event1["Hazard1"]
        new_row["Hazard 2"] = event1["Hazard2"]
        new_row["Start Date 1"] = event1["Start Date"]
        new_row["End Date 1"] = event1["End Date"]
        new_row["Country 1"] = event1["Country"]
        new_row["Continent 1"] = event1["Continent"]
        new_row["Dis Mag Value 1"] = event1["Dis Mag Value"]
        new_row["Country 2"] = event1["Country"]
        new_row["Total Deaths 12"] = event1["Total Deaths"]
        new_row["Total Affected 12"] = event1["Total Affected"]
        new_row["Total Damages 12"] = event1["Total Damages, Adjusted ('000 US$')"]

        new_row["Timelag"] = max_time_lag
        new_row["Min spatial overlap"] = min_overlap_thres

        df = pd.concat([df, new_row], ignore_index=True)

    else:
        continue


# %%
df.to_csv(
    "data/df_single_and_pair_impacts_"
    + str(min_overlap_thres)
    + "_"
    + str(max_time_lag)
    + ".csv",
    sep=";",
    index=False,
)

# %%
