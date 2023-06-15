# %% Imports
import pandas as pd
import geopandas as gpd
from shapely import wkt
from shapely.geometry import Point, Polygon
import rasterio
import rasterio.plot
from rasterio import features
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import rioxarray
import pygeos
from funs import has_overlap_in_time


# %% Define constants
hazards = [
    "eq",
    "fl",
    "dr",
    "ts",
    "vo",
    "ls",
    "hw",
    "ew",
    "cw",
    "wf",
]  # available hazards


START_YEAR = 2000
END_YEAR = 2015
HAZARD_PATH = "C:/Users/wja209/DATA/RAW/hazards/"
PROCESSED_HAZARD_PATH = "C:/Users/wja209/DATA/PROCESSED/"

# %% Open all single hazard files, truncate to period 1990 - 2015 and store again
for hazard in hazards:
    print(hazard)
    df = pd.read_csv(HAZARD_PATH + hazard + ".csv", index_col=0)
    time_filter = (df["starttime"].str[0:4] >= str(START_YEAR)) & (
        df["endtime"].str[0:4] <= str(END_YEAR)
    )
    df = df[time_filter]
    df.to_csv(HAZARD_PATH + hazard + "_1990_2015.csv", index=False)


# %% Open all reduced single datafiles, concatenate into single df and store
df_list = []
for hazard in hazards:
    print(hazard)
    df_list.append(pd.read_csv(PROCESSED_HAZARD_PATH + hazard + "_1990_2015.csv"))
df = pd.concat(df_list)
df.to_csv(HAZARD_PATH + "hazards_1990_2015.csv", index=False)
