# %% Imports
import geopandas as gpd
import pandas as pd
import datetime
import json
from shapely import wkt

# %% Define constants
FIRST_YEAR = 2000
LAST_YEAR = 2018
PROCESSED_UNIQUE_IMPACT_PATH_CSV = (
    "data/unique_events_impact_" + str(FIRST_YEAR) + "_" + str(LAST_YEAR) + ".csv"
)

# %% Load impact data
df_impact = pd.read_csv(PROCESSED_UNIQUE_IMPACT_PATH_CSV, sep=";", index_col=0)

# %%
df_impact["Start Date"] = pd.to_datetime(df_impact["Start Date"])
df_impact["End Date"] = pd.to_datetime(df_impact["End Date"])

# %%
df_impact["geometry"] = wkt.loads(df_impact["geometry"])
gdf_impact = gpd.GeoDataFrame(df_impact, crs="epsg:4326")


# %% Read data
df_spatially_overlapping_events = pd.read_csv(
    "data/df_spatially_overlapping_events.csv", sep=";", index_col=0
)

# %% temporal overlap
temporal_buffer = datetime.timedelta(days=30)
df_s_t_overlapping_events = df_spatially_overlapping_events.copy(deep=True)

# %%
for ix, row in df_s_t_overlapping_events.iterrows():
    start_event = gdf_impact.loc[ix]["Start Date"] - temporal_buffer
    end_event = gdf_impact.loc[ix]["End Date"] + temporal_buffer
    overlapping_events = []
    for row_element in json.loads(row["Overlapping events"]):
        start_ol_event = gdf_impact.loc[row_element]["Start Date"]
        end_ol_event = gdf_impact.loc[row_element]["End Date"]
        overlap_criterion = (
            (start_ol_event >= start_event) & (start_ol_event <= end_event)
        ) | ((end_ol_event >= start_event) & (end_ol_event <= end_event))
        if overlap_criterion:
            overlapping_events.append(row_element)
    df_s_t_overlapping_events.loc[ix]["Overlapping events"] = json.dumps(
        overlapping_events
    )

# %%
df_s_t_overlapping_events.to_csv(
    "data/df_s_t_overlapping_events.csv", sep=";", index=True
)
# %%
