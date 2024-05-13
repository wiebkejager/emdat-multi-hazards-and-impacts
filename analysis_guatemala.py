# %%
import pandas as pd
from shapely import wkt
import geopandas as gpd
import matplotlib.pylab as plt

# %%
df_impact_gtm = pd.read_csv("data/impact_2000_2018_gtm.csv", sep=";").set_index(
    "Dis No"
)

df_impact_gtm["Start Date"] = df_impact_gtm["Start Date"].str[0:10]

# %%
df_impact_gtm["Hazards"] = df_impact_gtm[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: ", ".join(list(x.dropna())), axis=1
)

# %%
df_impact_gtm["Title"] = df_impact_gtm["Start Date"] + ": " + df_impact_gtm["Hazards"]
# %%

df_impact_gtm["geometry"] = wkt.loads(df_impact_gtm["geometry"])
gdf_impact = gpd.GeoDataFrame(df_impact_gtm, crs="epsg:4326")


# %%
guatemala = gpd.read_file(
    "C:/Users/wja209/DATA/RAW/gtm_adm_ocha_conred_2019_shp/gtm_admbnda_adm1_ocha_conred_20190207.shp"
)

# %%
dis_no_1 = "2010-0220-GTM"
dis_no_2 = "2010-0211-GTM"
dis_no_3 = "2010-0442-GTM"
dis_no_4 = "2010-0503-GTM"

# %%
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
# fig, (ax1, ax2) = plt.subplots(1, 2)
guatemala.boundary.plot(ax=ax1)
gdf_impact.loc[[dis_no_1]].reset_index().plot(
    ax=ax1, column="Dis No", alpha=0.5, legend=False
)
ax1.set_title(gdf_impact.loc[dis_no_1, "Title"])
# ax1.set_title("Pacaya volcano")


guatemala.boundary.plot(ax=ax2)
gdf_impact.loc[[dis_no_2]].reset_index().plot(
    ax=ax2, column="Dis No", alpha=0.5, legend=False
)
ax2.set_title(gdf_impact.loc[dis_no_2, "Title"])
# ax2.set_title("Hurricane Agatha")


guatemala.boundary.plot(ax=ax3)
gdf_impact.loc[[dis_no_3]].reset_index().plot(
    ax=ax3, column="Dis No", alpha=0.5, legend=False
)
ax3.set_title(gdf_impact.loc[dis_no_3, "Title"])


guatemala.boundary.plot(ax=ax4)
gdf_impact.loc[["2010-0503-GTM"]].reset_index().plot(
    ax=ax4, column="Dis No", alpha=0.5, legend=False
)
ax4.set_title(gdf_impact.loc[dis_no_4, "Title"])

fig.tight_layout()
# %%

# %%
