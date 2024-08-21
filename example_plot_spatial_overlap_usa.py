
# %%
from shapely import wkt
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import geopandas as gpd
import pandas as pd


#%%
df_impact = pd.read_csv("data/impact_2000_2018.csv", sep=";").set_index("Dis No")

#%%
filter_usa = df_impact["ISO"] == "USA"
df_impact = df_impact[filter_usa]


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
    column="Dis No", alpha=0.4, legend=True, cmap=cmap, ax=axs.reshape(-1)[0], legend_kwds={'fontsize': 15}

)
axs.reshape(-1)[0].set_title("a) 0% mutual overlap between \n 2000-0021-USA and 2000-0232-USA", fontsize = 17
)
axs.reshape(-1)[0].tick_params(labelsize=12)

# Examples 50%
gdf_impact.loc[["2014-0009-USA", "2014-0317-USA"]].reset_index().plot(
    column="Dis No",
    alpha=0.4,
    legend=True,
    cmap=cmap,
    ax=axs.reshape(-1)[1],
    legend_kwds={'fontsize': 15}

)
axs.reshape(-1)[1].set_xlim(-180, -65)
axs.reshape(-1)[1].set_title("b) 40% of 2014-0009-USA and \n 40% of 2014-0317-USA overlap", fontsize = 17
)

axs.reshape(-1)[1].tick_params(labelsize=15)

gdf_impact.loc[["2006-0128-USA", "2007-0173-USA"]].reset_index().plot(
    column="Dis No", alpha=0.4, legend=True, cmap=cmap, ax=axs.reshape(-1)[2],    legend_kwds={'fontsize': 15}

)
axs.reshape(-1)[2].set_title("c) 7% of 2006-0128-USA and \n 100% of 2007-0173-USA overlap", fontsize = 17
)
axs.reshape(-1)[2].tick_params(labelsize=15)

# Example 100%
gdf_impact.loc[["2006-0598-USA", "2006-0744-USA"]].reset_index().plot(
    column="Dis No",
    alpha=0.4,
    legend=True,
    cmap=cmap,
    ax=axs.reshape(-1)[3],
    legend_kwds={'fontsize': 15}
)
axs.reshape(-1)[3].set_title(
    "d) 100% mutual overlap between \n 2006-0598-USA and 2006-0744-USA", fontsize = 17
)
axs.reshape(-1)[3].tick_params(labelsize=15)
axs.reshape(-1)[3].set_xlim(-127, -115)


fig.tight_layout()
# %%
