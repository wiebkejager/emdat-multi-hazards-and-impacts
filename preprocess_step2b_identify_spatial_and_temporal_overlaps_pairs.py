# %% Imports
import pandas as pd
import itertools
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from shapely import wkt
import geopandas as gpd

FIRST_YEAR = 2000
LAST_YEAR = 2018
PROCESSED_IMPACT_PATH_CSV = (
    "data/impact_" + str(FIRST_YEAR) + "_" + str(LAST_YEAR) + ".csv"
)
PROCESSED_EMDAT_PATH = "data/emdat_2000_2018.csv"

# %%
df_emdat = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")
df = pd.read_csv("data/event_pairs.csv", sep=";")

# %%
df["Percent"] = df.apply(lambda x: np.max([x.Percent1, x.Percent2]), axis=1)
df["StartDate1"] = pd.to_datetime(
    df.apply(lambda x: df_emdat.loc[x.Event1, "Start Date"], axis=1)
)
df["StartDate2"] = pd.to_datetime(
    df.apply(lambda x: df_emdat.loc[x.Event2, "Start Date"], axis=1)
)
df["Timelag"] = df.apply(lambda x: abs((x.StartDate2 - x.StartDate1).days), axis=1)

# %%
plt.hist(
    df["Percent"] * 100,
    bins=100,
)
plt.xlabel("Intersection %")
plt.ylabel("Number of event pairs")


# %%
min_overlap_thress = [0, 0.5, 1]
max_time_lags = [0, 30, 91, 182, 365, 100000]

for min_overlap_thres in min_overlap_thress:
    for max_time_lag in max_time_lags:
        thres_filter = (df["Percent"] >= min_overlap_thres) & (
            df["Timelag"] <= max_time_lag
        )
        filename = (
            "data/event_pairs_"
            + str(min_overlap_thres)
            + "_"
            + str(max_time_lag)
            + ".csv"
        )
        df.loc[thres_filter].to_csv(filename, sep=";", index=False)


# %%
# event_pairs = list(df.loc[:, ["Event1", "Event2"]].itertuples(index=False, name=None))
# unique_events = df_emdat.index.values
# event_pairs = list(
#     df.loc[thres_filter, ["Event1", "Event2"]].itertuples(index=False, name=None)
# )


# # %% investigate temporal overlap":
# timelags = [
#     abs(
#         (
#             pd.to_datetime(df_emdat.loc[event_pair[0], "Start Date"])
#             - pd.to_datetime(df_emdat.loc[event_pair[1], "Start Date"])
#         ).days
#     )
#     for event_pair in event_pairs
# ]

# # %%
# print("0: ", sum([timelag <= 0 for timelag in timelags]))
# print("30: ", sum([timelag <= 30 for timelag in timelags]))
# print("91: ", sum([timelag <= 91 for timelag in timelags]))
# print("182: ", sum([timelag <= 182 for timelag in timelags]))
# print("365: ", sum([timelag <= 365 for timelag in timelags]))
# print("1000000: ", sum([timelag <= 1000000 for timelag in timelags]))
