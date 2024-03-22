# %% Imports
import pandas as pd
import numpy as np
from shapely import wkt
import geopandas as gpd
import json
import itertools
import datetime
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt

PROCESSED_EMDAT_PATH = "data/emdat_2000_2018.csv"

# %% EM-DAT
df_emdat = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")
df_emdat.loc[:, "Hazards"] = df_emdat[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: list(x.dropna()), axis=1
)
df_emdat.loc[:, "No Hazards"] = df_emdat.loc[:, "Hazards"].apply(len)


# %% s-t overlapping events
df = pd.read_csv("data/df_s_t_overlapping_events.csv", sep=";", index_col=0)


# %% Count number of events
df["Events"] = df["Events"].apply(json.loads)
df["No events"] = df["Events"].apply(len)


# %% Add hazards and count number of hazards
for ix, row in df.iterrows():
    events = row.loc["Events"]
    hazards = []
    for event in events:
        hazards = hazards + list(
            df_emdat.loc[event, ["Hazard1", "Hazard2", "Hazard3"]].dropna().values
        )

    df.loc[ix, "Hazards"] = json.dumps(hazards)

df["Hazards"] = df["Hazards"].apply(json.loads)
df["No hazards"] = df["Hazards"].apply(len)


# %%
# # %%
# # Total number of hazards in EMDAT
# total_hazards = df_emdat.loc[:, "No Hazards"].sum()
# singles_emdat = sum(df_emdat.loc[:, "No Hazards"] == 1)
# pairs_emdat = sum(df_emdat.loc[:, "No Hazards"] == 2) * 2
# triples_emdat = sum(df_emdat.loc[:, "No Hazards"] == 3) * 3

# # %%
# TIME_LAG_0 = 0
# TIME_LAG_91 = 91
# TIME_LAG_182 = 182
# TIME_LAG_365 = 365


# # %%
# TIME_LAGS = [TIME_LAG_0, TIME_LAG_91, TIME_LAG_182, TIME_LAG_365]
# df = pd.DataFrame(
#     columns=["Hazard occurs as single", "Hazard occurs as multi", "Unique events"]
# )
# df.index.name = "Days"
# for TIME_LAG in TIME_LAGS:
#     PATH = "data/df_s_t_overlapping_events_" + str(TIME_LAG) + ".csv"
#     df_temp = pd.read_csv(PATH, sep=";", index_col=0)
#     df_temp["Overlapping events"] = df_temp["Overlapping events"].apply(json.loads)
#     df_temp["No overlapping events"] = df_temp["Overlapping events"].apply(len)
#     single_hazards = sum(df_temp["Number hazards"] == 1)
#     df.loc[TIME_LAG, "Hazard occurs as single"] = single_hazards
#     df.loc[TIME_LAG, "Hazard occurs as multi"] = total_hazards - single_hazards

#     for ix, row in df_temp.iterrows():
#         df_temp.loc[ix, "Overlapping events seq"] = json.dumps(
#             sorted(row["Overlapping events"] + [ix])
#         )

#     df.loc[TIME_LAG, "Unique events"] = len(df_temp["Overlapping events seq"].unique())
#     df.loc[TIME_LAG, "EMDAT events with overlap"] = sum(
#         df_temp["No overlapping events"] > 0
#     )


# # %%
# import seaborn as sns

# fig, ax = plt.subplots(
#     1,
#     1,
#     figsize=(5, 3),
# )
# sns.set_style("whitegrid")
# fig = sns.lineplot(data=df, markers=True)
# fig.set(ylabel="Number", xlabel="Time lag in days")
# sns.move_legend(fig, "upper left", bbox_to_anchor=(1, 1))
# # %%
# df2 = pd.DataFrame(columns=["single", "multi"])
# df2.index.name = "Days"
# for TIME_LAG in TIME_LAGS:
#     PATH = "data/df_s_t_overlapping_events_" + str(TIME_LAG) + ".csv"
#     df_temp = pd.read_csv(PATH, sep=";", index_col=0)
#     no_overlap = sum(df_temp["Number overlapping events"] == 0)
#     df2.loc[TIME_LAG, "single"] = no_overlap
#     df2.loc[TIME_LAG, "multi"] = 5868 - no_overlap

# # %%
