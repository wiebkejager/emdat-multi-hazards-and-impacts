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

# %%
df_emdat = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")

df_emdat.loc[:, "Hazards"] = df_emdat[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: list(x.dropna()), axis=1
)

df_emdat.loc[:, "No Hazards"] = df_emdat.loc[:, "Hazards"].apply(len)

# %%
# Total number of hazards in EMDAT
total_hazards = df_emdat.loc[:, "No Hazards"].sum()
singles_emdat = sum(df_emdat.loc[:, "No Hazards"] == 1)

# %%
TIME_LAG_0 = 0
TIME_LAG_91 = 91
TIME_LAG_182 = 182
TIME_LAG_365 = 365


# %%
TIME_LAGS = [TIME_LAG_0, TIME_LAG_91, TIME_LAG_182, TIME_LAG_365]
df = pd.DataFrame(columns=["Single-hazards", "Multi-hazards"])
df.index.name = "Days"
for TIME_LAG in TIME_LAGS:
    PATH = "data/df_s_t_overlapping_events_" + str(TIME_LAG) + ".csv"
    df_temp = pd.read_csv(PATH, sep=";", index_col=0)
    single_hazards = sum(df_temp["Number hazards"] == 1)
    df.loc[TIME_LAG, "Single-hazards"] = single_hazards
    df.loc[TIME_LAG, "Multi-hazards"] = total_hazards - single_hazards


# %%
import seaborn as sns

sns.set_style("whitegrid")
fig = sns.lineplot(data=df, markers=True)
fig.set(ylabel="Number of hazards")

# %%
