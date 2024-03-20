# %% Imports
import pandas as pd
import itertools
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from shapely import wkt
import geopandas as gpd

FIRST_YEAR = 2000
LAST_YEAR = 2018
PROCESSED_IMPACT_PATH_CSV = (
    "data/impact_" + str(FIRST_YEAR) + "_" + str(LAST_YEAR) + ".csv"
)
PROCESSED_EMDAT_PATH = "data/emdat_2000_2018.csv"

# %%
df_emdat = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")

# %%
df = pd.read_csv("data/event_pairs.csv", sep=";")
df["Percent"] = df.apply(lambda x: np.max([x.Percent1, x.Percent2]), axis=1)


# %%
plt.hist(
    df["Percent"] * 100,
    bins=100,
)
plt.xlabel("Intersection %")
plt.ylabel("Number of event pairs")


# %%
min_overlap_thres = 0.5
thres_filter = (df["Percent1"] > min_overlap_thres) | (
    df["Percent2"] > min_overlap_thres
)

event_pairs = list(df.loc[:, ["Event1", "Event2"]].itertuples(index=False, name=None))
unique_events = df_emdat.index.values
event_pairs = list(
    df.loc[thres_filter, ["Event1", "Event2"]].itertuples(index=False, name=None)
)


# %%
df2 = df.loc[thres_filter]
df2.to_csv("data/event_pairs_50percent.csv", sep=";", index=False)

# %%
# dict_spatially_overlapping_events = (
#     {}
# )  # for each event list all spatially overlapping events
# for event in unique_events:
#     filter_event = [event in ec for ec in event_pairs]
#     overlapping_events = set(
#         itertools.chain.from_iterable((itertools.compress(event_pairs, filter_event)))
#     )
#     if overlapping_events:
#         overlapping_events.remove(event)
#     dict_spatially_overlapping_events[event] = json.dumps(list(overlapping_events))


# # %%
# df_spatially_overlapping_events = pd.DataFrame.from_dict(
#     dict_spatially_overlapping_events, orient="index", columns=["Overlapping events"]
# )

# # %%
# df_spatially_overlapping_events.to_csv(
#     "data/df_spatially_overlapping_events.csv", sep=";"
# )

# %%
df_impact = pd.read_csv("data/impact_2000_2018_usa.csv", sep=";").set_index("Dis No")

# %%
# df_impact = pd.read_csv(PROCESSED_IMPACT_PATH_CSV, sep=";", index_col=0).set_index(
#     "Dis No"
# )
df_impact["geometry"] = wkt.loads(df_impact["geometry"])
gdf_impact = gpd.GeoDataFrame(df_impact, crs="epsg:4326")
# gdf_impact["Affected Area"] = gdf_impact.to_crs(3857)["geometry"].area / 10**6


cmap = ListedColormap(["yellow", "lightseagreen"])

# %%
# Example 0%
fig, axs = plt.subplots(
    2,
    2,
    figsize=(11, 11),
    # width_ratios=[3, 3, 3],
)

gdf_impact.loc[["2000-0021-USA", "2000-0232-USA"]].reset_index().plot(
    column="Dis No", alpha=0.4, legend=True, cmap=cmap, ax=axs.reshape(-1)[0]
)
axs.reshape(-1)[0].set_title("a) 0% mutual overlap between 2000-0021-USA 2000-0232-USA")

# Examples 50%
gdf_impact.loc[["2014-0009-USA", "2014-0317-USA"]].reset_index().plot(
    column="Dis No",
    alpha=0.4,
    legend=True,
    cmap=cmap,
    ax=axs.reshape(-1)[1],
)
axs.reshape(-1)[1].set_xlim(-180, -65)
axs.reshape(-1)[1].set_title("b) 40% of 2014-0009-USA and 40% of 2014-0317-USA overlap")

gdf_impact.loc[["2006-0128-USA", "2007-0173-USA"]].reset_index().plot(
    column="Dis No", alpha=0.4, legend=True, cmap=cmap, ax=axs.reshape(-1)[2]
)
axs.reshape(-1)[2].set_title("c) 7% of 2013-0472-USA and 100% of 2018-0457-USA overlap")

# Example 100%
gdf_impact.loc[["2006-0598-USA", "2006-0744-USA"]].reset_index().plot(
    column="Dis No",
    alpha=0.4,
    legend=True,
    cmap=cmap,
    ax=axs.reshape(-1)[3],
)
axs.reshape(-1)[3].set_title(
    "d) 100% mutual overlap between 2006-0598-USA and 2006-0744-USA"
)
fig.tight_layout()

# %%
