# %% Imports
import pandas as pd
import itertools
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from shapely import wkt
import geopandas as gpd
from itertools import chain
import seaborn as sns

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
min_overlap_thress = [0, 0.25, 0.5, 0.75, 1]
max_time_lags = [0, 30, 91, 182, 365]


# %%
df_single_records = pd.DataFrame()


# %%
# min_overlap_thres = 1
# max_time_lag = 0
for min_overlap_thres in min_overlap_thress:
    for max_time_lag in max_time_lags:

        filename = (
            "data/event_pairs_"
            + str(min_overlap_thres)
            + "_"
            + str(max_time_lag)
            + ".csv"
        )
        df = pd.read_csv(filename, sep=";")
        event_pairs = list(
            df.loc[:, ["Event1", "Event2"]].itertuples(index=False, name=None)
        )
        events_with_overlap = list(chain.from_iterable(event_pairs))

        for unique_event in unique_events_sorted:
            if unique_event not in events_with_overlap:
                new_row = pd.DataFrame(
                    [
                        {
                            "Event": unique_event,
                            "Time lag": max_time_lag,
                            "Spatial overlap": min_overlap_thres,
                            "No hazards": len(
                                df_emdat.loc[
                                    unique_event, ["Hazard1", "Hazard2", "Hazard3"]
                                ]
                                .dropna()
                                .values
                            ),
                        }
                    ]
                )
                df_single_records = pd.concat([df_single_records, new_row])


# %%
hazard_filter = df_single_records["No hazards"] == 1
df_single_hazards = df_single_records[hazard_filter]

# %%
df_plot = (
    df_single_hazards[["Time lag", "Spatial overlap", "No hazards"]]
    .groupby(["Time lag", "Spatial overlap"])
    .agg("sum")
    .reset_index()
)

df_plot = df_plot.rename(columns={"No hazards": "Number of single hazards"})
df_plot["Spatial overlap"] = df_plot["Spatial overlap"] * 100
df_plot["Spatial overlap"] = df_plot["Spatial overlap"].astype(int).astype(str) + "%"

# %%
overlap_filter = (df_plot["Spatial overlap"] == "50%") | (
    df_plot["Spatial overlap"] == "100%"
)
sns.set_style("whitegrid", {"grid.linestyle": ":"})
ax = sns.lineplot(
    data=df_plot[overlap_filter],
    x="Time lag",
    y="Number of single hazards",
    hue="Spatial overlap",
    markers=True,
    legend=True,
    palette=sns.color_palette("Purples", n_colors=2),
    linewidth=4,
)

ax.set_xlabel("Time lag [days]", fontsize=25)
ax.set_ylabel("Number of single hazards", fontsize=25)
ax.tick_params(labelsize=20)
# ax.set_title("Single Hazards in EM-DAT 2000 - 2018", fontsize = 25)
plt.setp(ax.get_legend().get_texts(), fontsize="20")  # for legend text
plt.setp(ax.get_legend().get_title(), fontsize="25")  # for legend title

plt.tight_layout()
# %%
