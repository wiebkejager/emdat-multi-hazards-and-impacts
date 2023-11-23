# %% Imports
import pandas as pd
import geopandas as gpd

# %% Define constants
FIRST_YEAR = 2000
LAST_YEAR = 2015
EM_DAT_PATH = "C:/Users/wja209/DATA/RAW/EM-DAT/emdat_public_2023_03_31_query_uid-n7b9hv-natural-sisasters.csv"
GDIS_PATH = "C:/Users/wja209/DATA/RAW/pend-gdis-1960-2018-disasterlocations-gdb/pend-gdis-1960-2018-disasterlocations.gdb"
GDIS_CSV_PATH = "C:/Users/wja209/DATA/RAW/pend-gdis-1960-2018-disasterlocations-gdb/pend-gdis-1960-2018-disasterlocations.csv"
PROCESSED_IMPACT_PATH_EXT = "C:/Users/wja209/DATA/PROCESSED/impact_2000_2015_ext.gpkg"
PROCESSED_IMPACT_PATH = "C:/Users/wja209/DATA/PROCESSED/impact_2000_2015.gpkg"
PROCESSED_GDIS_PATH = "C:/Users/wja209/DATA/PROCESSED/gdis_2000_2015.gpkg"
PROCESSED_EMDAT_PATH = "C:/Users/wja209/DATA/PROCESSED/emdat_2000_2015.csv"
PROCESSED_IMPACT_CSVPATH_EXT = "C:/Users/wja209/DATA/PROCESSED/impact_2000_2015.csv"

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
df_emdat_raw["End Day"].fillna(1, inplace=True)

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


# # %% Process GDIS file to include relevant time period and hazards and save
# # Load
# gdf_gdis_raw = gpd.read_file(GDIS_PATH)

# # %%
# # Create new ISO variable with filled nans as much as possible
# gdf_gdis_raw["ISO"] = gdf_gdis_raw["iso3"].fillna(
#     gdf_gdis_raw["country"].map(country_iso_mapping)
# )

# # Create new Dis No variable in same format as emdat data set
# gdf_gdis_raw["Dis No"] = gdf_gdis_raw["disasterno"] + "-" + gdf_gdis_raw["ISO"]

# # Drop all data that is not in filtered emdat data set
# gdf_gdis_raw = gdf_gdis_raw[gdf_gdis_raw["Dis No"].isin(df_emdat["Dis No"])][
#     ["Dis No", "geometry"]
# ]

# # Aggregate to 1 geometry per disaster event
# gdf_gdis_2000_2015 = gdf_gdis_raw.dissolve("Dis No")

# # Save processed gdis file
# gdf_gdis_2000_2015.to_file(PROCESSED_GDIS_PATH, driver="GPKG")

# %% Alternatively load processed gdis file
gdf_gdis_2000_2015 = gpd.read_file(PROCESSED_GDIS_PATH)

# %% Merge impact with disaster locations
gdf_impact = gdf_gdis_2000_2015.merge(right=df_emdat, how="inner", on="Dis No")

# %% Calculated affected area
gdf_impact["Affected Area"] = (
    gdf_impact.to_crs({"init": "epsg:3857"})["geometry"].area / 10**6
)

# %% Save merged file
# Save extended version.
gdf_impact.to_file(PROCESSED_IMPACT_PATH_EXT)

# %%
# Drop more columns and save short (standard) version
df_impact_short = gdf_impact.drop(
    columns=["Disaster Type", "Disaster Subtype", "Associated Dis", "Associated Dis2"],
    axis=1,
)

# %%
df_impact_short.to_file(PROCESSED_IMPACT_PATH)
