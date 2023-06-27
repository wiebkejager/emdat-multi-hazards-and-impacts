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

# %% Load impact data
df = pd.read_csv(PROCESSED_IMPACT_EXP_AND_VUL_PATH_CSV).set_index("Dis No")
df = df.dropna(subset=["Population Count", "GDP per Capita PPP", "Affected Area"])

# %% Add column indicating eventtypes and count event types
eventtypes = ["multi-hazard", "single-hazard"]
df.loc[:, "eventtype"] = df[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: eventtypes[0] if sum(x.isna()) <= 1 else eventtypes[1], axis=1
)
# Add column indicating single-hazard or multi-hazard
df.loc[:, "eventtype_detailed"] = df[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: ",".join(sorted(list(x.dropna()))), axis=1
)

df.loc[:, "eventtype_detailed"].value_counts()

# %%
df.loc[:, "Population Density"] = (
    df.loc[:, "Population Count"] / df.loc[:, "Affected Area"]
)

df.loc[:, "Duration"] = (
    (
        pd.to_datetime(df.loc[:, "End Date"]) - pd.to_datetime(df.loc[:, "Start Date"])
    ).dt.total_seconds()
    / 60
    / 60
    / 24
)  # in days

# %%
# landslide_filter = df.loc[:, "Disaster Subtype"] != "Avalanche"
# df = df[landslide_filter]

# %%
vars = [
    "Total Affected",
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


# %% Correlations event types
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


# %% Correlations detailed event types
eventtypes_detailed = [
    "fl",
    "ew",
    "fl,ls",
    "eq",
    "ew,fl",
    "ls",
    "ew,fl,ls",
    "eq,ls",
]

correlations = pd.DataFrame(
    index=eventtypes_detailed,
    columns=vars[1 : len(vars)],
)

for eventtype in eventtypes_detailed:
    event_filter = df["eventtype_detailed"] == eventtype
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

# %%
