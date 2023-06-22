# %% Imports
import pandas as pd
import geopandas as gpd
from my_functions import find_overlapping_hazard
from shapely import wkt

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
]  # available hazards

START_YEAR = 2000
END_YEAR = 2015
HAZARD_PATH = "C:/Users/wja209/DATA/RAW/hazards/"
PROCESSED_HAZARD_PATH = "C:/Users/wja209/DATA/PROCESSED/"
PROCESSED_IMPACT_PATH = (
    "C:/Users/wja209/DATA/PROCESSED/impact_exposure_vulnerability_2000_2015.gpkg"
)
PROCESSED_IMPACT_PATH2_CSV = "C:/Users/wja209/DATA/PROCESSED/impact_hazard_exposure_vulnerability_2000_2015_continuous.csv"
PROCESSED_IMPACT_PATH2 = "C:/Users/wja209/DATA/PROCESSED/impact_hazard_exposure_vulnerability_2000_2015_continuous.gpkg"
PROCESSED_IMPACT_PATH2_GEOM_CSV = "C:/Users/wja209/DATA/PROCESSED/impact_hazard_exposure_vulnerability_2000_2015_geometries_continuous.csv"


# # %% Open all single raw hazard files, truncate to period 2000 - 2015 and save
# for hazard in hazards:
#     print(hazard)
#     df = pd.read_csv(HAZARD_PATH + hazard + ".csv", index_col=0)
#     time_filter = (df["starttime"].str[0:4] >= str(START_YEAR)) & (
#         df["endtime"].str[0:4] <= str(END_YEAR)
#     )
#     df = df[time_filter]
#     # ls and wf do not have intensity, so compute affected area
#     # if (hazard == "ls") | (hazard == "wf") | (hazard == "fl"):
#     # Convert to gdf with temporary geometry column needed to calculated areal extent
#     df["geometry"] = df["Geometry"].apply(wkt.loads)
#     df = gpd.GeoDataFrame(
#         df, crs={"init": "epsg:4326"}, geometry=df["geometry"]
#     ).to_crs(
#         {"init": "epsg:3857"}
#     )  # reproject into planar coordinate system for area calucation
#     # Compute area
#     df["Intensity"] = df["geometry"].area / 10**6
#     # Drop geometry column again so that file format is consistant with other hazard files
#     df.drop("geometry", axis=1, inplace=True)

#     df.to_csv(HAZARD_PATH + hazard + "_2000_2015_continuous.csv", index=False)


# %% Load impact data
gdf_impact_geometries = gpd.read_file(PROCESSED_IMPACT_PATH)
gdf_impact = gdf_impact_geometries.copy()


# # %% Loop through hazards, find overlapping ones and save
# for hazard in hazards:
#     print(hazard)
#     # Load hazard file
#     df_hazard = pd.read_csv(HAZARD_PATH + hazard + "_2000_2015_continuous.csv")

#     # Convert to GeoDataFrame
#     df_hazard["geometry"] = df_hazard["Geometry"].apply(wkt.loads)
#     gdf_hazard = gpd.GeoDataFrame(
#         df_hazard, crs=gdf_impact.crs, geometry=df_hazard["geometry"]
#     )
#     gdf_hazard.drop("Geometry", axis=1, inplace=True)
#     gdf_hazard["starttime"] = pd.to_datetime(gdf_hazard["starttime"], utc=True)
#     gdf_hazard["endtime"] = pd.to_datetime(gdf_hazard["endtime"], utc=True)

#     # Identify overlapping hazards
#     gdf_overlapping_hazards = find_overlapping_hazard(
#         hazard, gdf_hazard, gdf_impact_geometries
#     )

#     # Save
#     gdf_overlapping_hazards.to_file(PROCESSED_HAZARD_PATH + hazard + "_continuous.gpkg")
#     gdf_overlapping_hazards.to_csv(PROCESSED_HAZARD_PATH + hazard + "_continuous.csv")

# %% Loop through overlapping hazards and join hazards with impact
for hazard in hazards:
    print(hazard)

    # Add hazard intensities to impact gdf when spatial footprints overlap
    gdf_overlapping_hazards = (
        gpd.read_file(PROCESSED_HAZARD_PATH + hazard + "_continuous.gpkg")
        .set_index("Dis No")
        .add_suffix("_" + hazard)
    )
    gdf_impact_geometries = gdf_impact_geometries.merge(
        right=gdf_overlapping_hazards, on="Dis No", how="left"
    )
    gdf_impact = gdf_impact.merge(
        right=gdf_overlapping_hazards.drop(columns=["geometry_" + hazard]),
        on="Dis No",
        how="left",
    )

    # Remove rows where hazard could not be matched
    hazard_filter = (
        (gdf_impact["Hazard1"] == hazard)
        | (gdf_impact["Hazard2"] == hazard)
        | (gdf_impact["Hazard3"] == hazard)
    )
    hazard_nan_filter = (
        gdf_impact_geometries["Intensity_" + hazard].isna() & hazard_filter
    )
    gdf_impact_geometries = gdf_impact_geometries[~hazard_nan_filter]
    gdf_impact = gdf_impact[~hazard_nan_filter]

    # Hazard intensities are 0, if hazard did not manifest itself
    # nan_filter = gdf_impact_geometries["Intensity_" + hazard].isna()
    # gdf_impact_geometries.loc[nan_filter, "Intensity_" + hazard] = 0
    # gdf_impact.loc[nan_filter, "Intensity_" + hazard] = 0

# %% Save combined hazard impact with and without geometries for further analysis
gdf_impact_geometries.to_csv(PROCESSED_IMPACT_PATH2_GEOM_CSV, index=False)
gdf_impact.to_file(PROCESSED_IMPACT_PATH2)
gdf_impact.drop(columns="geometry").to_csv(PROCESSED_IMPACT_PATH2_CSV, index=False)
