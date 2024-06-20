###
# This file analysis the preprocessed EMDAT data

# %%
import pandas as pd
import matplotlib.pyplot as plt
import squarify
from shapely import wkt
import geopandas as gpd

# %% Constants
# PROCESSED_EMDAT_PATH = "data/impact_2000_2018.csv"
PROCESSED_EMDAT_PATH = "data/emdat_2000_2018.csv"


# %%
df = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")


# %%
# %% Constants
PATH = "data/df_compound_consecutive_events.csv"

# %%
df_all = pd.read_csv(PATH, sep=";")

# %%
filter = df_all["Number Hazards"] > 1

type_hazards = df_all[filter]["Type Hazards"].value_counts()

labels = type_hazards.index.values
sizes = type_hazards.values
squarify.plot(sizes, label=labels)
plt.axis("off")
plt.show()

# %%
df_all[filter]["Type Event"].value_counts()


# %% Show regions with more of 3 types having led to disaster
PROCESSED_IMPACT_PATH_CSV = "data/impact_2000_2018.csv"

df_impact = pd.read_csv(PROCESSED_IMPACT_PATH_CSV, sep=";", index_col=0).set_index(
    "Dis No"
)

# %%
max_types_filter = df_all["Number Types"] >= 3
dis_nos = df_all[max_types_filter]["Dis No 1"]

# %%
df_impact["geometry"] = wkt.loads(df_impact["geometry"])
gdf_impact = gpd.GeoDataFrame(df_impact, crs="epsg:4326")

# %%
gdf_world = gpd.read_file("data/world-administrative-boundaries.geojson")


# %%
fig, ax = plt.subplots(
    1,
    1,
    figsize=(24, 24),
    # width_ratios=[3, 3, 3],
)
gdf_impact.loc[dis_nos].reset_index().plot(
    ax=ax, column="Dis No", categorical=True, cmap="Spectral", legend=False
)
gdf_world.boundary.plot(ax=ax, color="grey")

# %%
