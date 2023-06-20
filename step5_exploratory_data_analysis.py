# %%
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm

# %% Constants
PROCESSED_IMPACT_PATH2_CSV = (
    "C:/Users/wja209/DATA/PROCESSED/impact_hazard_exposure_vulnerability_1990_2015.csv"
)
PROCESSED_EMDAT_PATH = "C:/Users/wja209/DATA/PROCESSED/emdat_1990_2015.csv"


# %% Read data set
df = pd.read_csv(PROCESSED_IMPACT_PATH2_CSV)
df_emdat = pd.read_csv(PROCESSED_EMDAT_PATH)

# %% Add column indicating single-hazard or multi-hazard
df["eventtype"] = df[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: "multi-hazard" if sum(x.isna()) <= 1 else "single-hazard", axis=1
)
# Add column indicating single-hazard or multi-hazard
df["eventtype_detailed"] = df[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: ",".join(list(x.dropna())), axis=1
)

# %% Add column indicating single-hazard or multi-hazard
df_emdat["eventtype"] = df_emdat[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: "multi-hazard" if sum(x.isna()) <= 1 else "single-hazard", axis=1
)
# Add column indicating single-hazard or multi-hazard
df_emdat["eventtype_detailed"] = df_emdat[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: ",".join(list(x.dropna())), axis=1
)

# %%
fig, (ax1, ax2) = plt.subplots(1, 2)
df_emdat["eventtype"].value_counts().plot(kind="bar", ax=ax1, ylim=(0, 4000))
df["eventtype"].value_counts().plot(kind="bar", ax=ax2, ylim=(0, 4000))

# %%
fig, (ax1, ax2) = plt.subplots(1, 2)
df_emdat["eventtype_detailed"].value_counts().plot(kind="bar", ax=ax1, ylim=(0, 1800))
df["eventtype_detailed"].value_counts().plot(kind="bar", ax=ax2, ylim=(0, 1800))

# %% Standard pairplot for EDA
sns.pairplot(df, diag_kind="kde", hue="eventtype")


# %%
df_ranks = df.copy()
vars = [
    "Total Affected",
    "GDP per Capita PPP",
    "Population Count",
    "Intensity_eq",
    "Intensity_fl",
    "Intensity_dr",
    "Intensity_ts",
    "Intensity_vo",
    "Intensity_ls",
    "Intensity_hw",
    "Intensity_ew",
    "Intensity_cw",
    "Intensity_wf",
]

df_ranks.loc[:, vars] = df.loc[:, vars].rank() / df.loc[:, vars].rank().max()

# %%
sns.pairplot(df_ranks, diag_kind="hist", hue="eventtype")


# %%
df_normalized = df_ranks.copy()
df_normalized.loc[:, vars] = df_normalized.loc[:, vars].applymap(lambda x: norm.ppf(x))

# %%
sns.pairplot(df_normalized, diag_kind="kde")

# %%
vars2 = ["Total Affected", "GDP per Capita PPP", "Population Count", "eventtype"]
sns.pairplot(df_normalized[vars2], hue="eventtype", plot_kws={"alpha": 0.1})


# %%
