# %% Imports
import geopandas as gpd
import pandas as pd
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
df_impact["geometry"] = wkt.loads(df_impact["geometry"])
gdf_impact = gpd.GeoDataFrame(df_impact, crs="epsg:4326")

# %%
# Event 1: "2002-0048-RUS"
# Event 2: "2000-0830-POL"


# %% Check identification algorithm
event1 = gdf_impact.loc[["2002-0048-RUS"]]
event2 = gdf_impact.loc[["2000-0830-POL"]]
events = gdf_impact.loc[["2002-0048-RUS", "2000-0830-POL"]]

# Check spatial overlap
if event1.intersects(event2, align=False).values[0]:
    if event1.touches(event2, align=False).values[0] > 0:
        print("touches")
    else:
        print("intersects")


# %%
events.plot(color="palegreen", edgecolor="red")
event1.plot(color="palegreen", edgecolor="red")
event2.plot(color="palegreen", edgecolor="red")
# %%
