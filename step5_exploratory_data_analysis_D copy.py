# %%
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

# %% Define constants
PROCESSED_IMPACT_EXP_AND_VUL_PATH_CSV = (
    "C:/Users/wja209/DATA/PROCESSED/impact_exposure_vulnerability_2000_2015_nogeom.csv"
)
EM_DAT_PATH = "C:/Users/wja209/DATA/RAW/EM-DAT/emdat_public_2023_03_31_query_uid-n7b9hv-natural-sisasters.csv"


# %% Load impact data
df = pd.read_csv(PROCESSED_IMPACT_EXP_AND_VUL_PATH_CSV).set_index("Dis No")
df_emdat = pd.read_csv(EM_DAT_PATH, sep=";").set_index("Dis No")

# %% Temporary fix:
df.loc[:, "Continent"] = df_emdat.loc[:, "Continent"]

# %% Add column indicating single-hazard or multi-hazard
df.loc[:, "eventtype"] = df[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: "multi-hazard" if sum(x.isna()) <= 1 else "single-hazard", axis=1
)
# Add column indicating single-hazard or multi-hazard
df.loc[:, "eventtype_detailed"] = df[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: ",".join(sorted(list(x.dropna()))), axis=1
)

df.loc[:, "Duration"] = (
    (
        pd.to_datetime(df.loc[:, "End Date"]) - pd.to_datetime(df.loc[:, "Start Date"])
    ).dt.total_seconds()
    / 60
    / 60
    / 24
)

df.loc[:, "Population Density"] = (
    df.loc[:, "Population Count"] / df.loc[:, "Affected Area"]
)

# %%
df.loc[:, "eventtype_detailed"].value_counts()


# %%
# eventtype_filter = df["eventtype_detailed"].isin(["fl", "ls", "fl,ls"])
# df = df[eventtype_filter]


# %%
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(5, 5))
sns.countplot(x="eventtype", data=df, ax=ax1).set(xlabel=None)
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
ax1.set_ylabel("Count of events")
sns.boxplot(x="eventtype", y="Total Affected", data=df, showfliers=False, ax=ax2).set(
    xlabel=None
)
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)
sns.boxplot(x="eventtype", y="Total Deaths", data=df, showfliers=False, ax=ax3).set(
    xlabel=None
)
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=90)
fig.tight_layout()

# %%
countries = [
    "China",
    "United States of America (the)",
    "India",
    "Philippines (the)",
    "Indonesia",
    "Japan",
    "Afghanistan",
    "Mexico",
    "Pakistan",
    "Brazil",
]
fig, axes = plt.subplots(1, 10, figsize=(14, 7))
for i, ax in zip(range(10), axes.flat):
    sns.boxplot(
        x="eventtype",
        y="Total Affected",
        data=df[df.loc[:, "Country"] == countries[i]],
        showfliers=False,
        ax=ax,
        order=["single-hazard", "multi-hazard"],
    ).set(xlabel=None, title=countries[i])
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    fig.tight_layout()

# %%
vars = [
    "Total Affected",
    "Population Density",
    "Population Count",
    "GDP per Capita PPP",
    "Affected Area",
    "Duration",
]

eventtypes = ["multi-hazard", "single-hazard"]

correlations = pd.DataFrame(
    index=eventtypes,
    columns=vars[1 : len(vars)],
)

for eventtype in eventtypes:
    event_filter = df["eventtype"] == eventtype
    correlations.loc[eventtype, "Sample size"] = sum(event_filter)
    for var in vars[1 : len(vars)]:
        try:
            corr = stats.spearmanr(
                df.loc[event_filter, var],
                df.loc[event_filter, vars[0]],
                nan_policy="omit",
            )
        except:
            corr = list([np.nan, np.nan])

        if corr[1] <= 0.05:
            correlations.loc[eventtype, var] = np.round(corr[0], 2)

print(correlations)
