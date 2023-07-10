# %%
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
import statsmodels.api as sm
from scipy import stats


# %% Constants
PROCESSED_EMDAT_PATH = "C:/Users/wja209/DATA/PROCESSED/emdat_2000_2015.csv"
PROCESSED_IMPACT_EXP_AND_VUL_PATH_CSV = (
    "C:/Users/wja209/DATA/PROCESSED/impact_exposure_vulnerability_2000_2015_nogeom.csv"
)

# %%
df = pd.read_csv(PROCESSED_IMPACT_EXP_AND_VUL_PATH_CSV).set_index("Dis No")
# df = df.dropna(subset=["Population Count", "GDP per Capita PPP", "Affected Area"])

# %%
df.loc[:, "Duration"] = (
    (
        pd.to_datetime(df.loc[:, "End Date"]) - pd.to_datetime(df.loc[:, "Start Date"])
    ).dt.total_seconds()
    / 60
    / 60
    / 24
)  # in days

# %% Make Total Deaths more continuous
df["Total Deaths"] = df["Total Deaths"] + np.random.normal(0, 1, size=len(df))
df["Duration"] = df["Duration"] + np.random.normal(0, 1, size=len(df))


# %% Add column indicating single-hazard or multi-hazard
df.loc[:, "eventtype"] = df[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: "multi-hazard" if sum(x.isna()) <= 1 else "single-hazard", axis=1
)
# Add column indicating single-hazard or multi-hazard
df.loc[:, "eventtype_detailed"] = df[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: ",".join(sorted(list(x.dropna()))), axis=1
)

# Add column indicating single-hazard or multi-hazard
df.loc[:, "eventtype_detailed_unsrt"] = df[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: ",".join(list(x.dropna())), axis=1
)

# %%
event_counts = df.loc[:, "eventtype_detailed"].value_counts()
event_counts.to_csv("event_counts.csv", sep=";")

# %%
hazards = ["fl", "dr", "ew", "ls", "cw", "eq", "hw", "vo", "ts"]

for hazard in hazards:
    hazard1_filter = df.loc[:, "Hazard1"] == hazard
    df_hazard = df[hazard1_filter]
    order = sorted(df_hazard.loc[:, "eventtype_detailed_unsrt"].unique())
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    sns.countplot(
        x="eventtype_detailed_unsrt", data=df_hazard, ax=ax1, order=order
    ).set(xlabel=None)
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
    ax1.set_ylabel("Count of events")
    sns.boxplot(
        x="eventtype_detailed_unsrt",
        y="Total Affected",
        data=df_hazard,
        showfliers=False,
        ax=ax2,
        order=order,
    ).set(xlabel=None)
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)
    sns.boxplot(
        x="eventtype_detailed_unsrt",
        y="Total Deaths",
        data=df_hazard,
        showfliers=False,
        ax=ax3,
        order=order,
    ).set(xlabel=None)
    ax3.set_xticklabels(ax3.get_xticklabels(), rotation=90)
    fig.tight_layout()


# %%
hazard_groups = [
    ["fl", "ew", "ew,fl"],
    ["ew", "cw", "cw,ew"],
    ["dr", "hw", "dr,hw"],
]

for hazard_group in hazard_groups:
    hazard1_filter = df.loc[:, "eventtype_detailed"].isin(hazard_group)
    df_hazard = df[hazard1_filter]
    order = sorted(df_hazard.loc[:, "eventtype_detailed"].unique())
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 10))
    sns.countplot(
        x="eventtype_detailed", data=df_hazard, ax=ax1, order=hazard_group
    ).set(xlabel=None)
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
    ax1.set_ylabel("Count of events")
    sns.boxplot(
        x="eventtype_detailed",
        y="Total Affected",
        data=df_hazard,
        showfliers=False,
        ax=ax2,
        order=hazard_group,
    ).set(xlabel=None)
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)
    sns.boxplot(
        x="eventtype_detailed",
        y="Total Deaths",
        data=df_hazard,
        showfliers=False,
        ax=ax3,
        order=hazard_group,
    ).set(xlabel=None)
    ax3.set_xticklabels(ax3.get_xticklabels(), rotation=90)
    fig.tight_layout()


# %%
vars = [
    "Total Deaths",
    "Population Count",
    "GDP per Capita PPP",
    "Affected Area",
    "Duration",
]


# %% Pairplots
sns.pairplot(
    df.loc[
        :,
        vars,
    ],
    diag_kind="kde",
)

df_ranks = df.copy()
df_ranks.loc[:, vars] = (
    df_ranks.loc[:, vars].rank() / df_ranks.loc[:, vars].rank().max()
)
sns.pairplot(df_ranks.loc[:, vars], diag_kind="hist")

# %%

# %% Correlations event types
vars = [
    "Total Deaths",
    "Population Count",
    "GDP per Capita PPP",
    "Affected Area",
    "Duration",
]

correlations = pd.DataFrame(
    index=["fl", "ew", "ew,fl"],
    columns=vars[1 : len(vars)],
)

for hazard_group in ["fl", "ew", "ew,fl"]:
    event_filter = df["eventtype_detailed"] == hazard_group
    correlations.loc[hazard_group, "Sample size"] = sum(event_filter)
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
            correlations.loc[hazard_group, var] = np.round(corr[0], 2)

print(correlations)

# %%
