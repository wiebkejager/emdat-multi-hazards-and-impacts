# %% Imports
import geopandas as gpd
import pandas as pd
import itertools
import threading
import datetime
import json

# %% Define constants
START_YEAR = 2000
END_YEAR = 2015
PROCESSED_IMPACT_PATH = "impact_2000_2015.gpkg"
PROCESSED_IMPACT_PATH_CSV = "impact_2000_2015.csv"

# %% Load impact data
gdf_impact = gpd.read_file(PROCESSED_IMPACT_PATH)
gdf_impact.set_index("Dis No", inplace=True)

# # %%
# gdf_impact.drop("geometry", axis=1).to_csv(
#     PROCESSED_IMPACT_PATH_CSV, sep=";", index=True
# )
# %% Create list of indices of all possible event combinations
# event_indices = gdf_impact.index.values
# possible_event_combinations = list(itertools.combinations(event_indices, 2))[1:10000]


def check_intersection(
    possible_event_combination: tuple,
    gdf: gpd.GeoDataFrame,
    event_combinations: list,
):
    event1 = gdf.loc[[possible_event_combination[0]]]
    event2 = gdf.loc[[possible_event_combination[1]]]
    spatial_overlap = event1.intersection(
        event2, align=False
    ).is_ring  # intersection without only touches
    if spatial_overlap.values[0]:
        event_combinations.append(possible_event_combination)


# # %%
# event_combinations = list()
# threads = []
# for possible_event_combination in possible_event_combinations:
#     thread = threading.Thread(
#         target=check_intersection(
#             possible_event_combination, gdf_impact, event_combinations
#         )
#     )
#     threads.append(thread)

# # Start the threads
# for thread in threads:
#     thread.start()

# # Ensure all of the threads have finished
# for thread in threads:
#     thread.join()

# print(event_combinations)


# # %%
# df = pd.DataFrame(event_combinations, columns=["Event1", "Event2"])
# # df.to_csv("event_pairs.csv", sep=";", index=False)

# %%
df = pd.read_csv("event_pairs.csv", sep=";")
event_combinations = list(df.itertuples(index=False, name=None))
unique_events = list(set(itertools.chain.from_iterable(event_combinations)))

# %%
dict_spatially_overlapping_events = {}
for event in unique_events:
    filter_event = [event in ec for ec in event_combinations]
    overlapping_events = set(
        itertools.chain.from_iterable(
            (itertools.compress(event_combinations, filter_event))
        )
    )
    overlapping_events.remove(event)
    dict_spatially_overlapping_events[event] = json.dumps(list(overlapping_events))

# %%
df_spatially_overlapping_events = pd.DataFrame.from_dict(
    dict_spatially_overlapping_events, orient="index", columns=["Overlapping events"]
)
df_spatially_overlapping_events.to_csv("df_spatially_overlapping_events.csv", sep=";")


# %% temporal overlap
temporal_buffer = datetime.timedelta(days=30)
df_res = df_spatially_overlapping_events.copy(deep=True)

# %%
for ix, row in df_res.iterrows():
    if ix == "2010-0454-GMB":
        foo = 2
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
    df_res.loc[ix]["Overlapping events"] = json.dumps(overlapping_events)

# %%
df_res.to_csv("df_res.csv", sep=";", index=True)
# %%
