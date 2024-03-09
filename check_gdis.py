# %%
import pandas as pd

# %% Constants
PROCESSED_EMDAT_PATH = "data/emdat_2000_2018.csv"
GDIS_CSV_PATH = "data/pend-gdis-1960-2018-disasterlocations-csv/pend-gdis-1960-2018-disasterlocations.csv"

# %%
df_emdat = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")
df_gdis = pd.read_csv(GDIS_CSV_PATH)

# %%
df_emdat2 = df_emdat[df_emdat["geom"].isna()]

# %%
df_emdat2["disno"] = df_emdat2.index.str[0:9]
df_emdat2 = df_emdat2["disno"]
indicator = df_emdat2["disno"].isin(df_gdis["disasterno"])

sum(indicator)

# %%
df_emdat3 = df_emdat2[indicator]
# %%
indicator2 = df_gdis["disasterno"].isin(df_emdat2[indicator]["disno"])

# %%
foo = df_gdis[indicator2]

# %%
