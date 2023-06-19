import pandas as pd
import geopandas as gpd
from shapely import wkt


def find_overlapping_hazard(
    hazard: str, HAZARD_PATH: str, gdf_impact: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """Create a hazard GeoDataFrame with those hazards that have spatial
    and temporal overlap for the input hazard type. Multiple hazards
    corresponding to the same Dis No are dissolved"""

    # Load hazard file
    df_hazard = pd.read_csv(HAZARD_PATH + hazard + "_1990_2015.csv")

    # Transform to GeoDataFrame and set data types for columns
    df_hazard["geometry"] = df_hazard["Geometry"].apply(wkt.loads)
    gdf_haz = gpd.GeoDataFrame(
        df_hazard, crs=gdf_impact.crs, geometry=df_hazard["geometry"]
    )
    gdf_haz.drop("Geometry", axis=1, inplace=True)
    gdf_haz["starttime"] = pd.to_datetime(gdf_haz["starttime"], utc=True)
    gdf_haz["endtime"] = pd.to_datetime(gdf_haz["endtime"], utc=True)

    # Create filter to select only those rows from gdf_impact that contain hazard
    hazard_filter = (
        (gdf_impact["Hazard1"] == hazard)
        | (gdf_impact["Hazard2"] == hazard)
        | (gdf_impact["Hazard3"] == hazard)
    )

    # Create dataframe with all combinations of hazards and impacts
    df_haz_impact = gdf_haz.merge(
        right=gdf_impact[hazard_filter], how="cross", suffixes=["_hazard", "_impact"]
    )

    # Filter out hazards without temporal overlap
    temporal_filter = (
        (df_haz_impact["starttime"] >= df_haz_impact["Start Date"])
        & (df_haz_impact["starttime"] <= df_haz_impact["End Date"])
    ) | (
        (df_haz_impact["endtime"] >= df_haz_impact["Start Date"])
        & (df_haz_impact["endtime"] <= df_haz_impact["End Date"])
    )
    df_haz_impact = df_haz_impact[temporal_filter]

    # Filter out hazards with out spatial overlap
    spatial_filter = gpd.GeoSeries(df_haz_impact["geometry_hazard"]).intersects(
        gpd.GeoSeries(df_haz_impact["geometry_impact"])
    )
    df_haz_impact = df_haz_impact[spatial_filter]

    # Create geodataframe and dissolve multi-hazards (of same type) that correspond to same Dis No
    gdf_haz_impact = gpd.GeoDataFrame(
        df_haz_impact, crs=gdf_impact.crs, geometry=df_haz_impact["geometry_hazard"]
    )
    gdf_haz_impact = gdf_haz_impact.dissolve("Dis No", aggfunc={"Intensity": "max"})

    return gdf_haz_impact
