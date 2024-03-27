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
unique_events_sorted = df_emdat.sort_values(by="Start Date").index.values

# %%
min_overlap_thress = [0, 0.5, 1]
max_time_lags = [0, 30, 91, 182, 365, 100000]


# %%
def get_influencing_events(event, event_pairs, df_emdat) -> list:
    filter_event = [event in ec for ec in event_pairs]
    overlapping_events = set(
        itertools.chain.from_iterable((itertools.compress(event_pairs, filter_event)))
    )
    if overlapping_events:
        overlapping_events.remove(event)

        # remove the ones later in time than event
        startdate_event = df_emdat.loc[event, "Start Date"]
    return [
        i
        for i in overlapping_events
        if df_emdat.loc[i, "Start Date"] <= startdate_event
    ]


# %%
min_overlap_thres = 1
max_time_lag = 0
# for min_overlap_thres in min_overlap_thress:
#     for max_time_lag in max_time_lags:

filename = (
    "data/event_pairs_" + str(min_overlap_thres) + "_" + str(max_time_lag) + ".csv"
)
df = pd.read_csv(filename, sep=";")

dict_all_events = dict()

# for each event list all overlapping events
event_pairs = list(df.loc[:, ["Event1", "Event2"]].itertuples(index=False, name=None))

for unique_event in unique_events_sorted:

    influencing_events = get_influencing_events(unique_event, event_pairs, df_emdat)

    loop_condition = True
    while loop_condition:
        influencing_events_temp = []
        influencing_events_updated = []
        for event_new in influencing_events:
            influencing_events_temp = influencing_events_temp + get_influencing_events(
                event_new, event_pairs, df_emdat
            )

        if unique_event in influencing_events_temp:
            influencing_events_temp.remove(unique_event)

        influencing_events_updated = list(
            set(influencing_events + influencing_events_temp)
        )

        if sorted(influencing_events) == sorted(influencing_events_updated):
            loop_condition = False
        else:
            influencing_events = influencing_events_updated

    all_events = influencing_events + [unique_event]
    all_events_sorted = [
        e[0]
        for e in sorted(
            [tuple([i, df_emdat.loc[i, "Start Date"]]) for i in all_events],
            key=lambda a: a[1],
        )
    ]
    dict_all_events[unique_event] = json.dumps(all_events_sorted)


df_chain = pd.DataFrame.from_dict(dict_all_events, orient="index", columns=["Events"])

# %%
df_chain["Events"] = df_chain["Events"].apply(json.loads)


# %%
df_chain["No events"] = df_chain["Events"].apply(len)

for ix, row in df_chain.iterrows():
    events = row.loc["Events"]
    hazards = []
    damages = []
    affected = []
    deaths = []
    for event in events:
        hazards = hazards + list(
            df_emdat.loc[event, ["Hazard1", "Hazard2", "Hazard3"]].dropna().values
        )
        # damages = damages + [df_emdat.loc[event, "Total Damages, Adjusted ('000 US$')"]]
        # affected = affected + [df_emdat.loc[event, "Total Affected"]]
        # deaths = deaths + [df_emdat.loc[event, "Total Deaths"]]

    df_chain.loc[ix, "Hazards"] = json.dumps(hazards)
    # df.loc[ix, "Damages"] = np.nansum(damages)
    # df.loc[ix, "Affected"] = np.nansum(affected)
    # df.loc[ix, "Deaths"] = np.nansum(deaths)


df_chain["Hazards"] = df_chain["Hazards"].apply(json.loads)
df_chain["No hazards"] = df_chain["Hazards"].apply(len)

# %%
df_chain["Events"] = df_chain["Events"].apply(json.dumps)
df_chain["Hazards"] = df_chain["Hazards"].apply(json.dumps)

df_chain.to_csv(
    "data/df_chain_" + str(min_overlap_thres) + "_" + str(max_time_lag) + ".csv",
    sep=";",
)


# %%
# # %%
# df_impact = pd.read_csv("data/impact_2000_2018_usa.csv", sep=";").set_index("Dis No")

# # %%
# # df_impact = pd.read_csv(PROCESSED_IMPACT_PATH_CSV, sep=";", index_col=0).set_index(
# #     "Dis No"
# # )
# df_impact["geometry"] = wkt.loads(df_impact["geometry"])
# gdf_impact = gpd.GeoDataFrame(df_impact, crs="epsg:4326")
# # gdf_impact["Affected Area"] = gdf_impact.to_crs(3857)["geometry"].area / 10**6


# cmap = ListedColormap(["yellow", "lightseagreen"])

# # %%
# # Example 0%
# fig, axs = plt.subplots(
#     2,
#     2,
#     figsize=(11, 11),
#     # width_ratios=[3, 3, 3],
# )

# gdf_impact.loc[["2000-0021-USA", "2000-0232-USA"]].reset_index().plot(
#     column="Dis No", alpha=0.4, legend=True, cmap=cmap, ax=axs.reshape(-1)[0]
# )
# axs.reshape(-1)[0].set_title("a) 0% mutual overlap between 2000-0021-USA 2000-0232-USA")

# # Examples 50%
# gdf_impact.loc[["2014-0009-USA", "2014-0317-USA"]].reset_index().plot(
#     column="Dis No",
#     alpha=0.4,
#     legend=True,
#     cmap=cmap,
#     ax=axs.reshape(-1)[1],
# )
# axs.reshape(-1)[1].set_xlim(-180, -65)
# axs.reshape(-1)[1].set_title("b) 40% of 2014-0009-USA and 40% of 2014-0317-USA overlap")

# gdf_impact.loc[["2006-0128-USA", "2007-0173-USA"]].reset_index().plot(
#     column="Dis No", alpha=0.4, legend=True, cmap=cmap, ax=axs.reshape(-1)[2]
# )
# axs.reshape(-1)[2].set_title("c) 7% of 2013-0472-USA and 100% of 2018-0457-USA overlap")

# # Example 100%
# gdf_impact.loc[["2006-0598-USA", "2006-0744-USA"]].reset_index().plot(
#     column="Dis No",
#     alpha=0.4,
#     legend=True,
#     cmap=cmap,
#     ax=axs.reshape(-1)[3],
# )
# axs.reshape(-1)[3].set_title(
#     "d) 100% mutual overlap between 2006-0598-USA and 2006-0744-USA"
# )
# fig.tight_layout()

# # %%

# %%
