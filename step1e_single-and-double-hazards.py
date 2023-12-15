# %% Imports
import pandas as pd
import numpy as np
import json

# %%
PROCESSED_IMPACT_PATH_CSV = "impact_2000_2015.csv"

# %%
df_emdat = pd.read_csv(PROCESSED_IMPACT_PATH_CSV, sep=";").set_index("Dis No")

# %%
df_overlaps = pd.read_csv("df_res.csv", sep=";", index_col=0)
df_overlaps.replace("[]", np.nan, inplace=True)
df_overlaps.dropna(inplace=True)

# %%
# Add column indicating event set
df_emdat.loc[:, "eventtype_detailed_unsrt"] = df_emdat[
    ["Hazard1", "Hazard2", "Hazard3"]
].apply(lambda x: ",".join(list(x.dropna())), axis=1)

# Drop rows with more than 2 Hazards
# df_emdat = df_emdat.loc[df_emdat.loc[:, "Hazard3"].isna()]

# %%

for ix, row in df_overlaps.iterrows():
    for jx in json.loads(row["Overlapping events"]):
        # Check if same event reported across different countries and merge
        time_check = (
            df_emdat.loc[ix, "Start Date"] == df_emdat.loc[jx, "Start Date"]
        ) & (df_emdat.loc[ix, "End Date"] == df_emdat.loc[jx, "End Date"])
        hazard_check = df_emdat.loc[ix, "Hazard1"] == df_emdat.loc[ix, "Hazard1"]
        if time_check & hazard_check:
            foo = 2
        else:
            print(ix)
            print(jx)
            foo = 2
            # identify first and second hazard
            # if both single hazards

    # df_emdat.loc[ix, :]

# Merge events that are


# %%
columns = [
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

for ix, row in df_emdat:
    # does row have spatial overlap?

    # no and single or double hazard -> add to dataframe as H1 or H1&H2

    # yes and single hazard:
        # if 1st in overlapping hazards -> add to dataframe as H1 ????
        # if 2nd in overlapping hazards -> add to dataframe as H2
            # if 1st hazard has no other overlapping hazard add as H1 and add H1+H1

    # else: continue
