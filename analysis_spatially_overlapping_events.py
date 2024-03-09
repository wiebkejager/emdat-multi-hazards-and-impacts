# %% Imports
import pandas as pd
import numpy as np
from shapely import wkt
import geopandas as gpd
import json
import itertools
import datetime
from matplotlib.colors import ListedColormap

# %% Constants
PROCESSED_IMPACT_PATH_CSV = "data/impact_2000_2018.csv"
PROCESSED_EMDAT_PATH_CSV = "data/emdat_2000_2018.csv"

TIME_LAG = 182  # days

# %% Load impact data
df = pd.read_csv(PROCESSED_EMDAT_PATH_CSV).set_index("Dis No")

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
# Calculate number of overlapping events & number of overlapping hazards & number of overlapping hazard types
df["Number of overlapping events"] = df["Overlapping events"].apply(len)


# add number of overlapping events

# add overlapping hazards

# add number

# %%
df_impact_usa = pd.read_csv("data/impact_2000_2018_usa.csv", sep=";").set_index(
    "Dis No"
)

df_impact_usa["geometry"] = wkt.loads(df_impact_usa["geometry"])
gdf_impact_usa = gpd.GeoDataFrame(df_impact_usa, crs="epsg:4326")

# %%
gdf_impact_usa["Affected Area"] = (
    gdf_impact_usa.to_crs({"init": "epsg:3857"})["geometry"].area / 10**6
)

# %%
df_spatially_overlapping_events_usa = df_spatially_overlapping_events[
    df_spatially_overlapping_events.index.str[10:14] == "USA"
].tail(2)

# %%
df_spatially_overlapping_events_usa["Sig overlap"] = np.nan
for event in df_spatially_overlapping_events_usa.index:
    overlapping_events = df_spatially_overlapping_events_usa.loc[
        event, "Overlapping events"
    ]
    event1 = gdf_impact_usa.loc[[event]]
    sig_overlapping_events = []
    for overlapping_event in overlapping_events:
        event2 = gdf_impact_usa.loc[[overlapping_event]]
        if event2.index[0] == "2002-0119-USA":
            foo = 2
        intersection = event1.intersection(event2, align=False)
        area_intersection = intersection.to_crs({"init": "epsg:3857"}).area / 10**6
        criterion = np.min(
            [
                area_intersection[0] / event1["Affected Area"][0],
                area_intersection[0] / event2["Affected Area"][0],
            ]
        )
        if criterion > 0.25:
            sig_overlapping_events.append(overlapping_event)

    df_spatially_overlapping_events_usa.loc[event, "Sig overlap"] = json.dumps(
        sig_overlapping_events
    )

# %%
filter = (gdf_impact_usa.index == "2011-0264-USA") | (
    gdf_impact_usa.index == "2002-0119-USA"
)
cmap = ListedColormap(["red", "blue"])
gdf_impact_usa["color"] = np.nan
gdf_impact_usa[filter].reset_index().plot(
    column="Dis No", alpha=0.4, legend=True, colormap=cmap
)

# %%
event1 = gdf_impact_usa.loc[["2011-0264-USA"]]
event2 = gdf_impact_usa.loc[["2001-0724-USA"]]
intersection = event1.intersection(event2, align=False)
area_intersection = intersection.to_crs({"init": "epsg:3857"}).area / 10**6

# %%
area_intersection[0] / event1["Affected Area"][0]

# %%
area_intersection[0] / event2["Affected Area"][0]

# %%
gdf_impact_usa.loc[["2001-0724-USA"]].reset_index().plot(
    column="Dis No", alpha=0.4, legend=True
)

# %%
gdf_impact_usa.loc[["2011-0264-USA"]].reset_index().plot(
    column="Dis No", alpha=0.4, legend=True
)

# %%
