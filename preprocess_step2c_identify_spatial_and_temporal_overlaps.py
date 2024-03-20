# %% Imports
import pandas as pd
import itertools
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from shapely import wkt
import geopandas as gpd
import datetime


FIRST_YEAR = 2000
LAST_YEAR = 2018
PROCESSED_IMPACT_PATH_CSV = (
    "data/impact_" + str(FIRST_YEAR) + "_" + str(LAST_YEAR) + ".csv"
)
PROCESSED_EMDAT_PATH = "data/emdat_2000_2018.csv"

# %%
df_emdat = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")
df_emdat["Start Date"] = pd.to_datetime(df_emdat["Start Date"])
df_emdat["End Date"] = pd.to_datetime(df_emdat["End Date"])
# %%
df = pd.read_csv("data/event_pairs_50percent.csv", sep=";")

# %%

TIME_LAG_0 = 0
TIME_LAG_91 = 91
TIME_LAG_182 = 182
TIME_LAG_365 = 365
TIME_LAG_6935 = 6935

# %%
TIME_LAGS = [TIME_LAG_0, TIME_LAG_91, TIME_LAG_182, TIME_LAG_365, TIME_LAG_6935]
TIME_LAG = TIME_LAG_182

### Create pairs with temporal overlap
# %%
df_lag = df.copy(deep=True)
df_lag["Temporal Overlap"] = False
temporal_buffer = datetime.timedelta(days=TIME_LAG)

# %%
# we compare 2 start dates because some events miss an end date
for ix, row in df_lag.iterrows():
    start_event1 = df_emdat.loc[row["Event1"]]["Start Date"]
    start_event2 = df_emdat.loc[row["Event2"]]["Start Date"]
    day_difference = (start_event1 - start_event2).days
    if abs(day_difference) <= TIME_LAG:
        df_lag.loc[ix, "Temporal Overlap"] = True

df_lag = df_lag.loc[df_lag["Temporal Overlap"]]

### Create independent sets of events
# %%
list_lag = []
while len(df_lag) > 0:
    start_event11 = df_emdat.loc[df_lag.iloc[0]["Event1"]]["Start Date"]
    start_event12 = df_emdat.loc[df_lag.iloc[0]["Event2"]]["Start Date"]
    indices = []
    for ix, row in df_lag.iterrows():
        start_event21 = df_emdat.loc[row["Event1"]]["Start Date"]
        start_event22 = df_emdat.loc[row["Event2"]]["Start Date"]
