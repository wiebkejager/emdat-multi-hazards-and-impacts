#%% Imports
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import rasterio
import rasterio.plot
from rasterio import features
import matplotlib.pyplot 
import numpy as np
import xarray as xr
import rioxarray

#%% Constants
EM_DAT_PATH = "C:/Users/wja209/OneDrive - Vrije Universiteit Amsterdam/Research/Paper 1 - Ruoying/Data/EM-DAT/emdat_public_2023_03_31_query_uid-n7b9hv-natural-sisasters.csv"
HAZ_PATH = "C:/Users/wja209/OneDrive - Vrije Universiteit Amsterdam/Research/Paper 1 - Ruoying/Data/MYRIAD-HESA example data/MYRIAD-HES_simple.csv"
#EXP_PATH = "C:/Users/wja209/OneDrive - Vrije Universiteit Amsterdam/Research/Paper 1 - Ruoying/Data/GHS_POP_E2020_GLOBE_R2023A_4326_30ss_V1_0/GHS_POP_E2020_GLOBE_R2023A_4326_30ss_V1_0.tif.ovr"
EXP_PATH = "C:/Users/wja209/OneDrive - Vrije Universiteit Amsterdam/Research/Paper 1 - Ruoying/Data/gpw-v4-population-count-rev11_2020_2pt5_min_tif/gpw_v4_population_count_rev11_2020_2pt5_min.tif"
VUL_PATH = "C:/Users/wja209/OneDrive - Vrije Universiteit Amsterdam/Research/Paper 1 - Ruoying/Data/doi_10.5061_dryad.dk1j0__v2/GDP_per_capita_PPP_1990_2015_v2.nc"

# ### IMPACT
#%% Load data
df_em_dat_raw = pd.read_csv(EM_DAT_PATH, delimiter= ';')

#%%
df_em_dat_raw["Start Date"] = pd.to_datetime(df_em_dat_raw[['Start Year', 'Start Month', 'Start Day']].rename(columns = {'Start Year':'year', 'Start Month': 'month', 'Start Day': 'day'}))
df_em_dat_raw["End Date"] = pd.to_datetime(df_em_dat_raw[['End Year', 'End Month', 'End Day']].rename(columns = {'End Year':'year', 'End Month': 'month', 'End Day': 'day'}))
df_em_dat_raw.Latitude = df_em_dat_raw.Latitude.str.replace('\D', '', regex=True).astype("float")
df_em_dat_raw.Longitude = df_em_dat_raw.Longitude.str.replace('\D', '', regex=True).astype("float")


point = [Point(xy) for xy in zip(df_em_dat_raw.Latitude, df_em_dat_raw.Longitude)]


# %%
gdf_em_dat = gpd.GeoDataFrame(
    df_em_dat_raw[[
    "Start Date", 
    "End Date",
    "Total Affected",
    "Country", 
    "Disaster Type", 
    "Associated Dis",
    "Associated Dis2"
]], geometry=point, crs="EPSG:4326"
)


### HAZARD
# %%
df_haz_raw = pd.read_csv(HAZ_PATH, delimiter= ',')

# %%
df_haz = df_haz_raw[[
    "starttime", 
    "endtime",
    "Hazard", 
    "Intensity",
    "Unit",
    "event",
    "minlon",
    "minlat",
    "maxlon",
    "maxlat"
]].rename(columns={
    "starttime": "Start Date", 
    "endtime": "End Date"
    })

# %% Create spatial dataframe

point1 = [Point(xy) for xy in zip(df_haz_raw.minlon, df_haz_raw.minlat)]
point2 = [Point(xy) for xy in zip(df_haz_raw.minlon, df_haz_raw.maxlat)]
point3 = [Point(xy) for xy in zip(df_haz_raw.maxlon, df_haz_raw.maxlat)]
point4 = [Point(xy) for xy in zip(df_haz_raw.maxlon, df_haz_raw.minlat)]

poly = [Polygon(x) for x in zip(point1, point2, point3, point4)]

gdf_haz = gpd.GeoDataFrame(
    df_haz, geometry=poly, crs="EPSG:4326"
).drop(["minlat", "minlon", "maxlat", "maxlon"], axis = 1)

gdf_haz.plot('Hazard')

# %% Add buffer
# buffer = 0.1
# gdf_haz.geometry = gdf_haz.geometry.buffer(0.2)

### EXPOSURE
# %%
ds_exp = rioxarray.open_rasterio(EXP_PATH)

#%%
ds_exp.plot(robust = True, vmin = 0, vmax = 1000)

### VULNERABILITY
# %%
ds_vul = rioxarray.open_rasterio(VUL_PATH)

#%%
ds_vul.isel(time= 0).plot(robust = True)

#%% Perform analysis for first hazard. 
flood_geom = gdf_haz.loc[5,:]['geometry']
# Crop the raster data with the bounding box of fields, using ".rio.clip_box"

# %%
ds_exp_clip_box = ds_exp.rio.clip_box(*flood_geom.bounds)
ds_exp_clip_box.plot(robust = True, vmin = 0, vmax = 1000)



# %%