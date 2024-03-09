# %% Imports
import geopandas as gpd
import pandas as pd
import itertools
import threading
import json
from shapely import wkt
import time
import numpy as np


# %%
df = pd.read_csv("data/event_pairs.csv", sep=";")
event_pairs = list(df.itertuples(index=False, name=None))
unique_events = list(set(itertools.chain.from_iterable(event_pairs)))
threshold = 0.5

# %%
dict_spatially_overlapping_events = (
    {}
)  # for each event list all spatially overlapping events
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
df_spatially_overlapping_events.to_csv(
    "data/df_spatially_overlapping_events_10percent.csv", sep=";"
)
