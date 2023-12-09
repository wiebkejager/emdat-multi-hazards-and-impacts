# %% Imports
import geopandas as gpd
import itertools
import threading

# %% Define constants
START_YEAR = 2000
END_YEAR = 2015
PROCESSED_IMPACT_PATH = "impact_2000_2015.gpkg"

# %% Load impact data
gdf_impact_geometries = gpd.read_file(PROCESSED_IMPACT_PATH)
gdf_impact = gdf_impact_geometries.copy()
gdf_impact.set_index("Dis No", inplace=True)

# %% Create list of indices of all possible event combinations
event_indices = gdf_impact.index.values
possible_event_combinations = list(itertools.combinations(event_indices, 2))[1:10000]


def check_intersection(
    possible_event_combination: tuple,
    gdf: gpd.GeoDataFrame,
    event_combinations: list,
):
    event1 = gdf.loc[[possible_event_combination[0]]]
    event2 = gdf.loc[[possible_event_combination[1]]]
    spatial_overlap = event1.intersects(event2, align=False)
    if spatial_overlap.values[0]:
        event_combinations.append(possible_event_combination)


# %%
event_combinations = list()
threads = []
for possible_event_combination in possible_event_combinations:
    thread = threading.Thread(
        target=check_intersection(
            possible_event_combination, gdf_impact, event_combinations
        )
    )
    threads.append(thread)

# Start the threads
for thread in threads:
    thread.start()

# Ensure all of the threads have finished
for thread in threads:
    thread.join()

print(event_combinations)


# %%
event_combinations.to_csv("event_pairs.csv", sep=";")
