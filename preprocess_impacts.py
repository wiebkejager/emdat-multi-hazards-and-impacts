# %% Imports
import pandas as pd
import geopandas as gpd
from funs import has_overlap_in_time

# %% Define constants
START_YEAR = 2000
END_YEAR = 2015
VAR_MAPPING_PATH = "C:/Users/wja209/DATA/RAW/hazard-variable-mapping.csv"
EM_DAT_PATH = "C:/Users/wja209/DATA/RAW/EM-DAT/emdat_public_2023_03_31_query_uid-n7b9hv-natural-sisasters.csv"
GDIS_PATH = "C:/Users/wja209/DATA/RAW/pend-gdis-1960-2018-disasterlocations-gdb/pend-gdis-1960-2018-disasterlocations.gdb"
GDIS_CSV_PATH = "C:/Users/wja209/DATA/RAW/pend-gdis-1960-2018-disasterlocations-gdb/pend-gdis-1960-2018-disasterlocations.csv"
PROCESSED_IMPACT_PATH = "C:/Users/wja209/DATA/PROCESSED/impact_1990_2015.gpkg"
PROCESSED_GDIS_PATH = "C:/Users/wja209/DATA/PROCESSED/gdis_1990_2015.gpkg"
PROCESSED_EMDAT_PATH = "C:/Users/wja209/DATA/PROCESSED/emdat_1990_2015.csv"


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
# %% Save
df_emdat.to_csv(PROCESSED_EMDAT_PATH)

# %% Load GDIS data
# df_gdis_raw = gpd.read_file(GDIS_PATH)

# # %%
# df_gdis_raw["ISO"] = df_gdis_raw["iso3"].fillna(
#     df_gdis_raw["country"].map(country_iso_mapping)
# )

# # %%
# df_gdis_raw["Dis No"] = df_gdis_raw["disasterno"] + "-" + df_gdis_raw["ISO"]
# df_gdis_raw = df_gdis_raw[df_gdis_raw["Dis No"].isin(df_emdat["Dis No"])][
#     ["Dis No", "geometry"]
# ]

# df_gdis_1990_2015 = df_gdis_raw.dissolve("Dis No")
# df_gdis_1990_2015.to_file("foo.gpkg", driver="GPKG")
# df_gdis_1990_2015.to_file("foo.geojson", driver="GeoJSON")


# %%
df_gdis_1990_2015 = gpd.read_file(PROCESSED_GDIS_PATH)

# %% Merge impact with disaster locations
df_impact = df_gdis_1990_2015.merge(right=df_emdat, how="inner", on="Dis No")

# %% Save merged file
df_impact.to_file(PROCESSED_IMPACT_PATH)
