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
START_YEAR = 2000
END_YEAR = 2015
VAR_MAPPING_PATH = "C:/Users/wja209/OneDrive - Vrije Universiteit Amsterdam/Research/Paper 1 - Ruoying/Data/hazard-variable-mapping.csv"
EM_DAT_PATH = "C:/Users/wja209/OneDrive - Vrije Universiteit Amsterdam/Research/Paper 1 - Ruoying/Data/EM-DAT/emdat_public_2023_03_31_query_uid-n7b9hv-natural-sisasters.csv"
GDIS_PATH = "C:/Users/wja209/OneDrive - Vrije Universiteit Amsterdam/Research/Paper 1 - Ruoying/Data/pend-gdis-1960-2018-disasterlocations-gdb/pend-gdis-1960-2018-disasterlocations.gdb"
GDIS_CSV_PATH = "C:/Users/wja209/OneDrive - Vrije Universiteit Amsterdam/Research/Paper 1 - Ruoying/Data/pend-gdis-1960-2018-disasterlocations-gdb/pend-gdis-1960-2018-disasterlocations.csv"

# %% Load emdat data
variable_mapping = pd.read_csv(VAR_MAPPING_PATH, delimiter=";", header=0, index_col=0)
df_emdat_raw = pd.read_csv(
    EM_DAT_PATH,
    delimiter=";",
    header=0,
    usecols={
        "Dis No",
        "Start Year",
        "Start Month",
        "Start Day",
        "End Year",
        "End Month",
        "End Day",
        "Disaster Type",
        "Disaster Subtype",
        "Associated Dis",
        "Associated Dis2",
        "Total Affected",
        "Country",
        "ISO",
        "Region",
        "Continent",
        "Latitude",
        "Longitude",
    },
)

df_emdat_raw["Start Date"] = pd.to_datetime(
    df_emdat_raw[["Start Year", "Start Month", "Start Day"]].rename(
        columns={"Start Year": "year", "Start Month": "month", "Start Day": "day"}
    ),
    utc=True,
)
df_emdat_raw["End Date"] = pd.to_datetime(
    df_emdat_raw[["End Year", "End Month", "End Day"]].rename(
        columns={"End Year": "year", "End Month": "month", "End Day": "day"}
    ),
    utc=True,
)


# %% Cut emdat to relevant time period and hazards
time_filter = (df_emdat_raw["Start Year"] >= START_YEAR) & (
    df_emdat_raw["End Year"] <= END_YEAR
)
disaster_type_filter = df_emdat_raw["Disaster Type"].isin(
    variable_mapping["Disaster Type"]
)
# disaster_subtype_filter = df_emdat_raw["Disaster Subtype"].isin(
#     variable_mapping["Disaster Subtype"]
# )

df_emdat = df_emdat_raw[time_filter & disaster_type_filter].drop(
    {"Start Year", "Start Month", "Start Day", "End Year", "End Month", "End Day"},
    axis=1,
)

df_emdat["ISO"] = (
    df_emdat["ISO"]
    .fillna(df_emdat["Dis No"].str.replace("[\W\d_]", "", regex=True))
    .str.replace(" (the)", "")
)

country_iso_mapping = dict(
    (x, y) for x, y in df_emdat.groupby(["Country", "ISO"]).apply(list).index.values
)


# %% Load GDIS data
df_gdis_raw = gpd.read_file(GDIS_PATH)


# # %%Save as csv

# pd.DataFrame(
#     df_gdis_raw.assign(geometry=df_gdis_raw["geometry"].apply(lambda p: p.wkt))
# ).to_csv(GDIS_CSV_PATH)


# %%
df_gdis_raw["ISO"] = df_gdis_raw["iso3"].fillna(
    df_gdis_raw["country"].map(country_iso_mapping)
)


# %%
df_gdis_raw["Dis No"] = df_gdis_raw["disasterno"] + "-" + df_gdis_raw["iso3"]

# %%
df_impact_raw = df_emdat.merge(right=df_gdis_raw, how="inner", on="Dis No")


# %% Constants
# GDIS_PATH = "C:/Users/wja209/OneDrive - Vrije Universiteit Amsterdam/Research/Paper 1 - Ruoying/Data/pend-gdis-1960-2018-disasterlocations-gpkg/pend-gdis-1960-2018-disasterlocations.gpkg"
# GDIS_PATH = "C:/Users/wja209/OneDrive - Vrije Universiteit Amsterdam/Research/Paper 1 - Ruoying/Data/EM-DAT/pend-gdis-1960-2018-disasterlocations.csv"#
HAZ_PATH = "C:/Users/wja209/DATA/myriad/dr.csv"
# HAZ_PATH = "C:/Users/wja209/OneDrive - Vrije Universiteit Amsterdam/Research/Paper 1 - Ruoying/Data/MYRIAD-HESA example data/MYRIAD-HES_simple.csv"
# EXP_PATH = "C:/Users/wja209/OneDrive - Vrije Universiteit Amsterdam/Research/Paper 1 - Ruoying/Data/GHS_POP_E2020_GLOBE_R2023A_4326_30ss_V1_0/GHS_POP_E2020_GLOBE_R2023A_4326_30ss_V1_0.tif.ovr"
EXP_PATH = "C:/Users/wja209/OneDrive - Vrije Universiteit Amsterdam/Research/Paper 1 - Ruoying/Data/gpw-v4-population-count-rev11_2020_2pt5_min_tif/gpw_v4_population_count_rev11_2020_2pt5_min.tif"
VUL_PATH = "C:/Users/wja209/OneDrive - Vrije Universiteit Amsterdam/Research/Paper 1 - Ruoying/Data/doi_10.5061_dryad.dk1j0__v2/GDP_per_capita_PPP_1990_2015_v2.nc"
COUNTRIES_PATH = "C:/Users/wja209/DATA/world-administrative-boundaries.geojson"

### HAZARD
# %%
df_haz_raw = pd.read_csv(HAZ_PATH, index_col=0).drop(columns=["index1", "Id"])

# df_haz_raw['Geometry'] = pygeos.from_wkt(df_haz_raw['Geometry']) #format Geometry

df_haz_raw["geometry"] = df_haz_raw["Geometry"].apply(wkt.loads)

crs = {"init": "EPSG:4326"}
gdf_haz = gpd.GeoDataFrame(df_haz_raw, crs=crs, geometry=df_haz_raw["geometry"])
gdf_haz.drop("Geometry", axis=1, inplace=True)
gdf_haz["starttime"] = pd.to_datetime(
    df_haz_raw["starttime"], utc=True
)  # format starttime
gdf_haz["endtime"] = pd.to_datetime(df_haz_raw["endtime"], utc=True)  # format endtime
gdf_haz["hazard"] = "dr"

# %%
gdf_haz.plot(column="Intensity", cmap="OrRd", legend=True, vmax=0)

# %%
mintime = gdf_haz["starttime"].min()

# %%
## Countries
df_countries = gpd.read_file(COUNTRIES_PATH)
df_countries = df_countries[["iso3", "name", "geometry"]].rename(
    columns={"geometry": "country_geometry", "name": "Country"}
)

# ### IMPACT
# %% Load data

# df_gdis_raw = pd.read_csv(GDIS_PATH, delimiter= ',')

# %%
# df_gdis_raw = gpd.read_file(GDIS_PATH)

# %%
# df_gdis_raw["Dis No"] = df_gdis_raw['disasterno'] + "-" + df_gdis_raw['iso3']

# %%
# df_gdis_raw = df_gdis_raw[['Dis No', 'latitude', 'longitude']].rename(columns = {'latitude': 'gdis_latitude', 'longitude': 'gdis_longitude'})

# %%
df_em_dat_raw["Start Date"] = pd.to_datetime(
    df_em_dat_raw[["Start Year", "Start Month", "Start Day"]].rename(
        columns={"Start Year": "year", "Start Month": "month", "Start Day": "day"}
    ),
    utc=True,
)
df_em_dat_raw["End Date"] = pd.to_datetime(
    df_em_dat_raw[["End Year", "End Month", "End Day"]].rename(
        columns={"End Year": "year", "End Month": "month", "End Day": "day"}
    ),
    utc=True,
)
df_em_dat_raw.Latitude = df_em_dat_raw.Latitude.str.replace(
    "\D", "", regex=True
).astype("float")
df_em_dat_raw.Longitude = df_em_dat_raw.Longitude.str.replace(
    "\D", "", regex=True
).astype("float")
df_em_dat_raw = df_em_dat_raw[
    [
        "Dis No",
        "Start Date",
        "End Date",
        "Total Affected",
        "Country",
        "Disaster Type",
        "Associated Dis",
        "Associated Dis2",
        "Latitude",
        "Longitude",
    ]
].rename(columns={"Start Date": "starttime", "End Date": "endtime"})

# %% merge
df_impact_raw = df_em_dat_raw.merge(right=df_gdis_raw, how="left", on="Dis No")

# %%
df_impact_raw = df_impact_raw.merge(right=df_countries, how="left", on="Country")


# %%
# filter impacts on hazard type and min time
time_filter = df_impact_raw["starttime"] >= mintime
hazard_filter = df_impact_raw["Disaster Type"] == "Drought"
df_impact = df_impact_raw[time_filter & hazard_filter]
df_impact["best_geometry"] = df_impact["country_geometry"]

# %% filter on location
gdf_impact = gpd.GeoDataFrame(
    df_impact, geometry=df_impact["best_geometry"], crs="EPSG:4326"
)

# %%
gdf_impact.plot()

# %% create cross product hazard & impact, check if intersect, drop non-intersecting
gdf_haz = gdf_haz.add_suffix("_hazard")
gdf_impact = gdf_impact.add_suffix("_impact")
df_haz_impact = gdf_haz.merge(
    right=gdf_impact, how="cross", suffixes=["_hazard", "_impact"]
)


# %%df_haz_impact
spatial_filter = gpd.GeoSeries(df_haz_impact["geometry_hazard"]).intersects(
    gpd.GeoSeries(df_haz_impact["geometry_impact"])
)
df_haz_impact = df_haz_impact[spatial_filter]

# %%
temporal_filter = df_haz_impact.apply(
    lambda x: has_overlap_in_time(
        x["starttime_hazard"],
        x["endtime_hazard"],
        x["starttime_impact"],
        x["endtime_impact"],
    ),
    axis=1,
)
df_haz_impact = df_haz_impact[temporal_filter]


# %% Split into a hazard and an impact gdf for plotting
gdf_haz2 = gpd.GeoDataFrame(
    df_haz_impact, geometry=df_haz_impact["geometry_hazard"], crs="EPSG:4326"
)
gdf_imp2 = gpd.GeoDataFrame(
    df_haz_impact, geometry=df_haz_impact["geometry_impact"], crs="EPSG:4326"
)

# %% Plot?
fig, ax = plt.subplots(figsize=(15, 15))
gdf_haz2.plot(ax=ax, column="Intensity_hazard", cmap="OrRd")
gdf_imp2.boundary.plot(ax=ax, edgecolor="black")


# %% Merge if several hazards relate to the same disaster number


# %%
# #%%
# point = [Point(xy) for xy in zip(df_em_dat_raw.Latitude, df_em_dat_raw.Longitude)]

# # %%
# gdf_em_dat = gpd.GeoDataFrame(
#     df_em_dat_raw[[
#     "Start Date",
#     "End Date",
#     "Total Affected",
#     "Country",
#     "Disaster Type",
#     "Associated Dis",
#     "Associated Dis2"
# ]], geometry=point, crs="EPSG:4326"
# )


# %% Linked impact & hazard data frame


# %%
# # %%
# df_haz = df_haz_raw[[
#     "starttime",
#     "endtime",
#     "Hazard",
#     "Intensity",
#     "Unit",
#     "event",
#     "minlon",
#     "minlat",
#     "maxlon",
#     "maxlat"
# ]].rename(columns={
#     "starttime": "Start Date",
#     "endtime": "End Date"
#     })

# # %% Create spatial dataframe

# point1 = [Point(xy) for xy in zip(df_haz_raw.minlon, df_haz_raw.minlat)]
# point2 = [Point(xy) for xy in zip(df_haz_raw.minlon, df_haz_raw.maxlat)]
# point3 = [Point(xy) for xy in zip(df_haz_raw.maxlon, df_haz_raw.maxlat)]
# point4 = [Point(xy) for xy in zip(df_haz_raw.maxlon, df_haz_raw.minlat)]

# poly = [Polygon(x) for x in zip(point1, point2, point3, point4)]

# gdf_haz = gpd.GeoDataFrame(
#     df_haz, geometry=poly, crs="EPSG:4326"
# ).drop(["minlat", "minlon", "maxlat", "maxlon"], axis = 1)

# gdf_haz.plot('Hazard')

# %% Add buffer
# buffer = 0.1
# gdf_haz.geometry = gdf_haz.geometry.buffer(0.2)

### EXPOSURE
# %%
ds_exp = rioxarray.open_rasterio(EXP_PATH)

# %%
ds_exp.plot(robust=True, vmin=0, vmax=1000)

### VULNERABILITY
# %%
ds_vul = rioxarray.open_rasterio(VUL_PATH)

# %%
ds_vul.isel(time=0).plot(robust=True)

# %% Perform analysis for first hazard.
flood_geom = gdf_haz.loc[5, "geometry"]
# Crop the raster data with the bounding box of fields, using ".rio.clip_box"

# %%
ds_exp_clip_box = ds_exp.rio.clip_box(*flood_geom.bounds)
ds_exp_clip_box.plot(robust=True, vmin=0, vmax=1000)

# %%
fields_rasterized = features.rasterize(
    shapes=[flood_geom], out_shape=ds_exp.shape[1:3], transform=ds_exp.rio.transform()
)
plt.imshow(fields_rasterized, vmax=1000)
plt.colorbar()
# %%
