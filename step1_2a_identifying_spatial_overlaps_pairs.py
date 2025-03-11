# %% Imports
import geopandas as gpd
import pandas as pd
import itertools
import threading
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

# %% Create list of indices of all possible record combinations
record_indices = gdf_impact.index.values
possible_record_pairs = list(itertools.combinations(record_indices, 2))


# %%
def check_intersection(
    possible_record_combination: tuple,
    gdf: gpd.GeoDataFrame,
    record_pairs: list,
):
    record1 = gdf.loc[[possible_record_combination[0]]]
    record2 = gdf.loc[[possible_record_combination[1]]]
    if record1["ISO"].values[0] == record2["ISO"].values[0]:
        if record1.intersects(record2, align=False).iloc[0]:
            intersection = record1.intersection(record2, align=False)
            area_intersection = (intersection.to_crs(3857).area / 10**6).iloc[0]
            if area_intersection > 0:
                possible_record_combination = list(possible_record_combination)
                percent_area1 = np.round(
                    area_intersection / record1["Affected Area"][0], decimals=2
                )
                percent_area2 = np.round(
                    area_intersection / record2["Affected Area"][0], decimals=2
                )
                possible_record_combination.append(np.round(area_intersection))
                possible_record_combination.append(percent_area1)
                possible_record_combination.append(percent_area2)
                record_pairs.append(possible_record_combination)


# %%
record_pairs = list()

threads = []
start = time.time()
for possible_record_combination in possible_record_pairs:
    try:
        thread = threading.Thread(
            target=check_intersection(
                possible_record_combination, gdf_impact, record_pairs
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
    record_pairs,
    columns=["Record1", "Record2", "Area_intersection", "Percent1", "Percent2"],
)
df.to_csv("data/record_pairs.csv", sep=";", index=False)
