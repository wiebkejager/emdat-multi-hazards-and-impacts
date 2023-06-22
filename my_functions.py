import pandas as pd
import geopandas as gpd
from shapely import wkt


def find_overlapping_hazard(
    hazard: str, gdf_hazard: gpd.GeoDataFrame, gdf_impact: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """Create a hazard GeoDataFrame with those hazards that have spatial
    and temporal overlap for the input hazard type. Multiple hazards
    corresponding to the same Dis No are dissolved"""

    # Create filter to select only those rows from gdf_impact that contain hazard
    hazard_filter = (
        (gdf_impact["Hazard1"] == hazard)
        | (gdf_impact["Hazard2"] == hazard)
        | (gdf_impact["Hazard3"] == hazard)
    )

    # Create dataframe with all combinations of hazards and impacts
    df_hazard_impact = gdf_hazard.merge(
        right=gdf_impact[hazard_filter], how="cross", suffixes=["_hazard", "_impact"]
    )

    # Filter hazards with temporal overlap
    temporal_filter = (
        (df_hazard_impact["starttime"] >= df_hazard_impact["Start Date"])
        & (df_hazard_impact["starttime"] <= df_hazard_impact["End Date"])
    ) | (
        (df_hazard_impact["endtime"] >= df_hazard_impact["Start Date"])
        & (df_hazard_impact["endtime"] <= df_hazard_impact["End Date"])
    )
    df_hazard_impact = df_hazard_impact[temporal_filter]

    # Filter hazards with spatial overlap
    spatial_filter = gpd.GeoSeries(df_hazard_impact["geometry_hazard"]).intersects(
        gpd.GeoSeries(df_hazard_impact["geometry_impact"])
    )
    df_hazard_impact = df_hazard_impact[spatial_filter]

    # Create geodataframe and dissolve multi-hazards (of same type) that correspond to same Dis No
    gdf_hazard_impact = gpd.GeoDataFrame(
        df_hazard_impact,
        crs=gdf_impact.crs,
        geometry=df_hazard_impact["geometry_hazard"],
    )
    gdf_hazard_impact = gdf_hazard_impact.dissolve(
        "Dis No", aggfunc={"Intensity": "max"}
    )

    return gdf_hazard_impact
