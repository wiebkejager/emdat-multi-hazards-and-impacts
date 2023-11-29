import pandas as pd
import geopandas as gpd
from shapely import wkt


def get_bs_sample_df(df: pd.DataFrame, haz: str) -> pd.DataFrame:
    filter = (
        df.loc[:, "eventtype_detailed"] == haz
    )  # get indices of data rows that correspond to hazard of interest
    df_filtered = df.loc[filter]  # get data rows that correspond to hazard
    n_bs = len(df_filtered)  # size of bootstrap sample
    df_new = df_filtered.sample(
        n_bs, replace=True
    )  # create bootstrap sample of size n_bs
    return df_new


# %%
def get_impact_mean(df_haz: pd.DataFrame, impact_var: str) -> float:
    impact_mean = df_haz[impact_var].mean()
    return impact_mean


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


# rom rtree import index
from shapely.geometry import shape


def find_intersecting_polygons(xs: gpd.GeoSeries, ys: gpd.GeoSeries) -> pd.Series:
    """Return indices of xs and ys that have spatial overlap"""

    intersect_indices = []

    xs_spatial_index = xs.sindex

    for iy, y in ys.iterows():
        xs_possible_matches_index = list(
            xs_spatial_index.intersection(y["geometry"].bounds)
        )
        xs_possible_matches = xs.iloc[xs_possible_matches_index]
        xs_precise_match_index = xs_possible_matches.intersects(y["geometry"])
        if xs_precise_match_index:
            intersect_indices.append([xs_precise_match_index, iy])

    return intersect_indices


from shapely.strtree import STRtree


def find_intersecting_polygons2(
    gdf_x: gpd.GeoDataFrame, gdf_y: gpd.GeoDataFrame
) -> list:
    """Return indices of xs and ys that have spatial overlap"""

    intersect_indices = []

    tree = STRtree(gdf_x["geometry"])

    for iy, rowy in gdf_y.iterows():
        xs_match_index = tree.query(rowy["geometry"])
        if xs_match_index:
            intersect_indices.append([xs_match_index, iy])

    return intersect_indices


def merge_gdfs_based_on_intersect_indices(
    gdf_x: gpd.GeoDataFrame, gdf_y: gpd.GeoDataFrame, intersect_indices: list
) -> gpd.GeoDataFrame:
    gdf_x
