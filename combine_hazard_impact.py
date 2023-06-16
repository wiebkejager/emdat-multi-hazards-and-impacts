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
from funs import has_overlap_in_time

# %% Constants
PROCESSED_IMPACT_PATH = (
    "C:/Users/wja209/DATA/PROCESSED/impact_exposure_vulnerability_1990_2015.gpkg"
)

# %% Load data
gdf_impact = gpd.read_file(PROCESSED_IMPACT_PATH)


# %% Use Subtype to map Hazard 1
disaster_subtype_to_hazard_map = {
    "Drought": "dr",
    "Riverine flood": "fl",
    "Cold wave": "cw",
    "Convective storm": "ew",
    "Ground movement": "eq",
    "Flash flood": "fl",
    "Coastal flood": "fl",
    "Tropical cyclone": "eq",
    "Avalanche": "ls",
    "Ash fall": "vo",
    "Landslide": "ls",
    "Heat wave": "hw",
    "Mudslide": "ls",
    "Tsunami": "ts",
    "Extra-tropical storm": "eq",
    "Rockfall": "ls",
    "Lava flow": "vo",
}

gdf_impact.loc[:, "Hazard1"] = gdf_impact["Disaster Subtype"].map(
    disaster_subtype_to_hazard_map
)

# %% For nan's use Type to map Hazard 1
disaster_type_to_hazard_map = {
    "Drought": "dr",
    "Flood": "fl",
    "Storm": "ew",
    "Earthquake": "eq",
    "Landslide": "ls",
    "Volcanic activity": "vo",
}
gdf_impact.loc[gdf_impact["Hazard1"].isna(), "Hazard1"] = gdf_impact[
    gdf_impact["Hazard1"].isna()
]["Disaster Type"].map(disaster_type_to_hazard_map)

# %% For remaining nan's drop rows.
gdf_impact = gdf_impact[~gdf_impact["Hazard1"].isna()]


# %% Map Associated to Hazard 2
associated_disaster_to_hazard_map = {
    "gdf_impactd shortage": "exclude",
    "Fire": "exclude",
    "Slide (land, mud, snow, rock)": "ls",
    "Flood": "fl",
    "Broken Dam/Burst bank": "exclude",
    "Rain": "exclude",
    "Tsunami/Tidal wave": "ts",
    "Hail": "exclude",
    "Drought": "dr",
    "Surge": "exclude",
    "Cold wave": "cw",
    "Water shortage": "exclude",
    "Heat wave": "hw",
    "Wildfire": "wf",
    "Famine": "exclude",
    "Transport accident": "exclude",
    "Snow/ice": "exclude",
    "Collapse": "exclude",
    "Pollution": "exclude",
    "Crop failure": "exclude",
    "Lightening": "exclude",
    "Avalanche (Snow, Debris)": "ls",
    "Fog": "exclude",
    "Storm": "ew",
}

gdf_impact.loc[:, "Hazard2"] = gdf_impact["Associated Dis"].map(
    associated_disaster_to_hazard_map
)

# %% Drop rows with exclude
gdf_impact = gdf_impact[gdf_impact["Hazard2"] != "exclude"]


# %% Map Associated 2 to Hazard 3
associated_disaster2_to_hazard_map = {
    "Transport accident": "exclude",
    "Slide (land, mud, snow, rock)": "ls",
    "Surge": "exclude",
    "Famine": "exclude",
    "gdf_impactd shortage": "exclude",
    "Flood": "fl",
    "Tsunami/Tidal wave": "ts",
    "Rain": "exclude",
    "Broken Dam/Burst bank": "exclude",
    "Hail": "exclude",
    "Explosion": "exclude",
    "Snow/ice": "exclude",
    "Cold wave": "cw",
    "Pollution": "exclude",
    "Avalanche (Snow, Debris)": "ls",
    "Collapse": "exclude",
    "Fire": "exclude",
    "Lightening": "exclude",
    "Wildfire": "wf",
    "Industrial accidents": "exclude",
    "Storm": "eq",
    "Epidemic": "exclude",
}
gdf_impact.loc[:, "Hazard3"] = gdf_impact["Associated Dis2"].map(
    associated_disaster2_to_hazard_map
)


# %%
gdf_impact = gdf_impact[gdf_impact["Hazard3"] != "exclude"]


# %% Add flood intensity

fl_filter = (
    (gdf_impact["Hazard1"] == "fl")
    | (gdf_impact["Hazard2"] == "fl")
    | (gdf_impact["Hazard3"] == "fl")
)

eq_filter = (
    (gdf_impact["Hazard1"] == "eq")
    | (gdf_impact["Hazard2"] == "eq")
    | (gdf_impact["Hazard3"] == "eq")
)

# %%
df_eq = pd.read_csv("C:/Users/wja209/DATA/RAW/hazards/eq_1990_2015.csv")

# %%
df_eq["geometry"] = df_eq["Geometry"].apply(wkt.loads)
crs = gdf_impact.crs
gdf_haz = gpd.GeoDataFrame(df_eq, crs=crs, geometry=df_eq["geometry"])
gdf_haz.drop("Geometry", axis=1, inplace=True)
gdf_haz["starttime"] = pd.to_datetime(df_eq["starttime"], utc=True)  # format starttime
gdf_haz["endtime"] = pd.to_datetime(df_eq["endtime"], utc=True)  # format endtime

# %%
df_haz_impact = gdf_haz.merge(
    right=gdf_impact[eq_filter], how="cross", suffixes=["_hazard", "_impact"]
)

# %%
temporal_filter = (
    (df_haz_impact["starttime"] >= df_haz_impact["Start Date"])
    & (df_haz_impact["starttime"] <= df_haz_impact["End Date"])
) | (
    (df_haz_impact["endtime"] >= df_haz_impact["Start Date"])
    & (df_haz_impact["endtime"] <= df_haz_impact["End Date"])
)

df_haz_impact = df_haz_impact[temporal_filter]


# %%df_haz_impact
spatial_filter = gpd.GeoSeries(df_haz_impact["geometry_hazard"]).intersects(
    gpd.GeoSeries(df_haz_impact["geometry_impact"])
)

# %%
df_haz_impact = df_haz_impact[spatial_filter]

## TO DO: Dissolve the ones that have the same disaster number and make list of their magnitudes


# %% TO DO:
gdf_impact = gdf_impact.set_index("Dis No")
df_haz_impact = df_haz_impact.set_index("Dis No")
gdf_impact.loc["eq intensity"] = df_haz_impact["Intensity"]
