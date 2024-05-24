# %% Imports
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import numpy as np
from shapely import wkt
import geopandas as gpd

# %%
# PROCESSED_EMDAT_PATH = "data/emdat_2000_2018.csv"

# # %% EM-DAT
# df_emdat = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")
# df_emdat.loc[:, "Hazards"] = df_emdat[["Hazard1", "Hazard2", "Hazard3"]].apply(
#     lambda x: list(x.dropna()), axis=1
# )
# df_emdat.loc[:, "No hazards"] = df_emdat.loc[:, "Hazards"].apply(len)


# %% s-t overlapping events
min_overlap_thress = [0.5]  # [0.25, 0.5, 0.75, 1]
max_time_lags = [91]  # [0, 30, 91, 182, 365]

df_chains = pd.DataFrame()
df_plot = pd.DataFrame()

for min_overlap_thres in min_overlap_thress:
    for max_time_lag in max_time_lags:
        df_chain_temp = pd.read_csv(
            "data/df_chain_"
            + str(min_overlap_thres)
            + "_"
            + str(max_time_lag)
            + ".csv",
            sep=";",
            index_col=0,
        )
        df_chain_temp["Timelag"] = max_time_lag
        df_chain_temp["Overlap"] = min_overlap_thres
        df_chains = pd.concat([df_chains, df_chain_temp], ignore_index=True)


# %%
# Identify independent events
ll_events = df_chains["Events"].to_list()
ll_unique_events = list()

for l_events in ll_events:
    ll_events2 = ll_events
    ll_events2.remove(l_events)
    if not any(
        set(json.loads(l_events)).issubset(set(json.loads(l_events2)))
        for l_events2 in ll_events2
    ):
        ll_unique_events.append(l_events)

df_ind_events = df_chains.loc[df_chains["Events"].isin(ll_unique_events)]


# %% Unique hazards per event
df_ind_events["Unique hazards"] = df_ind_events["Hazards"].apply(
    lambda x: set(json.loads(x))
)
df_ind_events["No unique hazards"] = df_ind_events["Unique hazards"].apply(len)

# %%
# one_event_filter = df_chains["No events"] == 1
# df_plot_events = (
#     df_chains.loc[one_event_filter, ["No events", "Timelag", "Overlap"]]
#     .groupby(by=["Timelag", "Overlap"])
#     .agg("sum")
# )
# df_plot_events

# %%
# df_impact = pd.read_csv("data/impact_2000_2018.csv", sep=";")
# df_impact_chn = df_impact.loc[df_impact["ISO"] == "CHN"]
# df_impact_chn.to_csv("data/impact_2000_2018_chn.csv", sep=";")


# %%
# df_impact = pd.read_csv("data/impact_2000_2018_chn.csv", sep=";").set_index("Dis No")
# # %%
# df_impact["geometry"] = wkt.loads(df_impact["geometry"])
# gdf_impact = gpd.GeoDataFrame(df_impact, crs="epsg:4326")

# # %%
# gdf_impact.loc[foo].reset_index().plot(column="Dis No", alpha=0.2, legend=True)

# # %%
# gdf_impact.loc[["2008-0374-CHN"]].reset_index().plot(
#     column="Dis No", alpha=0.2, legend=True
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
