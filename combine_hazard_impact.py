# %% Imports
import pandas as pd
import geopandas as gpd
from shapely import wkt
import time

# %% Constants
PROCESSED_IMPACT_PATH = (
    "C:/Users/wja209/DATA/PROCESSED/impact_exposure_vulnerability_1990_2015.gpkg"
)

# %% Load data
start = time.time()
gdf_impact = gpd.read_file(PROCESSED_IMPACT_PATH)
end = time.time()
print((end - start) / 60)

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

# %%
gdf_haz_impact = gpd.GeoDataFrame(
    df_haz_impact, crs=crs, geometry=df_haz_impact["geometry_hazard"]
)
gdf_haz2 = gdf_haz_impact.dissolve(
    "Dis No", aggfunc={"Intensity": (lambda x: list(x))}
).add_suffix("_eq")

# %%
gdf_impact = gdf_impact.set_index("Dis No")

# %% Merge hazards with impacts
foo = gdf_impact.join(gdf_haz2, how="left", rsuffix="_eq")


# %%
