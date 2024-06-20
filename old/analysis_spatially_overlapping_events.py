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


# %% Constants
PROCESSED_IMPACT_PATH_CSV = "data/impact_2000_2018.csv"
PROCESSED_EMDAT_PATH_CSV = "data/emdat_2000_2018.csv"

TIME_LAG = 182  # days

PROCESSED_EMDAT_PATH = "data/emdat_2000_2018.csv"

# %%
df_emdat = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")

# %% Load impact data
# df = pd.read_csv(PROCESSED_EMDAT_PATH_CSV).set_index("Dis No")


# %% Load impact data
# df_impact = pd.read_csv(PROCESSED_IMPACT_PATH_CSV, sep=";", index_col=0).set_index(
#     "Dis No"
# )
# df_impact[["Hazard1", "Hazard2", "Hazard3"]] = df_impact[
#     ["Hazard1", "Hazard2", "Hazard3"]
# ].fillna("")
# df_impact["Start Date"] = pd.to_datetime(df_impact["Start Date"])
# df_impact["End Date"] = pd.to_datetime(df_impact["End Date"])
# # %%
# df_impact["geometry"] = wkt.loads(df_impact["geometry"])
# gdf_impact = gpd.GeoDataFrame(df_impact, crs="epsg:4326")


# %%
df_spatially_overlapping_events = pd.read_csv(
    "data/df_spatially_overlapping_events.csv", sep=";", index_col=0
)

# %%
df = df_spatially_overlapping_events
df["Overlapping events"] = df["Overlapping events"].apply(json.loads)


# %% Determine unique sequences
for ix, row in df.iterrows():
    df.loc[ix, "Overlapping events seq"] = json.dumps(
        sorted(row["Overlapping events"] + [ix])
    )

len(df["Overlapping events seq"].unique())

# %%  Calculate number of overlapping events & number of overlapping hazards & number of overlapping hazard types

# add number of overlapping events
df["Number overlapping events"] = df["Overlapping events"].apply(len)

# %%
# Add number overlapping hazards
df["Hazards"] = np.nan
df["Total Affected"] = np.nan
df["Total Deaths"] = np.nan
df["Total Damages"] = np.nan


for ix, row in df.iterrows():
    ov_events = row.loc["Overlapping events"]
    hazards = list(df_emdat.loc[ix, ["Hazard1", "Hazard2", "Hazard3"]].dropna().values)

    for ov_event in ov_events:
        hazards = hazards + list(
            df_emdat.loc[ov_event, ["Hazard1", "Hazard2", "Hazard3"]].dropna().values
        )

    df.loc[ix, "Hazards"] = json.dumps(hazards)
    df.loc[ix, "Total Deaths"] = df_emdat.loc[ix, "Total Deaths"]
    df.loc[ix, "Total Affected"] = df_emdat.loc[ix, "Total Affected"]
    df.loc[ix, "Total Damages"] = df_emdat.loc[
        ix, "Total Damages, Adjusted ('000 US$')"
    ]


# %%
df["Hazards"] = df["Hazards"].apply(json.loads)
df["Number hazards"] = df["Hazards"].apply(len)

# %%
# Add number overlapping hazard types
df["Hazard types"] = df["Hazards"].apply(set)
df["Number hazard types"] = df["Hazard types"].apply(len)

# %%
df["ISO"] = df.index.str[10:14]

# %%
filter = df["Number overlapping events"] >= 19
df.loc[filter, "ISO"].value_counts()

# Size of impact area


# #%% Scatter plots
# plt.scatter(df["Number of overlapping events"], df["Total Damages"])


# %%
plt.hist(df["Number overlapping events"], bins=19)

# %%
fig, axs = plt.subplots(
    1,
    3,
    figsize=(12, 6),
    # width_ratios=[3, 3, 3],
)
axs[0].hist(
    x=df["Number overlapping events"],
)
axs[1].hist(x=df["Number hazards"])
axs[2].hist(x=df["Number hazard types"])
# plt.xlabel("Intersection %")
# plt.ylabel("Number of event pairs")


# %%
df_impact = pd.read_csv("data/impact_2000_2018.csv", sep=";").set_index("Dis No")

df_impact["geometry"] = wkt.loads(df_impact["geometry"])
gdf_impact = gpd.GeoDataFrame(df_impact, crs="epsg:4326")


# %%
gdf_impact.loc[["2010-0239-CHN", "2016-0236-CHN", "2016-0162-CHN"]].reset_index().plot(
    column="Dis No", alpha=0.05, legend=True
)


# %%
gdf_impact.loc[
    df_spatially_overlapping_events.loc["2010-0239-CHN", "Overlapping events"]
].reset_index().plot(
    column="Dis No", alpha=0.05, legend=False, cmap=ListedColormap(["gray"])
)

# %%
