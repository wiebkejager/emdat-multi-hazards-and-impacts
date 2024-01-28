# %% Imports
import geopandas as gpd
import pandas as pd
import itertools
import threading
import datetime
import json
from shapely import wkt
import time

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


# %% Create list of indices of all possible event combinations
event_indices = gdf_impact.index.values
possible_event_pairs = list(itertools.combinations(event_indices, 2))


# %%
def check_intersection(
    possible_event_combination: tuple,
    gdf: gpd.GeoDataFrame,
    event_pairs: list,
    split_events: list,
):
    event1 = gdf.loc[[possible_event_combination[0]]]
    event2 = gdf.loc[[possible_event_combination[1]]]
    if event1.intersects(event2, align=False).values[0]:
        if event1.touches(event2, align=False).values[0] > 0:
            split_events.append(possible_event_combination)
        else:
            event_pairs.append(possible_event_combination)

    # if event1.overlaps(event2, align=False).values[0]:
    #     event_pairs.append(possible_event_combination)
    #     return
    # if event1.covers(event2, align=False).values[0]:
    #     event_pairs.append(possible_event_combination)
    #     return
    # if event1.covered_by(event2, align=False).values[0]:
    #     event_pairs.append(possible_event_combination)
    #     return
    # if event1.touches(event2, align=False).values[0]:
    #     split_events.append(possible_event_combination)
    #     return


# %%
event_pairs = list()
split_events = list()

threads = []
start = time.time()
for possible_event_combination in possible_event_pairs:
    try:
        thread = threading.Thread(
            target=check_intersection(
                possible_event_combination, gdf_impact, event_pairs, split_events
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
df = pd.DataFrame(event_pairs, columns=["Event1", "Event2"])
df2 = pd.DataFrame(split_events, columns=["Event1", "Event2"])

df.to_csv("data/event_pairs.csv", sep=";", index=False)
df2.to_csv("data/split_event_pairs.csv", sep=";", index=False)


# %%
# df = pd.read_csv("event_pairs.csv", sep=";")
event_pairs = list(df.itertuples(index=False, name=None))
unique_events = list(set(itertools.chain.from_iterable(event_pairs)))

# %%
dict_spatially_overlapping_events = {}
for event in unique_events:
    filter_event = [event in ec for ec in event_pairs]
    overlapping_events = set(
        itertools.chain.from_iterable((itertools.compress(event_pairs, filter_event)))
    )
    overlapping_events.remove(event)
    dict_spatially_overlapping_events[event] = json.dumps(list(overlapping_events))

# %%
df_spatially_overlapping_events = pd.DataFrame.from_dict(
    dict_spatially_overlapping_events, orient="index", columns=["Overlapping events"]
)
df_spatially_overlapping_events.to_csv("df_spatially_overlapping_events.csv", sep=";")
