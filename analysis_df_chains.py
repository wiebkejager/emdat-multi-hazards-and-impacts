# %% Imports
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import numpy as np
from shapely import wkt
import geopandas as gpd

# %%
PROCESSED_EMDAT_PATH = "data/emdat_2000_2018.csv"

# %% EM-DAT
df_emdat = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")
df_emdat.loc[:, "Hazards"] = df_emdat[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: list(x.dropna()), axis=1
)
df_emdat.loc[:, "No hazards"] = df_emdat.loc[:, "Hazards"].apply(len)


# %% s-t overlapping events
min_overlap_thres = 1
max_time_lag = 30
df_chain_1 = pd.read_csv(
    "data/df_chain_" + str(min_overlap_thres) + "_" + str(max_time_lag) + ".csv",
    sep=";",
    index_col=0,
)
df_chain_1["Events"] = df_chain_1["Events"].apply(json.loads)
df_chain_1["Hazards"] = df_chain_1["Hazards"].apply(json.loads)

min_overlap_thres = 0.5
max_time_lag = 91
df_chain_2 = pd.read_csv(
    "data/df_chain_" + str(min_overlap_thres) + "_" + str(max_time_lag) + ".csv",
    sep=";",
    index_col=0,
)
df_chain_2["Events"] = df_chain_2["Events"].apply(json.loads)
df_chain_2["Hazards"] = df_chain_2["Hazards"].apply(json.loads)

# %%
var = "No events"
print(df_chain_1[var].max())
print(df_chain_1[var].median())
print(df_chain_1[var].mean())
print("")
print(df_chain_2[var].max())
print(df_chain_2[var].median())
print(df_chain_2[var].mean())


# %%

foo = df_chain_1.loc["2008-0374-CHN", "Events"]
foo2 = df_emdat.loc[foo]


# %%
# df_impact = pd.read_csv("data/impact_2000_2018.csv", sep=";")
# df_impact_chn = df_impact.loc[df_impact["ISO"] == "CHN"]
# df_impact_chn.to_csv("data/impact_2000_2018_chn.csv", sep=";")


# %%
df_impact = pd.read_csv("data/impact_2000_2018_chn.csv", sep=";").set_index("Dis No")
# %%
df_impact["geometry"] = wkt.loads(df_impact["geometry"])
gdf_impact = gpd.GeoDataFrame(df_impact, crs="epsg:4326")

# %%
gdf_impact.loc[foo].reset_index().plot(column="Dis No", alpha=0.2, legend=True)

# %%
gdf_impact.loc[["2008-0374-CHN"]].reset_index().plot(
    column="Dis No", alpha=0.2, legend=True
)

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
