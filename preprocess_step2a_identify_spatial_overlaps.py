# %% Imports
import geopandas as gpd
import pandas as pd
import itertools
import threading
import json
from shapely import wkt
import time
import numpy as np

# %% Define constants
FIRST_YEAR = 2000
LAST_YEAR = 2018
PROCESSED_IMPACT_PATH_CSV = (
    "data/impact_" + str(FIRST_YEAR) + "_" + str(LAST_YEAR) + ".csv"
)

# %% Load impact data
df_impact = pd.read_csv(PROCESSED_IMPACT_PATH_CSV, sep=";", index_col=0).set_index(
    "Dis No"
)
#  df_impact = pd.read_csv("data/impact_2000_2018_usa.csv", sep=";").set_index("Dis No")

# %%
df_impact["geometry"] = wkt.loads(df_impact["geometry"])
gdf_impact = gpd.GeoDataFrame(df_impact, crs="epsg:4326")
gdf_impact["Affected Area"] = gdf_impact.to_crs(3857)["geometry"].area / 10**6

# %% Create list of indices of all possible event combinations
event_indices = gdf_impact.index.values
possible_event_pairs = list(itertools.combinations(event_indices, 2))


# %%
def check_intersection(
    possible_event_combination: tuple,
    gdf: gpd.GeoDataFrame,
    event_pairs: list,
):
    event1 = gdf.loc[[possible_event_combination[0]]]
    event2 = gdf.loc[[possible_event_combination[1]]]
    if event1["ISO"].values[0] == event2["ISO"].values[0]:
        if event1.intersects(event2, align=False).iloc[0]:
            intersection = event1.intersection(event2, align=False)
            area_intersection = (intersection.to_crs(3857).area / 10**6).iloc[0]
            if area_intersection > 0:
                possible_event_combination = list(possible_event_combination)
                percent_area1 = np.round(
                    area_intersection / event1["Affected Area"][0], decimals=2
                )
                percent_area2 = np.round(
                    area_intersection / event2["Affected Area"][0], decimals=2
                )
                possible_event_combination.append(np.round(area_intersection))
                possible_event_combination.append(percent_area1)
                possible_event_combination.append(percent_area2)
                event_pairs.append(possible_event_combination)


# %%
event_pairs = list()

threads = []
start = time.time()
for possible_event_combination in possible_event_pairs:
    try:
        thread = threading.Thread(
            target=check_intersection(
                possible_event_combination, gdf_impact, event_pairs
            )
        )
        threads.append(thread)
    except Exception as inst:
        print("Error:" + inst)

# Start the threads
for thread in threads:
    thread.start()

# Ensure all of the threads have finished
for thread in threads:
    thread.join()
end = time.time()
duration = end - start

# %%
df = pd.DataFrame(
    event_pairs,
    columns=["Event1", "Event2", "Area_intersection", "Percent1", "Percent2"],
)
df.to_csv("data/event_pairs.csv", sep=";", index=False)
