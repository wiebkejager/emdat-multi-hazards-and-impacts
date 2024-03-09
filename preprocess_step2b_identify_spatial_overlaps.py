# %% Imports
import pandas as pd
import itertools
import json


# %%
df = pd.read_csv("data/event_pairs.csv", sep=";")


# %%
min_overlap_thres = 0.4
thres_filter = (df["Percent1"] > min_overlap_thres) & (
    df["Percent2"] > min_overlap_thres
)

event_pairs = list(df.loc[:, ["Event1", "Event2"]].itertuples(index=False, name=None))
unique_events = list(set(itertools.chain.from_iterable(event_pairs)))
event_pairs = list(
    df.loc[thres_filter, ["Event1", "Event2"]].itertuples(index=False, name=None)
)

# %%
dict_spatially_overlapping_events = (
    {}
)  # for each event list all spatially overlapping events
for event in unique_events:
    filter_event = [event in ec for ec in event_pairs]
    overlapping_events = set(
        itertools.chain.from_iterable((itertools.compress(event_pairs, filter_event)))
    )
    if overlapping_events:
        overlapping_events.remove(event)
    dict_spatially_overlapping_events[event] = json.dumps(list(overlapping_events))


# %%
df_spatially_overlapping_events = pd.DataFrame.from_dict(
    dict_spatially_overlapping_events, orient="index", columns=["Overlapping events"]
)

# %%
df_spatially_overlapping_events.to_csv(
    "data/df_spatially_overlapping_events_.csv", sep=";"
)

# %%
