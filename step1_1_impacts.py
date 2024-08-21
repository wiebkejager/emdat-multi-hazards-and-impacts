###
# This file:
# - Maps EMDAT hazards to natural hazards we are considering
# - Filters EMDAT to relevant events
# - Filters EMDAT & GDIS to relevant time period 2000 - 2018
# - Merges EMDAT & GDIS based on Disaster No
# - Merges cross-boundary events reported in indidivual entries to a single unique event
# - Main output file: PROCESSED_UNIQUE_IMPACT_PATH_CSV

# %% Imports
import pandas as pd
import geopandas as gpd
import numpy as np

# %% Define constants
FIRST_YEAR = 2000
LAST_YEAR = 2018
EM_DAT_PATH = "data/emdat_public_2023_03_31_query_uid-n7b9hv-natural-sisasters.csv"
GDIS_PATH = "data/pend-gdis-1960-2018-disasterlocations-gdb/pend-gdis-1960-2018-disasterlocations.gdb"
PROCESSED_EMDAT_PATH = "data/emdat_" + str(FIRST_YEAR) + "_" + str(LAST_YEAR) + ".csv"
PROCESSED_GDIS_PATH = "data/gdis_" + str(FIRST_YEAR) + "_" + str(LAST_YEAR) + ".gpkg"
PROCESSED_IMPACT_PATH = (
    "data/impact_" + str(FIRST_YEAR) + "_" + str(LAST_YEAR) + ".gpkg"
)
PROCESSED_IMPACT_PATH_CSV = (
    "data/impact_" + str(FIRST_YEAR) + "_" + str(LAST_YEAR) + ".csv"
)
PROCESSED_IMPACT_NO_GEO_PATH_CSV = (
    "data/impact_no_geo_" + str(FIRST_YEAR) + "_" + str(LAST_YEAR) + ".csv"
)
PROCESSED_UNIQUE_IMPACT_PATH_CSV = (
    "data/unique_events_impact_" + str(FIRST_YEAR) + "_" + str(LAST_YEAR) + ".csv"
)

# %% Disater to hazard mappings. These are used to select the relevant events in the emdat data set
disaster_type_to_hazard_map = {
    "Drought": "dr",
    "Flood": "fl",
    "Storm": "ew",
    "Earthquake": "eq",
    "Landslide": "ls",
    "Volcanic activity": "vo",
}

disaster_subtype_to_hazard_map = {
    "Drought": "dr",
    "Riverine flood": "fl",
    "Cold wave": "cw",
    "Convective storm": "ew",
    "Ground movement": "eq",
    "Flash flood": "fl",
    "Coastal flood": "fl",
    "Tropical cyclone": "ew",
    "Avalanche": "ls",
    "Ash fall": "vo",
    "Landslide": "ls",
    "Heat wave": "hw",
    "Mudslide": "ls",
    "Tsunami": "ts",
    "Extra-tropical storm": "ew",
    "Rockfall": "ls",
    "Lava flow": "vo",
    "Pyroclastic flow": "vo",
    "Lahar": "vo",
}

# %%
associated_disaster_to_hazard_map = {
    "Food shortage": "exclude",
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
    "Wildfire": "exclude",
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
    "Volcanic activity": "vo",
    "Fire": "exclude",
    "Epidemic": "exclude",
    "Industrial accidents": "exclude",
    "Insect infestation": "exclude",
    "Rain": "exclude",
    "Pollution": "exclude",
    "Transport accident": "exclude",
    "Earthquake": "eq",
    "Explosion": "exclude",
    "Lightening": "exclude",
    "Fog": "exclude",
    "Intoxication": "exclude",
}

# %% Map Associated 2 to Hazard 3
associated_disaster2_to_hazard_map = {
    "Transport accident": "exclude",
    "Slide (land, mud, snow, rock)": "ls",
    "Surge": "exclude",
    "Famine": "exclude",
    "Food shortage": "exclude",
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
    "Wildfire": "exclude",
    "Industrial accidents": "exclude",
    "Storm": "ew",
    "Epidemic": "exclude",
    "Volcanic activity": "vo",
    "Crop failure": "exclude",
    "Transport accident": "exclude",
    "Water shortage": "exclude",
    "Drought": "dr",
    "Heat wave": "hw",
    "Fog": "exclude",
    "Oil spill": "exclude",
    "Liquefaction": "exclude",
    "Insect infestation": "exclude",
}

# %% Load emdat data
# variable_mapping = pd.read_csv(VAR_MAPPING_PATH, delimiter=";", header=0, index_col=0)
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
        "Dis Mag Value",
        "Dis Mag Scale",
        "Total Deaths",
        "Total Affected",
        "Total Damages, Adjusted ('000 US$')",
        "Country",
        "Continent",
        "ISO",
    },
)

# %% Select events in revelant time period
# Fill missing day values with 1 to enable date conversion when month and year are present. Relevant for droughts and extreme temperature events who are mostly recorded as months &year
df_emdat_raw["Start Day"].fillna(1, inplace=True)
filter_28_days = df_emdat_raw["End Month"] == 2
filter_31_days = (
    (df_emdat_raw["End Month"] == 1)
    & (df_emdat_raw["End Month"] == 3)
    & (df_emdat_raw["End Month"] == 5)
    & (df_emdat_raw["End Month"] == 7)
    & (df_emdat_raw["End Month"] == 8)
    & (df_emdat_raw["End Month"] == 10)
    & (df_emdat_raw["End Month"] == 12)
)
filter_30_days = (
    (df_emdat_raw["End Month"] == 4)
    & (df_emdat_raw["End Month"] == 6)
    & (df_emdat_raw["End Month"] == 9)
    & (df_emdat_raw["End Month"] == 11)
)

df_emdat_raw.loc[filter_28_days, "End Day"].fillna(28, inplace=True)
df_emdat_raw.loc[filter_31_days, "End Day"].fillna(31, inplace=True)
df_emdat_raw.loc[filter_30_days, "End Day"].fillna(30, inplace=True)

# Convert
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

time_filter = (df_emdat_raw["Start Year"] >= FIRST_YEAR) & (
    df_emdat_raw["Start Year"] <= LAST_YEAR
)

df_emdat = df_emdat_raw[time_filter].drop(
    {"Start Year", "Start Month", "Start Day", "End Year", "End Month", "End Day"},
    axis=1,
)

# %% Define Hazard1 and select events with relevant Hazard1
# First use disaster subtype to define Hazard 1
df_emdat.loc[:, "Hazard1"] = df_emdat["Disaster Subtype"].map(
    disaster_subtype_to_hazard_map
)

# For resulting nan's use Type to map Hazard 1
df_emdat.loc[df_emdat["Hazard1"].isna(), "Hazard1"] = df_emdat[
    df_emdat["Hazard1"].isna()
]["Disaster Type"].map(disaster_type_to_hazard_map)
# For remaining nan's drop rows.
df_emdat = df_emdat[~df_emdat["Hazard1"].isna()]

# %% Define Hazard2 and select events with relevant Hazard2
df_emdat.loc[:, "Hazard2"] = df_emdat["Associated Dis"].map(
    associated_disaster_to_hazard_map
)
#  Drop rows with exclude
df_emdat = df_emdat[df_emdat["Hazard2"] != "exclude"]

# %% Define Hazard3 and select events with relevant Hazard3
df_emdat.loc[:, "Hazard3"] = df_emdat["Associated Dis2"].map(
    associated_disaster2_to_hazard_map
)
#  Drop rows with exclude
df_emdat = df_emdat[df_emdat["Hazard3"] != "exclude"]


# %% Process "Dis No" to fit "disasterno" in gdis file
df_emdat["ISO"] = (
    df_emdat["ISO"]
    .fillna(df_emdat["Dis No"].str.replace("[\W\d_]", "", regex=True))
    .str.replace(" (the)", "")
)
country_iso_mapping = dict(
    (x, y) for x, y in df_emdat.groupby(["Country", "ISO"]).apply(list).index.values
)

# %% Save processed emdat data file
df_emdat.to_csv(PROCESSED_EMDAT_PATH, index=False)


# %% Process GDIS file to include relevant time period and hazards and save
# Load
gdf_gdis_raw = gpd.read_file(GDIS_PATH)

# %%
# Replace iso in gdis that are not in emdat with nan
iso_indicator = ~gdf_gdis_raw["iso3"].isin(df_emdat["ISO"])
gdf_gdis_raw.loc[iso_indicator, "iso3"] = np.nan
# %%
# Create new ISO variable with filled nans as much as possible
gdf_gdis_raw["ISO"] = gdf_gdis_raw["iso3"].fillna(
    gdf_gdis_raw["country"].map(country_iso_mapping)
)

# Create new Dis No variable in same format as emdat data set
gdf_gdis_raw["Dis No"] = gdf_gdis_raw["disasterno"] + "-" + gdf_gdis_raw["ISO"]

# %%
# Drop all data that is not in filtered emdat data set
gdf_dropped_gdis_raw = gdf_gdis_raw[~gdf_gdis_raw["Dis No"].isin(df_emdat["Dis No"])][
    ["Dis No", "geometry"]
]

# %%
gdf_gdis_raw = gdf_gdis_raw[gdf_gdis_raw["Dis No"].isin(df_emdat["Dis No"])][
    ["Dis No", "geometry"]
]

# %%
# Aggregate to 1 geometry per disaster event
gdf_gdis_2000_2018 = gdf_gdis_raw.dissolve("Dis No")
gdf_gdis_2000_2018_dis_no = gdf_gdis_raw["Dis No"].unique()

# Save processed gdis file
gdf_gdis_2000_2018.to_file(PROCESSED_GDIS_PATH, driver="GPKG")

# %%
filter_geom = df_emdat["Dis No"].isin(gdf_gdis_2000_2018_dis_no)
df_emdat.loc[filter_geom, "geom"] = 1

# %%
df_emdat.to_csv(PROCESSED_EMDAT_PATH, index=False)

# # %% Alternatively load processed gdis file
# gdf_gdis_2000_2018 = gpd.read_file(PROCESSED_GDIS_PATH)

# %% Merge impact with disaster locations
gdf_impact = gdf_gdis_2000_2018.merge(right=df_emdat, how="inner", on="Dis No")

# %% Calculated affected area
# gdf_impact["Affected Area"] = (
#     gdf_impact.to_crs({"init": "epsg:3857"})["geometry"].area / 10**6
# )

# %% Save merged file
# Drop more columns and save short (standard) version
df_impact_short = gdf_impact.drop(
    columns=["Disaster Type", "Disaster Subtype"],
    axis=1,
)

# %%
df_impact_short.to_file(PROCESSED_IMPACT_PATH)

# %%
df_impact_short.to_csv(PROCESSED_IMPACT_PATH_CSV, sep=";", index=True)

# %%
